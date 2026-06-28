# GCP Authentication Specification (Keyless Approach)

> This document describes the passwordless/keyless authentication strategy used in this project for both local development and cloud deployment, adhering to the principle of least privilege and Google Cloud security best practices.

---

## Why Avoid Service Account JSON Keys?
- **Security Risk:** JSON keys do not expire by default and are the #1 cause of credentials leaks in open-source repositories.
- **Compliance:** Modern enterprise environments ban static JSON keys in favor of short-lived tokens and identity federation.
- **Maintenance:** Managing, rotating, and storing secrets securely adds unnecessary overhead to the pipeline.

---

## 1. Local Development Setup (Application Default Credentials - ADC)

To interact with GCP services (GCS, BigQuery) from your local machine or local script executions, we use **Application Default Credentials**.

### Step-by-Step Local Configuration:
1. Ensure the Google Cloud SDK (`gcloud`) is installed.
2. Authenticate your main CLI session:
```bash
gcloud auth login
```
3. Generate the local ADC file for application SDKs (Python, dbt, etc):
```bash
gcloud auth application-default login
```
> This command creates a credentials file at `~/.config/gcloud/application_default_credentials.json` on Linux/macOS or `%APPDATA%\gcloud\application_default_credentials.json` on Windows.

---

## 2. Docker & Apache Airflow Integration

Since Airflow runs inside Docker containers, it needs access to the local host's ADC credentials without embedding secrets inside the image.

### Docker Compose Mapping (Best Practice):

To make your local credentials available to Airflow, mount your local `gcloud` configuration directory as a read-only volume and expose the `GOOGLE_APPLICATION_CREDENTIALS` environment variable inside your `docker-compose.yaml`:

```yaml
services:
    airflow-worker:
      ...
      environment:
        - GOOGLE_APPLICATION_CREDENTIALS=/home/airflow/.config/gcloud/application_default_credentials.json
        - GCP_PROJECT_ID=${GCP_PROJECT_ID}
      volumes:
        - ~/.config/gcloud:/home/airflow/.config/gcloud:ro
```

When Airflow tasks trigger Python scripts, dbt packages, or GCP operators, the Google SDK will seamlessly assume your identity.

---

## 3. Production Environment (Cloud Native Identity)

When deploying this architecture to production (e.g., Google Cloud Composer for Airflow, Google Cloud Functions for ingestion):

1. **No Code Changes:** The code remains identical. The Google SDK automatically detects if it's running inside GCP.
2. **Attached Service Accounts:** We attach a dedicated Service Account (IAM Identity) to the Cloud Function or Composer Environment.
3. **IAM Roles Required (Least Privilege):**
    - **Ingestion (Cloud Function):** `roles/storage.objectCreator` on the specific raw bucket.
    - **Orchestration/Transformation (dbt/Airflow):** `roles/storage.objectViewer` (to read raw data) and `roles/bigquery.admin` (scoped down to the project datasets to create/ drop models).

---

## 4. Security Recommendations for Sandbox Users

- **Timeouts**: Local tokens expire and need a periodic refresh (`gcloud auth application-default login`). This is expected behavior.
- **Scoping:** Ensure your user account has at least `roles/storage.admin` and `roles/bigquery.admin` inside your assigned Sandbox Project to execute infrastructure management scripts.

---

Last updated: 2026-06-28 

