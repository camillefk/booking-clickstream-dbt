# Development Setup Guide

**Time to Complete:** 30-45 minutes (first time)

> This guide walks you through setting up the entire project locally on your machine.

---

## Prerequisites (Do You Have These?)

Before starting, verify you have:

### System Requirements

- **OS:** macOS, Linux, or Windows (with WSL2)
- **Disk Space:** 10GB free (for Docker, dependencies, data)
- **RAM:** 8GB minimum (16GB recommended for Airflow)
- **Internet:** Stable connection (for downloading packages)

### Required Software

Check if you have these installed:

```bash
# Python 3.10+
python --version
# Expected: Python 3.10.x or 3.11.x or 3.12.x

# Docker & Docker Compose
docker --version
# Expected: Docker 24.x or newer
docker-compose --version
# Expected: Docker Compose 2.x or newer

# Google Cloud SDK
gcloud --version
# Expected: Google Cloud SDK with bq, gsutil

# Git
git --version
# Expected: Git 2.x or newer
```

### Optional but Recommended

- **Visual Studio Code** with Python extension
- **DBeaver** or **BigQuery Studio** (for SQL queries)
- **Postman** (for API testing)
- **Make** (simplifies commands)

---

## Quick Start (5 minutes)

### Step 1: Clone Repository

```bash
git clone https://github.com/camillefk/booking-clickstream-dbt.git
cd booking-clickstream-dbt
```

### Step 2: Authenticate with GCP

```bash
# Login to Google Cloud (opens browser)
gcloud auth application-default login

# Set your GCP project (replace with YOUR sandbox project)
gcloud config set project YOUR_SANDBOX_PROJECT_ID

# Verify
gcloud config list
```

**Why?**
- This gives your computer permission to access GCP
- No JSON keys needed (secure!)
- Follows org policies

### Step 3: Create Environment File

```bash
# Copy template
cp config/environment_template.md .env

# Edit with YOUR values (use nano, vim, or VSCode)
nano .env
```

Edit these values with YOUR GCP information:

```bash
# Find these in Google Cloud Console
GCP_PROJECT_ID="your-sandbox-project-id"
GCP_REGION="europe-west1" # Or your preferred region
GCS_BUCKET_NAME="your-project-id-clickstream-raw"

# These can stay as defaults
BIGQUERY_DATASET_RAW="clickstream_raw"
BIGQUERY_DATASET_STAGING="clickstream_staging"
BIGQUERY_DATASET_ANALYTICS="clickstream_analytics"

# For local development
DBT_TARGET="dev"
AIRFLOW_HOME="$HOME/airflow"  # or /home/airflow if using Docker
```

### Step 4: Load Environment

```bash
source .env
echo "✓ Environment loaded. Verify:"
echo $GCP_PROJECT_ID
```

### Step 5: Create GCP Infrastructure

```bash
# Make script executable
chmod +x infra/setup_gcp.sh

# Run setup (creates buckets, datasets)
./infra/setup_gcp.sh
```

**Expected output:**
```
Creating bucket: your-project-clickstream-raw
Creating dataset: clickstream_raw
Creating dataset: clickstream_staging
Creating dataset: clickstream_analytics
✓ Infrastructure created successfully!
```

---

## Part 1: Set Up Python Environment

### Install Python 3.10+ (If Needed)

**macOS (with Homebrew):**
```bash
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv
```

**Windows:**
- Download from [python.org](https://www.python.org/)
- Check "Add Python to PATH" during installation

### Create Virtual Environment

```bash
# Navigate to project root
cd booking-clickstream-dbt

# Create virtual environment
python3.11 -m venv venv

# Activate it
# macOS/Linux:
source venv/bin/activate

# Windows
venv\Scripts\activate

# Verify (should show "venv" in prompt)
# (venv) camille@machine booking-clickstream-dbt %
```

**Why virtual environment?**
- Isolates dependencies (don't affect other projects)
- Different projects can use different package versions
- Easy to delete (just remove folder)

### Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install base dependencies
pip install -r requirements.txt

# Install dbt
pip install dbt-bigquery

# Install Airflow (for later)
pip install apache-airflow[gcp,bigquery]

# Install development tools
pip install pytest black flake8 mypy

# Verify
python --version
dbt --version
airflow version
```

**What each package does:**
- `dbt-bigquery`- Run dbt with BigQuery
- `apache-airflow` - Orchestration framework
- `pytest` - Testing
- `black` - Code formatting
- `flake8` - Linting

---

## Part 2: Configure dbt

### Create dbt Project

```bash
# If not already created
cd dbt

# Initialize if needed (usually already done)
dbt init booking-clickstream-dbt
```

### Configure dbt Profiles

dbt needs to know how to connect to BigQuery:

```bash
# Create dbt profiles directory
mkdir -p ~/.dbt

# Create profiles.yml
nano ~/.dbt/profiles.yml
```

**Paste this (edit with your values):**

```yaml
booking-clickstream-dbt:
  outputs:
    dev:
      type: bigquery
      project: "{{ env_var('GCP_PROJECT_ID') }}"
      dataset: "{{ env_var('BIGQUERY_DATASET_STAGING') }}"
      location: "{{ env_var('GCP_REGION', 'europe-west1') }}"
      method: oauth
      threads: 4
      timeout_seconds: 300
      priority: interactive
      retries: 1

    prod:
      type: bigquery
      project: "{{ env_var('GCP_PROJECT_ID') }}"
      dataset: "{{ env_var('BIGQUERY_DATASET_ANALYTICS') }}"
      location: "{{ env_var('GCP_REGION', 'europe-west1') }}"
      method: oauth
      threads: 1
      timeout_seconds: 300
      priority: batch
      retries: 3

  target: dev  # Default target (can override with --target prod)
```

**Save and verify:**

```bash
# Change to dbt directory
cd dbt

# Test connection
dbt debug

# Expected output: ✓ All checks passed!
```

### Create dbt Project Config

**Edit `dbt/dbt_project.yml`:**

```yaml
name: 'booking_clickstream_dbt'
version: '1.0.0'
config-version: 2

profile: 'booking-clickstream-dbt'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
data-paths: ["data"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]
target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  booking_clickstream_dbt:
    materialized: table
    staging:
      materialized: view
    core:
      materialized: table
```

---

## Part 3: Set Up Airflow

### Initialize Airflow

```bash
# Create airflow home (if it doesn't exist)
mkdir -p ~/airflow

# Set Airflow home
export AIRFLOW_HOME=~/airflow

# Initialize database
airflow db init

# Create user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

### Start Airflow

**Option 1: Local (Quickest for Testing)**

```bash
# In one terminal, start scheduler
airflow scheduler

# In another terminal, start webserver
airflow webserver

# Access at http://localhost:8080
# Login: admin / admin
```

**Option 2: Docker Compose (Recommended)**

```bash
# Navigate to airflow directory
cd airflow

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs airflow-webserver

# Access at http://localhost:8080
```

### Verify Airflow

```bash
# List DAGs
airflow dags list

# Test a DAG
airflow dags test clickstream_ingestion_dag 2026-05-06

# View DAG structure
airflow dags show clickstream_ingestion_dag
```

---

## Part 4: Set Up Data Generator (Docker)

### Build Docker Image

```bash
# Navigate to data generator
cd src/data_generator

# Build image
docker build -t clickstream-generator:latest .

# Verify
docker images | grep clickstream
```

### Run Generator

```bash
# Run with environment variables
docker run \
    --env-file ../../.env \
    --rm \
    clickstream-generator:latest

# Or with docker-compose
docker-compose -f ../../docker-compose.yml up generator
```

**Expected output:**
```
Starting data generation...
Generating 10000 events...
✓ Generated 10000 events in 2.5 seconds
Uploading to GCS...
✓ Uploaded to gs://your-bucket/raw/clickstream/2026-05-06/
```

---

## ✓ Validation Checklist

After setup, verify everything works:

### Python & Dependencies

```bash
# Check Python version
python --version
# Expected: 3.10+

# Check key packages
python -c "import dbt; print(dbt.__version__)"
python -c "import airflow; print(airflow.__version__)"
python -c "from google.cloud import bigquery; print('✓ BigQuery SDK installed')"
```

### GCP Authentication

```bash
# Verify gcloud auth
gcloud auth application-default print-access-token | head -c 50
# Expected: Shows token (auth working)

# Verify project
gcloud config list --format='value(core.project)'
# Expected: Your sandbox project ID
```

### dbt

```bash
cd dbt

# Test connection
dbt debug
# Expected: ✓ All checks passed!

# Dry run (don't actually query)
dbt compile --select stg_*
# Expected: No errors
```

### BigQuery

```bash
# List datasets
bq ls
# Expected: Shows your datasets (raw, staging, analytics)

# List tables in raw dataset
bq ls --dataset_id=clickstream_raw
# Expected: Shows tables (if data uploaded)
```

### Airflow

```bash
# List DAGs
airflow dags list
# Expected: Shows your DAGs

# Test DAG syntax
airflow dags test clickstream_ingestion_dag 2026-05-06
# Expected: No errors
```

### Data Generator

```bash
cd src/data_generator

# Test import
python -c "from generator import ClickstreamGenerator; print('✓ Generator imports successfully')"

# Run generator
python main.py --events 100 --dry-run
# Expected: Generates 100 events (doesn't upload)
```

---

## Daily Development Workflow

After initial setup, this is your daily flow:

### 1. Load Environment (Every Terminal)

```bash
# From project root
source .env
```

### 2. Activate Virtual Environment

```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Work on dbt Models

```bash
cd dbt

# Make changes to models/...

# Test locally
dbt run --select stg_* --target dev
dbt test

# Preview SQL (don't run)
dbt parse
```

### 4. Test Data Pipeline

```bash
# Generate sample data
cd src/data_generator
python main.py --events 1000

# Run dbt transformations
cd ../../dbt
dbt run
dbt test

# Query results
bq query --use_legacy_sql=false "
  SELECT COUNT(*) as total_events 
  FROM clickstream_staging.stg_clickstream_events
"
```

### 5. Debug Issues

```bash
# Check logs
tail -f ~/airflow/logs/...

# Run dbt with debug logging
dbt run --debug

# Query for issues
bq query "SELECT * FROM clickstream_raw.raw_clickstream_events LIMIT 10"
```

---

## Troubleshooting

### Problem: "gcloud not found"

```bash
# Solution: Install Google Cloud SDK
# macOS
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash

# Windows
# Download from: https://cloud.google.com/sdk/docs/install
```

### Problem: "Permission denied accessing GCS bucket"

```bash
# Solution: Re-authenticate
gcloud auth application-default login

# Or check project is set
gcloud config set project YOUR_PROJECT_ID
```

### Problem: "dbt: command not found"

```bash
# Solution: Make sure venv is activated
source venv/bin/activate

# Re-install dbt
pip install dbt-bigquery
```

### Problem: "Airflow scheduler not running"

```bash
# Check Airflow logs
tail -f ~/airflow/logs/scheduler/latest/

# Restart scheduler
airflow scheduler --debug
```

### Problem: "Docker image build fails"

```bash
# Solution: Check Dockerfile
docker build -t clickstream-generator:latest . --progress=plain

# Rebuild without cache
docker build --no-cache -t clickstream-generator:latest .
```

### Problem: "BigQuery quota exceeded"

```bash
# Solution: Reduce event generation
export GENERATOR_DAILY_EVENTS="1000"  # Was 10000

# Or wait 24 hours for quota reset
```

---

## File Structure After Setup

```
booking-clickstream-dbt/
├── .env                              # ✓ Your environment (created)
├── venv/                             # ✓ Virtual environment (created)
│   └── bin/python                    # Your Python
├── dbt/
│   ├── dbt_project.yml              # ✓ Configured
│   ├── profiles.yml                 # (in ~/.dbt/profiles.yml)
│   ├── models/                      # Your models (to create)
│   └── tests/                       # Tests (to create)
├── src/data_generator/
│   ├── main.py                      # (to create)
│   └── Dockerfile                   # (to create)
├── airflow/
│   ├── docker-compose.yml           # ✓ Ready
│   ├── dags/                        # Your DAGs (to create)
│   └── logs/                        # Created by Airflow
├── infra/
│   └── setup_gcp.sh                 # ✓ Already ran
└── docs/
    ├── DEVELOPMENT_SETUP.md         # This file
    └── ...
```

---

## Next Steps

1. Follow this guide to set up
2. Run `dbt debug` to verify connection
3. Generate sample data with `python src/data_generator/main.py`
4. Check data in BigQuery: `bq ls`
5. Read `docs/DATA_MODELING.md` to understand the schema
6. Start building dbt models (Week 3)
7. Set up Airflow DAGs (Week 4)

---

## 📞 Getting Help

### Check These First

1. **Error in logs?** Check `~/airflow/logs/` or Docker logs
2. **dbt error?** Run `dbt debug` to see details
3. **Data missing?** Check GCS with: `gsutil ls gs://{bucket}/`
4. **Permission issue?** Run `gcloud auth application-default login`

### Still Stuck?

1. Check `docs/TROUBLESHOOTING.md` (create if needed)
2. Search error message + "dbt" or "Airflow"
3. Check GitHub Issues in this repo

---

**Last Updated:** 2026-06-11 