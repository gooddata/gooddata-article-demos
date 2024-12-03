# (C) 2024 GoodData Corporation
import logging
import os
import pathlib
from datetime import datetime

import orjson
import pyarrow
import pyarrow.parquet as pq

from kafka import KafkaConsumer

log_handler = logging.StreamHandler()
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))

GOAL_DIR = pathlib.Path("/tmp/data/kafka")
GOAL_DIR.mkdir(parents=True, exist_ok=True)

SCHEMA = pyarrow.schema(
    [
        pyarrow.field("transaction_id", pyarrow.string()),
        pyarrow.field("account_id", pyarrow.string()),
        pyarrow.field("amount", pyarrow.float64()),
        pyarrow.field("currency", pyarrow.string()),
        pyarrow.field("timestamp", pyarrow.timestamp("us")),
        pyarrow.field("transaction_type", pyarrow.string()),
    ]
)


def store_data(data: list[dict], batch: int) -> None:
    path = GOAL_DIR / f"data_{batch}.parquet"
    table = pyarrow.Table.from_pylist(data, schema=SCHEMA)
    pq.write_table(table, path)


def main():
    consumer = KafkaConsumer(
        "test",
        bootstrap_servers="kafka:9092",
        value_deserializer=lambda x: orjson.loads(x),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )

    results = []
    threshold = 10_000
    batch = 0
    for msg in consumer:
        logger.info(f"{msg.value=}")
        converted_value = {
            "transaction_id": msg.value.get("transaction_id"),
            "account_id": msg.value.get("account_id"),
            "amount": float(msg.value.get("amount")),
            "currency": msg.value.get("currency"),
            "timestamp": datetime.strptime(
                msg.value.get("timestamp"), "%Y-%m-%dT%H:%M:%S.%f"
            ),
            "transaction_type": msg.value.get("transaction_type"),
        }
        results.append(converted_value)
        if len(results) == threshold:
            store_data(results, batch)
            batch += 1
            results = []


if __name__ == "__main__":
    main()
