import os

def _int_env(name, default):
    val = os.getenv(name)
    return int(val) if val is not None else default

def _float_env(name, default):
    val = os.getenv(name)
    return float(val) if val is not None else default

class Config:
    # GCP
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    GCP_REGION = os.getenv("GCP_REGION", "us-central1")
    BUCKET_NAME = os.getenv("BUCKET_NAME")

    # Generator params
    GENERATOR_NUM_EVENTS = _int_env("GENERATOR_NUM_EVENTS", 10000)
    GENERATOR_BATCH_SIZE = _int_env("GENERATOR_BATCH_SIZE", 5000)
    GENERATOR_UNIQUE_USERS = _int_env("GENERATOR_UNIQUE_USERS", 500)
    GENERATOR_UNIQUE_PAGES = _int_env("GENERATOR_UNIQUE_PAGES", 50)
    GENERATOR_UNIQUE_PRODUCTS = _int_env("GENERATOR_UNIQUE_PRODUCTS", 1000)
    GENERATOR_SESSION_TIMEOUT_MINUTES = _int_env("GENERATOR_SESSION_TIMEOUT_MINUTES", 30)

    # Event distribution (fractions or percentages)
    # Default: 60% pageview, 20% click, 10% addto cart, 10% purchase
    GENERATOR_P_PAGEVIEW = _float_env("GENERATOR_P_PAGEVIEW", 0.6)
    GENERATOR_P_CLICK = _float_env("GENERATOR_P_CLICK", 0.2)
    GENERATOR_P_ADD_TO_CART = _float_env("GENERATOR_P_ADD_TO_CART", 0.1)
    GENERATOR_P_PURCHASE = _float_env("GENERATOR_P_PURCHASE", 0.1)

    # Other
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    # Prefix where data will be stored in bucket
    GCS_PATH_PREFIX = os.getenv("GCS_PATH_PREFIX", "raw/clickstream")
