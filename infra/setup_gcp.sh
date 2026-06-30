#!/bin/bash

# ==============================================================
# Description: Keyless Infrastructure Setup
# Architecture: GCS (raw) -> BigQuery (raw, staging, analytics)
# ==============================================================

set -euo pipefail

# --- Configuration & Validation ---
GCP_PROJECT_ID="${GCP_PROJECT_ID:-}"
GCP_REGION="${GCP_REGION:-us-central1}" # Defaulting to us-central1 if empty

if [ -z "$GCP_PROJECT_ID" ]; then
    echo "CRITICAL ERROR: Environment variable GCP_PROJECT_ID is not set."
    echo "Please export GCP_PROJECT_ID='your-sandbox-id' and retry."
    exit 1
fi

BUCKET_NAME="${GCP_PROJECT_ID}-clickstream-raw"
DATASETS=("clickstream_raw" "clickstream_staging" "clickstream_analytics")

echo "================================================================="
echo " Starting GCP Infrastructure Setup (Keyless Mode)"
echo " Target Project: $GCP_PROJECT_ID"
echo " Target Region:  $GCP_REGION"
echo "================================================================="

# --- 1. Enable Required GCP APIs ---
echo "--> Ensuring required Google Cloud APIs are active..."
gcloud services enable storage.googleapis.com bigquery.googleapis.com --project="$GCP_PROJECT_ID"

# --- 2. GCS Bucket Provisioning ---
echo "--> Checking Cloud Storage Bucket: gs://$BUCKET_NAME..."
if gcloud storage buckets describe "gs://$BUCKET_NAME" --project="$GCP_PROJECT_ID" >/dev/null 2>&1; then
    echo "  Bucket already exists. Skipping creation."
else
    echo "  Creating bucket gs://$BUCKET_NAME..."
    gcloud storage buckets create "gs://$BUCKET_NAME" \
        --project="$GCP_PROJECT_ID" \
        --location="$GCP_REGION" \
        --uniform-bucket-level-access
    echo "  ✓ Bucket created successfully with uniform bucket-level access."
fi

# --- 3. BigQuery Datasets Provisioning ---
for dataset in "${DATASETS[@]}"; do
    echo "--> Checking BigQuery Dataset: $dataset..."
    if bq show --project_id="$GCP_PROJECT_ID" "$dataset" >/dev/null 2>&1; then
        echo "  Dataset '$dataset' already exists. Skipping creation."
    else
        echo "  Creating Dataset '$dataset'..."
        bq mk --location="$GCP_REGION" \
              --project_id="$GCP_PROJECT_ID" \
              --dataset \
              --description="Dataset for booking clickstream project ($dataset layer)" \
              "$dataset"
        echo "  ✓ Dataset '$dataset' created successfully."
    fi
done

echo "================================================================="
echo " Infrastructure Provisioning Completed Successfully!"
echo "================================================================="