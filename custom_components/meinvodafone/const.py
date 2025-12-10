"""Constants for the meinvodafone integration."""

DOMAIN = "meinvodafone"
COORDINATOR = "meinvodafone_coordinator"
MEINVODAFONE_API = "meinvodafone_api"
MEINVODAFONE_API_POOL = "meinvodafone_api_pool"

DEFAULT_UPDATE_INTERVAL = 15
MAX_UPDATE_RETRY_COUNT = 2
REQUEST_TIMEOUT = 10

MINT_HOST = "https://www.vodafone.de/mint"
API_HOST = "https://www.vodafone.de/api"
API_V2_HOST = "https://api.vodafone.de/meinvodafone/v2/"

USER_AGENT = "MeinVodafone/14.3 (iPhone; iOS 17.4; Scale/3.00)"
CLIENT_ID = "ddbd0b14-2db1-11ec-a0b8-9457a55a403c-app"
HEADER_REFERER = "https://www.vodafone.de/meinvodafone/services/"

X_VF_CLIENT_ID = "MyVFWeb"

DATA_LISTENER = "data_listener"
CONTRACT = "contract"
CONTRACT_ID = "contract_id"
CONTRACT_USAGE = "contract_usage"

BILLING = "billing"
DATA = "data"
SMS = "sms"
MINUTES = "minutes"

NAME = "name"
LAST_UPDATE = "last_update"

REMAINING = "remaining"
TOTAL = "total"
USED = "used"

CURRENT_SUMMARY = "current_summary"
LAST_SUMMARY = "last_summary"
CYCLE_START = "cycle_start"
CYCLE_END = "cycle_end"
