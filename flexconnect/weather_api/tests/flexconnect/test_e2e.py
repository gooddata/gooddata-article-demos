# (C) 2024 GoodData Corporation
import orjson
import pyarrow.flight

#
# Few sample end-to-end tests which exercise the sample function by making
# Flight RPC calls. The tests also try, whether you can call the API, so
# make sure you have the API token readily in your environment.
#


def test_list_flexconnect_funs(testing_flexconnect_server):
    c = pyarrow.flight.FlightClient(testing_flexconnect_server.location)

    for flight_info in c.list_flights():
        function_descriptor = orjson.loads(flight_info.descriptor.command)

        assert function_descriptor["functionName"] == "WeatherAPIFlexConnect"


def test_function_call(testing_flexconnect_server, flexconnect_call_parameters):
    c = pyarrow.flight.FlightClient(testing_flexconnect_server.location)

    flight_info = c.get_flight_info(
        pyarrow.flight.FlightDescriptor.for_command(
            orjson.dumps(
                {
                    "functionName": "WeatherAPIFlexConnect",
                    "parameters": flexconnect_call_parameters,
                }
            )
        )
    )
    data: pyarrow.Table = c.do_get(flight_info.endpoints[0].ticket).read_all()

    assert data.num_rows == 192 # Max response size for the API without trimming.
    assert data.num_columns == 4
