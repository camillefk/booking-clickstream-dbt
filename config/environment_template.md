# Environment Configuration Guide

## Overview

This project requires environment variables for secure configuration. This guide helps you set them up.

### Why Environment Variables?

- ✓ **Security**: Credentials never in code
- ✓ **Flexibility:** Change config without code changes
- ✓ **Portability**: Same code runs in dev/prod (just different vars)
- ✓ **Best Practice**: Industry standard (12-factor app)

---

## 1. Quick Setup (5 minutes)

### Step 1: Create `.env` file (NEVER COMMIT!)

Create your `.env` file based on the `.env.example` template.
> *Make sure `.env` is included in your `.gitignore` file.*

### Step 2: Configure Environment Variables

Replace all `{YOUR_VALUE}` placeholders with actual values from your GCP project.

### Step 3: Load into Shell

```bash
source .env
# Now all variables are available to Python/dbt/Airflow
```

---

## 2. Environment Variables References

### 2.1 GCP Configuration (REQUIRED)

```bash
# GCP Project Configuration
# =========================

# Your main GCP project ID (sandbox project)
# Find it: Go to GCP Console → Select Project → Note the ID 
GCP_PROJECT_ID="{YOUR_SANDBOX_PROJECT_ID}"

# Example: GCP_PROJECT_ID="my-sandbox-project-12345-v1"

# GCP Region (where BigQuery and GCS are located)
# Options: us-central1, europe-west1 (Amsterdam), europe-west4 (Netherlands)
GCP_REGION="europe-west1"

# Example: GCP_REGION="europe-west1"

# For authentication (see docs/GCP_AUTHENTICATION.md)
# Leave empty if using gcloud auth application-default login
# Only set if you have a service account JSON (not recommended)
GOOGLE_APPLICATION_CREDENTIALS=""
```

---

### 2.2 Google Cloud Storage (Data Lake)

```bash
# GCP Bucket Configuration
# ========================

# Bucket name for RAW clickstream events
# Must be GLOBALLY unique (GCS requires this)
# Naming convention: {project-id}-clickstream-raw
# Example: my-sandbox-project-12345-v1-clickstream-raw
GCS_BUCKET_NAME="{YOUR_PROJECT_ID}-clickstream-raw"

# GCS Path prefix for data (you can have multiple datasets in same bucket)
# This organizes data: gs://{bucket}/raw/clickstream/...
GCS_DATA_PATH="raw/clickstream"

# Example full path: gs://my-project-clickstream-raw/raw/clickstream/2026-05-29/
```

**Why?**
- GCS is cheap (first 5GB free), perfect for raw data
- Bucket name must be unique globally (avoids conflicts)
- Path prefix keeps data organized

---

### 2.3 BigQuery Datasets

```bash
# BigQuery Dataset Names
# ======================

# RAW Layer: Events loaded directly from GCS
# No transformations yet, just typed
BIGQUERY_DATASET_RAW="clickstream_raw"

# STAGING Layer: Cleaned, deduplicated data
# Still denormalized, used by dbt
BIGQUERY_DATASET_STAGING="clickstream_staging"

# ANALYTICS Layer: Star Schema with facts & dimensions
# Final, analysis-ready data
BIGQUERY_DATASET_ABALYTICS="clickstream_analytics"

# Example: Your bigquery will have 3 datasets with these names
# each with tables inside
```

**Why?**
- **Raw:** Audit trail (can always regenerate from this)
- **Staging:** Working area (may change frequently)
- **Analytics:** Sacred (this is what analysts use)

---

### 2.4 dbt Configuration

```bash
# dbt Project Setup
# =================

# dbt Target/Profile: which environment are we running?
# Options: dev (local testing), prod (production)
DBT_TARGET="dev"

# dbt Profiles Directory (where dbt looks for credentials)
# Default: ~/.dbt (home directory)
# Can override if needed
DBT_PROFILES_DIR="$HOME/.dbt"

# dbt Threads (parallel execution)
# Higher = faster, but more GCP quota usage
# Safe default: 4
DBT_THREADS="4"

# dbt Logging Level
# Options: debug, info, warning
DBT_LOG_LEVEL="info"

# Example:
# DBT_TARGET="dev" means we're using "dev" profile in profiles.yml
# dbt will read credentials from $HOME/.dbt/profiles.yml
```

**Why?**
- `DBT_TARGET` lets us switch dev ↔ prod with one variable
- `DBT_THREADS` affects speed (dev can be slower to save quota)
- Logging helps debug issues

---

### 2.5 Airflow Configuration

```bash
# Apache Airflow Setup
# ====================

# Airflow Home directory (where DAGs, logs, config live)
# If using docker-compose, set to /home/airflow
# If local, set to ~/airflow
AIRFLOW_HOME="{PATH_TO_AIRFLOW_HOME}"

# Example: AIRFLOW_HOME="/home/airflow" (Docker) or "~/airflow" (local)

# Airflow Database URL (stores DAG history, task state)
# SQLite for local: sqlite:////home/airflow/airflow.db
# PostgreSQL for prod: postgresql://user:password@localhost:5432/airflow
AIRFLOW_DATABASE_URL="sqlite:////{AIRFLOW_HOME}/airflow.db"

# Example: AIRFLOW_DATABASE_URL="sqlite:////home/airflow/airflow.db"

# Executor (how Airflow runs tasks)
# Options: SequentialExecutor (one at a time, for local), CeleryExecutor (parallel)
# For portfolio: SequentialExecutor is fine
AIRFLOW_EXECUTOR="SequentialExecutor"

# Airflow User (for webUI login)
AIRFLOW_USERNAME="admin"

# Airflow Password (for webUI login, change in production!)
AIRFLOW_PASSWORD="airflow"  # Change this in production!

# Email for alerts (when DAGs fail)
AIRFLOW_EMAIL="seu.email@example.com"

# Example: AIRFLOW_EMAIL="camille@example.com"
```

**Why?**
- `AIRFLOW_HOME` tells Airflow where to find its config
- `AIRFLOW_EXECUTOR` determines how parallel tasks run
- Database URL is where Airflow stores state

---

### 2.6 Data Generator Configuration

```bash
# Data Generator Settings
# =======================

# How many events to generate per day
# For local testing: 1000-10000 (fast)
# For realistic data: 100000+ (slow, uses quota)
GENERATOR_DAILY_EVENTS="10000"

# Number of unique users to simulate
GENERATOR_UNIQUE_USERS="500"

# Number of unique pages on the site
GENERATOR_UNIQUE_PAGES="50"

# Number of unique products
GENERATOR_UNIQUE_PRODUCTS="1000"

# Session timeout in minutes
# (after how long of inactivity does a session end?)
GENERATOR_SESSION_TIMEOUT_MINUTES="30"

# Event distribution (must sum to 100)
# pageview: user lands on page
# click: user clicks on something
# add_to_cart: user adds product to cart
# purchase: user completes purchase
GENERATOR_EVENT_DISTRIBUTION_PAGEVIEW="60"
GENERATOR_EVENT_DISTRIBUTION_CLICK="25"
GENERATOR_EVENT_DISTRIBUTION_ADD_TO_CART="10"
GENERATOR_EVENT_DISTRIBUTION_PURCHASE="5"

# Conversion rate (what % of sessions result in purchase?)
GENERATOR_CONVERSION_RATE="5"

# Example:
# GENERATOR_DAILY_EVENTS="10000" = generate 10K events per run
# GENERATOR_EVENT_DISTRIBUTION_PAGEVIEW="60" = 60% of events are pageviews
```

**Why?**
- These let you tune how realistic the data is
- For testing: use low numbers (fast)
- For demos: use high numbers (realistic)

---

### 2.7 Docker Configuration

```bash
# Docker Compose Settings
# =======================

# Docker Compose file location
DOCKER_COMPOSE_FILE="airflow/docker-compose.yml"

# Container image for data generator
DOCKER_IMAGE_GENERATOR="clickstream-generator:latest"

# Container image for Airflow
DOCKER_IMAGE_AIRFLOW="apache/airflow:2.8.1"

# Example:
# These are used when running: docker-compose up
```

**Why?**
- Makes it easy to reference images in scripts
- Can version containers without changing code

---

### 2.8 Logging & Monitoring

```bash
# Logging Configuration
# =====================

# Log level for all applications
# Options: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL="INFO"

# Where to save logs
LOG_PATH="{AIRFLOW_HOME}/logs"

# Enable debug mode? (more verbose output)
DEBUG_MODE="false"

# Example: LOG_PATH="/home/airflow/logs"
```

**Why?**
- `LOG_LEVEL` controls verbosity
- Logs help debug problems later

---

## 3. How to Use These Variables

### In Python

```python
import os

# Read from environment
project_id = os.getenv("GCP_PROJECT_ID")
bucket_name = os.getenv("GCS_BUCKET_NAME")

# With fallback (if not set, use default)
log_level = os.getenv("LOG_LEVEL", "INFO")

# Raise error if required variable missing
if not project_id:
    raise ValueError("GCP_PROJECT_ID environment variable not set!")
```

### In dbt (profiles.yml)

```yaml
booking-clickstream-dbt:
  outputs:
    dev:
      type: bigquery
      project: "{{ env_var('GCP_PROJECT_ID') }}"
      dataset: "{{ env_var('BIGQUERY_DATASET_STAGING') }}"
      threads: "{{ env_var('DBT_THREADS', 4) }}"
```

### In Bash

```bash
# Load from file
source .env

# Use in commands
gsutil mb gs://${GCS_BUCKET_NAME}

# In docker-compose
docker-compose -f ${DOCKER_COMPOSE_FILE} up
```

---

## 4. Security Best Practices

### DO ✓

```bash
# Store in .env (which is in .gitignore)
source .env

# Use IAM roles instead of service account keys
gcloud auth application-default login

# Rotate credentials regularly

# Use strong passwords for Airflow
AIRFLOW_PASSWORD="very-long-random-string-123!@#"

# Different credentials per environment
```

### DON'T ✕

```bash
# ✕ NEVER commit .env to Git
git add .env  # DON'T DO THIS!

# ✕ NEVER hardcode credentials
GCP_PROJECT_ID="my-secret-project"  # DON'T DO THIS!

# ✕ NEVER use weak passwords
AIRFLOW_PASSWORD="password"  # DON'T DO THIS!

# ✕ NEVER share screenshots with env vars visible
```

---

## 5. Common Issues & Solutions

### Issue: "Variable not found"

```bash
# Problem: You set var in one terminal, but it's not in Python script

# Solution: source .env BEFORE running Python
source .env
python src/data_generator/main.py

# Or add to script:
# import dotenv; dotenv.load_dotenv()
```

### Issue: Different values in Dev vs Prod

```bash
# Create separate env files:
.env.dev          # Development settings
.env.prod         # Production settings

# Load based on environment:
if [ "$ENVIRONMENT" == "prod" ]; then
    source .env.prod
else
    source .env.dev
fi
```

### Issue: "Service account key not found"

```bash
# Use Application Default Credentials instead:
gcloud auth application-default login

# This uses gcloud CLI auth (no JSON key needed!)
# More secure and org-policy compliant
```

---

**Last Updated:** 2026-05-29