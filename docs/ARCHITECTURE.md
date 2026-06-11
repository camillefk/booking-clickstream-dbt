# Architecture Decision Record

## 1. Project Overview

**Goal:** Build an end-to-end ELT pipeline that transforms raw clickstream events into a dimensional data model ready for business analytics.

**Scope:** Simulation of e-commerce/travel website click tracking and user journey analysis.

---

## 2. Architecture Overview

### Layer Breakdown

| Layer | Tool | Purpose | Why This Choice |
|-------|------|---------|-----------------|
| **1. Generation** | Python + Docker | Create synthetic clickstream events | Portable, reproducible, no external APIs |
| **2. Data Lake** | Google Cloud Storage | Store raw JSON events | Cheap, scales to TB, serverless |
| **3. Raw Warehouse** | BigQuery (raw dataset) | First load from GCS | Staging before transformation |
| **4. Transformation** | dbt | Clean, model, test data | Industry standard, builds data lineage |
| **5. Analytics** | BigQuery (analytics dataset) | Ready for queries/BI | Dimensional model, optimized for queries |
| **6. Visualization** | Looker Studio | Create dashboards | Free, integrates with BigQuery |
| **7. Orchestration** | Apache Airflow | Schedule everything | Manage dependencies, error handling, retries |

---

## 3. Component Decisions

### Why ELT?
- ✓ BigQuery is fast enough to handle raw data
- ✓ dbt runs AFTER load (cleaner separation)
- ✓ Can re-run transformations without re-extracting
- ✓ Cheaper (no intermediate processing servers)

### Why Star Schema?
- ✓ Analyts write simple queries: `SELECT * FROM facts JOIN dimensions`
- ✓ Queries run in seconds, not minutes
- ✓ Business users can understand the model

### Why dbt?
- ✓ Most popular in Europe
- ✓ Easy to learn SQL + YAML
- ✓ Built-in data quality testing

### Why self-hosted Airflow locally?
- ✓ Free (critical for portfolio)
- ✓ Can showcase in interviews
- ✓ Can run locally on Docker (easy setup)
- ✓ Same code that runs on Cloud Composer later

### Why No JSON Keys? (ADR-001)
**Problems:**
- ✕ Can't commit to GitHub (security risk)
- ✕ Hard to rotate
- ✕ Org policy forbids

**Solution:** Workload Identify Federation + gcloud CLI
```bash
# Instead of this (NEVER):
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

#We do this (SECURE):
gcloud auth application-default login
#dbt finds credentials automatically
```

**Benefits:**
- ✓ No secrets in code
- ✓ Org-compliant
- ✓ Easier credential rotation
- ✓ Follows Google best practices

---

## 4. Technology Choices

### Why Google Cloud?
- ✓ BigQuery in simple to use
- ✓ GCS is cheap for raw data
- ✓ Good free tier for portfolio projects

### Why Python for Generator?
- ✓ Easy to learn
- ✓ Rich libraries
- ✓ Easy to containerize (Docker)
- ✓ Can run locally or on Cloud Functions

---

## 5. Deployment Strategy

### Development (Local)
- Data generator: Docker on local machine
- Airflow: docker-compose.yml
- dbt: Run locally
- BigQuery: Sandbox project

### Production (Future)
- Data generator: Cloud Functions (triggered daily)
- Airflow: Cloud Composer (managed)
- dbt: Cloud Build (CI/CD)
- BigQuery: Prod project

**Why this strategy?**
- ✓ Easy to develop locally
- ✓ Easy to scale to prod
- ✓ Portable (can show to recruiters)

---

## 6. Security Decisions

| **Component** | **Approach** | **Why** |
|-------|---------|-----------------|
| Credentials | gcloud CLI + ADC | No secrets in code |
| Config | .env files | Easy to change per environment |
| Secrets | Excluded from git | gitignore prevents accidents |
| IAM | Minimal privilege | Only what's needed |

---

## 7. Monitoring & Operations

### How We'll Know It Works
- ✓ Airflow DAGs run without errors
- ✓ Data appears in BigQuery
- ✓ dbt tests pass
- ✓ Dashboards show dara

### Alerting Strategy
- Simple: Check DAG status in Airflow UI
- Medium: Email alerts on DAG failure (future)
- Advanced: Slack integration (future)

---

This architecture is designed to:
1. ✓ **Show recruiter value** - Dimensional modeling, data quality, orchestration
2. ✓ **Be learnable** - One tool at a time (python → dbt → airflow)
3. ✓ **Be cost-free** - Portfolio project
4. ✓ **Be professional** - Testing, documentation, version control

---

**Last Updated:** 2026/06/11