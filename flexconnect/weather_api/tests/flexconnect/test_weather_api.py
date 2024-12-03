# (C) 2024 GoodData Corporation
from flexconnect.weather_api import WeatherFunction


def test_sample_function1(flexconnect_call_parameters):
    fun = WeatherFunction.create()
    result = fun.call(flexconnect_call_parameters, None, {})

    assert result is not None
