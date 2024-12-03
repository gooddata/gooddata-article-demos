# (C) 2024 GoodData Corporation
import os
import pickle
from datetime import datetime, timedelta
from typing import Optional

import gooddata_flight_server as gf
import pandas as pd
import pyarrow
import requests
import structlog
from gooddata_flexconnect import (
    ExecutionContext,
    ExecutionType,
    FlexConnectFunction,
    LabelElementsExecutionRequest,
)
from gooddata_sdk import (
    AbsoluteDateFilter,
    Filter,
    NegativeAttributeFilter,
    PositiveAttributeFilter,
    RelativeDateFilter,
)

_LOGGER = structlog.get_logger("machine_learning_flexconnect")

FORECAST_URL = "https://api.weatherapi.com/v1/forecast.json"

class MachineLearningFlexConnect(FlexConnectFunction):
    """FlexConnectFunction implementation for machine learning revenue prediction.
    This class predicts revenue based on date and weather data using a pre-trained
    machine learning model. It retrieves weather forecasts for the specified dates
    and location, prepares the features, and then uses the model to predict revenue.

    Attributes:
        Name (str): The name of the FlexConnectFunction.
        Schema (dict): The output schema for the function.
        model: The pre-trained machine learning model used for predictions.
        API_KEY (str): API key for accessing the weather API.
    """
    Name = "MachineLearningFlexConnect"
    Schema = {
        "date": pyarrow.date32(),
        "predicted_revenue": pyarrow.float64(),
    }

    model = None
    API_KEY = None

    def _handle_date(self, context: ExecutionContext) -> list[datetime]:
        """Extracts a list of dates from the execution context filters.

        If date filters are provided in the execution context, it processes them to generate
        a list of dates to predict for. If no date filters are provided, it defaults to
        predicting for the next 7 days.

        Args:
            context (ExecutionContext): The execution context containing report execution request and filters.

        Returns:
            list[datetime]: A list of datetime objects representing the dates to predict for.
        """
        now = datetime.now()
        date_list = []

        for date_filter in context.report_execution_request.filters:
            if isinstance(date_filter, AbsoluteDateFilter):
                from_date = datetime.fromisoformat(date_filter.from_date)
                to_date = datetime.fromisoformat(date_filter.to_date)
                delta = (to_date - from_date).days + 1
                date_list = [from_date + timedelta(days=i) for i in range(delta)]
                return date_list
            elif isinstance(date_filter, RelativeDateFilter):
                if date_filter.granularity == "DAY":
                    from_date = now + timedelta(days=date_filter.from_shift)
                    to_date = now + timedelta(days=date_filter.to_shift)
                    delta = (to_date - from_date).days + 1
                    date_list = [from_date + timedelta(days=i) for i in range(delta)]
                    return date_list
                # Handle other granularities if needed
        # Default to next 7 days if no date filter is provided
        from_date = now
        to_date = now + timedelta(days=6)
        delta = (to_date - from_date).days + 1
        date_list = [from_date + timedelta(days=i) for i in range(delta)]
        return date_list

    def _extract_location(self, execution_context: ExecutionContext) -> str:
        """Extracts the location from the execution context filters.

        It looks for a PositiveAttributeFilter with label_identifier 'customer_city' to determine
        the location. If not found, defaults to 'San Francisco'.

        Args:
            execution_context (ExecutionContext): The execution context containing filters.

        Returns:
            str: The location extracted from the filters or the default location.
        """
        # Default location
        location = "San Francisco"
        for filter in execution_context.filters:
            if (
                isinstance(filter, PositiveAttributeFilter)
                and filter.label_identifier == "customer_city"
            ):
                location = filter.values[0]
                break  # Assuming we take the first matching filter
        return location

    def _get_weather_data(self, dates: list[datetime], location: str) -> dict[str, list[any]]:
        """Retrieves weather data for the given dates and location.

        Fetches weather forecast data from the weather API for the specified future dates
        and location. The weather data includes average temperature and daily chance of rain.

        Args:
            dates (list[datetime]): List of datetime objects for which to fetch weather data.
            location (str): Location for which to fetch weather data.

        Returns:
            dict[str, list[any]]: A dictionary containing weather data with keys 'Date', 'Temperature', and 'Rain'.
        """
        output = {
            'Date': [],
            'Temperature': [],
            'Rain': [],
        }
        headers = {
            'Content-Type': 'application/json'
        }
        future_dates = [date for date in dates if date.date() >= datetime.now().date()]
        # Fetch forecast data for future dates only
        if future_dates:
            # Weather API allows up to 10 days of forecast data
            days_ahead = (max(future_dates).date() - datetime.now().date()).days + 1
            params = {
                'key': self.API_KEY,
                'q': location,
                'days': min(days_ahead, 10),
            }
            try:
                response = requests.get(FORECAST_URL, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                if 'forecast' in data:
                    for day in data.get("forecast", {}).get("forecastday", []):
                        date_str = day['date']
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                        if date in future_dates:
                            day_data = day['day']
                            output['Date'].append(date)
                            output['Temperature'].append(day_data['avgtemp_c'])
                            output['Rain'].append(day_data['daily_chance_of_rain'])
                else:
                    _LOGGER.warning("No forecast data available.")
            except requests.HTTPError as http_err:
                _LOGGER.error(f"HTTP error occurred while fetching forecast data: {http_err}")
            except Exception as err:
                _LOGGER.error(f"An error occurred while fetching forecast data: {err}")
        return output

    def _prepare_features(
        self, date_list: list[datetime], weather_data: dict[str, list[any]]
    ) -> dict[str, list[any]]:
        """Prepares input features for the model based on the date list and weather data.

        Constructs a feature set that includes day of the week, month, temperature, and rain probability.
        Aligns weather data with the date list and handles any missing weather data.

        Args:
            date_list (list[datetime]): List of dates for which to prepare features.
            weather_data (dict[str, list[any]]): Weather data corresponding to the dates.

        Returns:
            dict[str, list[any]]: A dictionary of input features for the model.
        """
        # Align weather data with date_list
        weather_df = {
            date: {'temperature': temp, 'rain': rain}
            for date, temp, rain in zip(
                weather_data['Date'], weather_data['Temperature'], weather_data['Rain']
            )
        }
        input_features = {
            'day_of_week': [],
            'month': [],
            'temperature': [],
            'rain': [],
            # Add other features as needed
        }
        for date in date_list:
            input_features['day_of_week'].append(date.weekday())
            input_features['month'].append(date.month)
            weather_info = weather_df.get(date)
            if weather_info:
                input_features['temperature'].append(weather_info['temperature'])
                input_features['rain'].append(weather_info['rain'])
            else:
                # Handle missing weather data
                input_features['temperature'].append(None)
                input_features['rain'].append(None)

        return input_features

    def call(
        self,
        parameters: dict,
        columns: Optional[tuple[str, ...]],
        headers: dict[str, list[str]],
    ) -> gf.ArrowData:
        """Executes the FlexConnectFunction to predict revenue.

        This method is called when the function is invoked. It processes the execution context,
        handles date and location extraction, retrieves weather data, prepares features,
        and uses the model to make predictions. Returns the results as an Arrow table.

        Args:
            parameters (dict): Dictionary of parameters including the execution context.
            columns (Optional[tuple[str, ...]]): Tuple of requested column names.
            headers (dict[str, list[str]]): Headers from the request.

        Returns:
            gf.ArrowData: An Arrow table containing the prediction results.

        Raises:
            ValueError: If no execution context is provided or insufficient data for prediction.
        """
        execution_context = ExecutionContext.from_parameters(parameters)
        if execution_context is None:
            raise ValueError("Function did not receive execution context.")
        _LOGGER.info("execution_context", context=execution_context)

        date_list = self._handle_date(execution_context)
        location = self._extract_location(execution_context)
        weather_data = self._get_weather_data(date_list, location)
        input_features = self._prepare_features(date_list, weather_data)

        # Drop entries with missing data
        feature_df = pd.DataFrame(input_features)
        feature_df.dropna(inplace=True)

        if feature_df.empty:
            _LOGGER.error("No data available after removing entries with missing features.")
            raise ValueError("Insufficient data for prediction.")

        # Update date_list to match the cleaned data
        date_list = [date_list[i] for i in feature_df.index]
        input_features = feature_df.to_dict(orient='list')

        predictions = self.model.predict(input_features)

        output = {
            "date": [date.date() for date in date_list],
            "predicted_revenue": predictions.tolist(),
        }

        _LOGGER.info("Output", output=output)

        return pyarrow.Table.from_pydict(output)

    @staticmethod
    def on_load(ctx: gf.ServerContext) -> None:
        """Loads the machine learning model and API key when the function is loaded.

        This method is called once when the server starts. It loads the pre-trained machine
        learning model from a pickle file and retrieves the weather API key from environment variables.

        The model is loaded in on_load, to reduce the response time, as it may not be instantaneous.

        Args:
            ctx (gf.ServerContext): The server context.

        Returns:
            None
        """
        with open('revenue_model.pkl', 'rb') as model_file:
            MachineLearningFlexConnect.model = pickle.load(model_file)
        _LOGGER.info("Model loaded successfully")
        MachineLearningFlexConnect.API_KEY = os.getenv("WEATHER_API_KEY")
