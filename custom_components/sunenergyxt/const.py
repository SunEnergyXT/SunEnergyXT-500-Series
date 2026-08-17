"""
Constants for SunEnergyXT 500 Series integration.

This module defines constant values used throughout the SunEnergyXT integration.

Constants:
- DOMAIN: The integration domain name
- HOST_PREFIX: Prefix for SunEnergyXT device hostnames
- HOST_SUFFIX: Suffix for SunEnergyXT device hostnames
"""

DOMAIN = "sunenergyxt"
HOST_PREFIX = "SunEnergyXT_AIO_"
HOST_SUFFIX = ".local"
CONF_POLLING_INTERVAL = "polling_interval"
DEFAULT_POLLING_INTERVAL = 3
MIN_POLLING_INTERVAL = 3
MAX_POLLING_INTERVAL = 60
