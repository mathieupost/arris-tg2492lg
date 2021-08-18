__version__ = "2.0.0"

from datetime import timedelta


USERNAME = "admin"
TOKEN_EXPIRATION = timedelta(minutes=5)

# For an overview of all Arris OIDs see: https://mibs.observium.org/mib/ARRIS-ROUTER-DEVICE-MIB/#
ARRIS_ROUTER_MIB = "1.3.6.1.4.1.4115.1.20.1"

# Router information
MAC_ADDRESS_OID = ARRIS_ROUTER_MIB + ".1.1.13.0"
SERIAL_NUMBER_OID = ARRIS_ROUTER_MIB + ".1.5.8.0"
HARDWARE_VERSION_OID = ARRIS_ROUTER_MIB + ".1.5.10.0"
SOFTWARE_VERSION_OID = ARRIS_ROUTER_MIB + ".1.5.11.0"

# Client information
CLIENT_HOST_NAME_OID = ARRIS_ROUTER_MIB + ".1.2.4.2.1.3"
CLIENT_MAC_OID = ARRIS_ROUTER_MIB + ".1.2.4.2.1.4"
CLIENT_ADAPTER_TYPE_OID = ARRIS_ROUTER_MIB + ".1.2.4.2.1.6"
CLIENT_TYPE_OID = ARRIS_ROUTER_MIB + ".1.2.4.2.1.7"
CLIENT_LEASE_END_OID = ARRIS_ROUTER_MIB + ".1.2.4.2.1.9"
CLIENT_ROW_STATUS_OID = ARRIS_ROUTER_MIB + ".1.2.4.2.1.13"
CLIENT_ONLINE_OID = ARRIS_ROUTER_MIB + ".1.2.4.2.1.14"
CLIENT_COMMENT_OID = ARRIS_ROUTER_MIB + ".1.2.4.2.1.15"
CLIENT_DEVICE_NAME_OID = ARRIS_ROUTER_MIB + ".1.2.4.2.1.20"
