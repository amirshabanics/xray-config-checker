import prometheus_client
import os

"""
network: MCI, IRANCIL, Zitel, ...
config_name: the name of your config
"""
PROMETHEUS_PORT = os.getenv("PROMETHEUS_PORT")
CONFIG_STATUS_GAUGE = prometheus_client.Gauge(
    "config_status", "Config status indicator.", ["network", "config_name"]
)


def setup() -> None:
    prometheus_client.start_http_server(int(PROMETHEUS_PORT))
