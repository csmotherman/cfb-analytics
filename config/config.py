from pathlib import Path
import os

from dotenv import load_dotenv
import cfbd

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

API_KEY = os.getenv("CFBD_API_KEY")

# ============================================================
# CFBD API CONFIGURATION
# ============================================================

configuration = cfbd.Configuration(
    access_token=API_KEY
)

client = cfbd.ApiClient(configuration)

games_api = cfbd.GamesApi(client)
plays_api = cfbd.PlaysApi(client)
drives_api = cfbd.DrivesApi(client)

# ============================================================
# PROJECT DIRECTORIES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

RAW_DIR = DATA_DIR / "raw"

CLEAN_DIR = DATA_DIR / "cleaned"

FEATURE_DIR = DATA_DIR / "features"

OUTPUT_DIR = PROJECT_ROOT / "output"

# ============================================================
# DOWNLOAD SETTINGS
# ============================================================

SEASON_TYPE = "regular"

FBS_ONLY = True

SAVE_FORMAT = "parquet"

REQUEST_DELAY = 1

MAX_RETRIES = 5