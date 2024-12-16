from influxdb_client_3 import InfluxDBClient3

from .constants import *


def get_influx_client() -> InfluxDBClient3:

    return InfluxDBClient3(
        host=INFLUXDB_HOST, token=os.environ.get("INFLUXDB_TOKEN"), org=INFLUXDB_ORG
    )
