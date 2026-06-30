#!/bin/bash

# =================================================================================
# Description: Destructive script to wipe project infrastructure (Sandbox cleanup)
# =================================================================================

set -euo pipefail

GCP_PROJECT_ID="${GCP_PROJECT_ID:-}"

if [ -z "$GCP_PROJECT_ID" ]; then
    echo "CRITICAL ERROR: Environment variable GCP_PROJECT_ID is not set."
    exit 1
fi

BUCKET_NAME="${GCP_PROJECT_ID}-clickstream-raw"
DATASETS=("clickstream_raw" "clickstream_staging" "clickstream_analytics")

echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo " WARNING: Destructive Action Initiated"
echo " This will permanently delete data inside $GCP_PROJECT_ID"
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
read -p "Are you absolutely sure you want to delete all resources? (y/N) " -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Teardown aborted by user."
    exit 0
fi

# --- 1. Remove BigQuery Datasets (Cascading delete) ---
for dataset in "${DATASETS[@]}"; do
    echo "--> Dropping BigQuery Dataset: $dataset (and all its tables)..."
    if bq show --project_id="$GCP_PROJECT_ID" "$dataset" >/dev/null 2>&1; then
        bq rm -f -r --project_id="$GCP_PROJECT_ID" "$dataset"
        echo "  ✓ Dataset '$dataset' dropped."
    else
        echo "  Dataset '$dataset' not found. Skipping."
    fi
done

# --- 2. Remove GCS Bucket (and all internal objects) ---
echo "--> Deleting Cloud Storage Bucket: gs://$BUCKET_NAME..."
if gcloud storage buckets describe "gs://$BUCKET_NAME" --project="$GCP_PROJECT_ID" >/dev/null 2>&1; then
    # Force delete bucket even if it contains objects
    gcloud storage buckets delete "gs://$BUCKET_NAME" --project="$GCP_PROJECT_ID" --quiet
    echo "  ✓ Bucket gs://$BUCKET_NAME deleted."
else
    echo "  Bucket not found. Skipping."
fi

echo "================================================================="
echo " Teardown completed. Resources successfully cleared."
echo "================================================================="