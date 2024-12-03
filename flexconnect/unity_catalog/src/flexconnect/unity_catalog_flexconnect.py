# (C) 2024 GoodData Corporation
import os
from typing import Optional

import polars as pl
import pyarrow
import structlog
from databricks import sql
from databricks.sdk import WorkspaceClient
from gooddata_flexconnect import (
    ExecutionContext,
    FlexConnectFunction,
)
from gooddata_flight_server import ServerContext
from gooddata_flight_server.tasks.base import ArrowData

_LOGGER = structlog.get_logger("unitycatalog_function")

TOKEN = os.environ.get("TOKEN")
HOST = os.environ.get("HOST")
HTTP_PATH = os.environ.get("HTTP_PATH")
TABLE_NAME = os.environ.get("TABLE_NAME")


class UnityCatalogsFunction(FlexConnectFunction):
    """A FlexFun implementation for retrieving data from Unity Catalog.

    This class interacts with Databricks' Unity Catalog to fetch table data
    and make it available in a format compatible with GoodData.

    Attributes:
        Name (str): The name of the table in GoodData.
        type_mappings (dict): Mapping of data types from Databricks to PyArrow.
        Schema (pyarrow.Schema): The schema of the table.
    """

    Name = "Name of the Table in GoodData"
    type_mappings = {
            'STRING': pyarrow.string(),
            'INT': pyarrow.int32(),
            'INTEGER': pyarrow.int32(),
            'BIGINT': pyarrow.int64(),
            'FLOAT': pyarrow.float32(),
            'DOUBLE': pyarrow.float64(),
            'BOOLEAN': pyarrow.bool_(),
            'TIMESTAMP': pyarrow.timestamp('ms'),
            'DATE': pyarrow.date32(),
        }
    Schema = {}

    def __init__(self):
        """Initializes the UnityCatalogsFunction by setting up the table schema.

        Connects to the Databricks workspace and retrieves the table schema,
        mapping Databricks data types to PyArrow data types.
        """
        w = WorkspaceClient(host=HOST,token=TOKEN)

        table = w.tables.get(TABLE_NAME)

        # Extract column information
        columns = table.columns

        fields = []
        for col in columns:
            name = col.name
            data_type = col.type_text.upper()  # Get the data type as a string and convert to uppercase
            nullable = col.nullable if hasattr(col, 'nullable') else True  # Default to True if nullable info is missing

            if data_type in self.type_mappings:
                arrow_type = self.type_mappings[data_type]
            else:
                raise TypeError(f"Unsupported data type: {data_type}")

            fields.append(pyarrow.field(name, arrow_type, nullable=nullable))

        self.Schema = pyarrow.schema(fields)


    def call(
        self,
        parameters: dict,
        columns: Optional[tuple[str, ...]],
        headers: dict[str, list[str]],
    ) -> ArrowData:
        """Fetches data from the specified table and returns it in Arrow format.

        Args:
            parameters (dict): Parameters passed to the function, including execution context.
            columns (Optional[tuple[str, ...]]): Specific columns to fetch. Fetches all if None.
            headers (dict[str, list[str]]): HTTP headers from the request.

        Returns:
            ArrowData: The data fetched from the table in Arrow format.

        Raises:
            ValueError: If the execution context is invalid.
        """
        execution_context = ExecutionContext.from_parameters(parameters)
        if execution_context is None:
            # This can happen for invalid invocations that do not come from GoodData
            raise ValueError("Function did not receive execution context.")
        _LOGGER.info("execution_context", context=execution_context)

        connection = sql.connect(
            server_hostname=HOST,
            http_path=HTTP_PATH,
            access_token=TOKEN
        )
        # Optimization, so we ask only for the necessary columns.
        columns_str = ', '.join(columns) if columns else '*'
        query = f"SELECT {columns_str} FROM {TABLE_NAME}"

        cursor = connection.cursor()
        cursor.execute(query)
        # Fetch the data and column names
        data = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        pl_df = pl.DataFrame(data, schema=column_names, orient="row")
        _LOGGER.info("pl_df", table=pl_df.to_arrow())
        return pl_df.to_arrow()


    @staticmethod
    def on_load(ctx: ServerContext) -> None:
        pass
