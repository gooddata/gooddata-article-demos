# (C) 2024 GoodData Corporation
import calendar
import os
from datetime import datetime, timedelta
from typing import Any, Optional

import gooddata_flight_server as gf
import pyarrow
import requests
import structlog
from dateutil.relativedelta import relativedelta
from gooddata_flexconnect import (
    ExecutionContext,
    ExecutionType,
    FlexConnectFunction,
)
from gooddata_flight_server.tasks.base import ArrowData
from gooddata_sdk import (
    AbsoluteDateFilter,
    Filter,
    NegativeAttributeFilter,
    PositiveAttributeFilter,
    RelativeDateFilter,
)

_LOGGER = structlog.get_logger("weatherapi_function")

HISTORICAL_URL = "https://api.weatherapi.com/v1/history.json"
FORECAST_URL = "https://api.weatherapi.com/v1/forecast.json"

class WeatherFunction(FlexConnectFunction):
    Name = "WeatherAPIFlexConnect"
    Schema = pyarrow.schema(
        [
            pyarrow.field("date", pyarrow.date32()),
            pyarrow.field("Source", pyarrow.string()),
            pyarrow.field("Temperature", pyarrow.float64()),
            pyarrow.field("Rain", pyarrow.int32()),
        ]
    )

    def _handle_date(self, context: Optional[ExecutionContext]) -> tuple[str, str]:
        """Extract the from_date and to_date from the execution context filters."""

        now = datetime.now()
        for date_filter in context.filters:
            if isinstance(date_filter, AbsoluteDateFilter):
                return date_filter.from_date, date_filter.to_date
            elif isinstance(date_filter, RelativeDateFilter):
                if date_filter.granularity == "DAY":
                    from_date = (now + timedelta(days=date_filter.from_shift - 1)).date()
                    to_date = (now + timedelta(days=date_filter.to_shift)).date()
                    if date_filter.to_shift == 0:
                        to_date = now.date()
                elif date_filter.granularity == "WEEK":
                    # Align to the beginning of the from_week and the end of the to_week
                    current_week_start = now - timedelta(days=now.weekday())
                    from_date = current_week_start + timedelta(weeks=date_filter.from_shift)
                    to_date = current_week_start + timedelta(weeks=date_filter.to_shift + 1) - timedelta(seconds=1)
                    if date_filter.to_shift == 0:
                        # Align to the end of the current week (Sunday)
                        to_date = current_week_start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
                elif date_filter.granularity == "MONTH":
                    # Align to the beginning of the from_month and the end of the to_month
                    from_date = (now + relativedelta(months=date_filter.from_shift)).replace(
                        day=1, hour=0, minute=0, second=0, microsecond=0
                    )
                    to_date = now + relativedelta(months=date_filter.to_shift + 1)
                    to_date = to_date.replace(
                        day=1, hour=0, minute=0, second=0, microsecond=0
                    ) - timedelta(microseconds=1)
                    if date_filter.to_shift == 0:
                        to_date = now.replace(
                            day=calendar.monthrange(now.year, now.month)[1],
                            hour=23,
                            minute=59,
                            second=59,
                            microsecond=999999,
                        )
                elif date_filter.granularity == "YEAR":
                    # Align to the beginning of the from_year and the end of the to_year
                    from_date = now.replace(
                        year=now.year - date_filter.from_shift, month=1, day=1, hour=0, minute=0, second=0, microsecond=0
                    )
                    to_date = now.replace(
                        year=now.year - date_filter.to_shift + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0
                    ) - timedelta(microseconds=1)
                    if date_filter.to_shift == 0:
                        to_date = now.replace(
                            month=12, day=31, hour=23, minute=59, second=59, microsecond=999999
                        )
                else:
                    continue
                return from_date.isoformat(), to_date.isoformat()
        # Default to last week + 1 day ahead if no date filter is provided
        from_date = (now - timedelta(days=7)).date().isoformat()
        to_date = (now + timedelta(days=1)).date().isoformat()
        return from_date, to_date

    def _extract_location(self, execution_context: ExecutionContext) -> str:
        """Extract the location from the execution context filters."""
        # Default location
        location = "San Francisco"
        for filter in execution_context.report_execution_request.filters:
            if (
                isinstance(filter, PositiveAttributeFilter)
                and filter.label_identifier == "customer_city"
            ):
                location = filter.values[0]
                break  # Assuming we take the first matching filter
        return location

    def _get_historical_data(self, fromdate: str, todate: str, location: str) -> dict[str, Any]:
        """Retrieve and process historical weather data."""
        clamped_time = min(datetime.now(), datetime.fromisoformat(todate)).date().isoformat()
        params = {
            "key": WeatherFunction.ApiKey,
            "q": location,
            "dt": fromdate,
            "end_dt": clamped_time
        }
        response = requests.get(HISTORICAL_URL, params=params)
        response.raise_for_status()
        data = response.json()
        output = {
            "Date": [],
            "Source": [],
            "Temperature": [],
            "Rain": []
        }
        for day in data.get("forecast", {}).get("forecastday", []):
            for hour in day.get("hour", []):
                output["Date"].append(datetime.fromtimestamp(hour["time_epoch"]))
                output["Source"].append("Observation")
                output["Temperature"].append(hour["temp_c"])
                output["Rain"].append(hour["chance_of_rain"])
        return output

    def _get_forecast_data(self, days: int, location: str) -> dict[str, Any]:
        """Retrieve and process forecast weather data."""
        days = min(days, 3)  # Forecast for free plans is up to 3 days
        if days <= 0:
            return {
                "Date": [],
                "Source": [],
                "Temperature": [],
                "Rain": []
            }
        params = {
            "key": WeatherFunction.ApiKey,
            "q": location,
            "days": days,
            "aqi": "no",
            "alerts": "no"
        }
        response = requests.get(FORECAST_URL, params=params)
        response.raise_for_status()
        data = response.json()
        output = {
            "Date": [],
            "Source": [],
            "Temperature": [],
            "Rain": []
        }
        for day in data.get("forecast", {}).get("forecastday", []):
            for hour in day.get("hour", []):
                output["Date"].append(datetime.fromtimestamp(hour["time_epoch"]))
                output["Source"].append("Forecast")
                output["Temperature"].append(hour["temp_c"])
                output["Rain"].append(hour["chance_of_rain"])
        return output

    def call(
        self,
        parameters: dict,
        columns: Optional[tuple[str, ...]],
        headers: dict[str, list[str]],
    ) -> ArrowData:
        execution_context = ExecutionContext.from_parameters(parameters)
        if execution_context is None:
            # This can happen for invalid invocations that do not come from GoodData
            raise ValueError("Function did not receive execution context.")
        _LOGGER.info("execution_context", context=execution_context)

        # Check, for label elements. This happens e.g., when you filter and want to know what can be filtered.
        if execution_context.execution_type == ExecutionType.LABEL_ELEMENTS:
            # Filtered to one of our columns.
            if execution_context.attributes[0] == "Source":
                output = {
                    "Source": ["Observation", "Forecast"],
                }
            else:
                # Didn't match our columns, no need to return anything, so we return empty table.
                output = {}
            return pyarrow.table(output)

        fromdate, todate = self._handle_date(execution_context)
        location = self._extract_location(execution_context)

        historical_data = self._get_historical_data(fromdate, todate, location)

        days_difference = (datetime.fromisoformat(todate) - datetime.now()).days
        forecast_data = self._get_forecast_data(days_difference, location)

        # Merge historical and forecast data
        output = {
            "Date": historical_data["Date"] + forecast_data["Date"],
            "Source": historical_data["Source"] + forecast_data["Source"],
            "Temperature": historical_data["Temperature"] + forecast_data["Temperature"],
            "Rain": historical_data["Rain"] + forecast_data["Rain"],
        }

        _LOGGER.info("Output", output=output)

        return pyarrow.table(output)

    @staticmethod
    def on_load(ctx: gf.ServerContext) -> None:
        WeatherFunction.ApiKey = os.getenv("WEATHER_API_KEY")
