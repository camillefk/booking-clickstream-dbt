# Booking.com Clickstream & Dimensional Modeling (dbt Focus)

> Production-grade clickstream data platform showcasing dimensional modeling with dbt on Google Cloud. Demonstrates complete ELT pipeline and best practices in data engineering.

---

## Project Overview

This project simulates a **real-world data engineering challenge**: transforming raw clickstream events (user navigation, click, purchases) into a dimensional model ready for business analytics.

### What's the Problem We're Solvig?

Raw clickstream data is noisy and unstructured. Our job is to **organize this chaos** into a format that:
- ✓ Business analysts can query easily
- ✓ Tracks user behavior accurately (sessions, funnels)
- ✓ Maintains data quality and lineage
- ✓ Scales to millions of events

### How Do We Solve It?

Raw Events (JSON) -> GCS (Data Lake) -> BigQuery (Raw Layer) -> dbt (Transformations) -> Looker Studio (Visualization). All orchestrated by Apache Airflow.

---

## Technology Stack

| Component | Technology | Why? |
|-----------|-----------|------|
| **Data Generation** | Python + Docker | Simulates real clickstream events |
| **Data Lake** | Google Cloud Storage (GCS) | Cheap, scalable, serverless |
| **Data Warehouse** | BigQuery | Fast analytics, ANSI SQL, serverless |
| **Transformations** | dbt | Industry standard, data lineage, testing |
| **Orchestration** | Apache Airflow | Workflow scheduling, monitoring, retries |
| **Visualization** | Looker Studio | Free, integrates with BigQuery |
| **IaC & Config** | Environment Variables | No hardcoded secrets, easy to scale |

---

## Quick Start !

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- `gcloud` CLI (Google Cloud SDK)
- Git

### Setup (15 minutes)

1. **Clone the repository:**
```bash
git clone https://github.com/camillefk/booking-clickstream-dbt.git
cd booking-clickstream-dbt
```

Create your `.env` file based on the `.env.example` file and update it with YOUR own values.

2. **Create GCP infrastructure:**
```bash
cd infra
chmod +x setup_gcp.sh # Make the script executable
./setup_gcp.sh        # Run the setup to create GCP resources
cd ..
```

3. **Generate sample data:**
```bash
cd src/data_generator
docker build -t clickstream-gen .
docker run --env-file ../../.env clickstream-gen
cd ../..
```

4. **Run Airflow:**
```bash
cd airflow
docker-compose up -d
# Access at http://localhost:8080
cd ..
```

5. **Run dbt:**
```bash
cd dbt
dbt run --target dev
dbt test
dbt docs generate
cd ..
```

For detailed setup, see `DEVELOPMENT_SETUP.md`

---

## Documentation

- `ARCHITECTURE.md` - Design decisions & trade-offs
- `DATA_MODELING.md` - Dimensional model explained
- `DEVELOPMENT_SETUP.md` - Step-by-step setup guide
- `DBT_PROJECT_SETUP.md` - dbt project structure
- `AIRFLOW_SETUP.md` - Airflow orchestration
- `GCP_AUTHENTICATION.md` - Auth without JSON keys
- `TROUBLESHOOTING.md` - Common issues & solutions

---

## Project Structure

```text
booking-clickstream-dbt/
├── docs/                    # Documentation
├── src/data_generator/      # Clickstream generator
├── dbt/                     # Transformations (Star Schema)
├── airflow/                 # Pipeline orchestration
├── infra/                   # GCP infrastructure
├── config/                  # Configuration templates
├── .gitignore               # Git ignore rules
├── README.md                # This file
└── CHANGELOG.md             # Version history
```

---

## Contributing

Want to add features ? See `CONTRIBUTING.md`

---

## Support

Found an issue ? Check `TROUBLESHOOTING.md` first.

---

## License

MIT License - See `LICENSE` for details.

---

## Next Steps 

1. Read `ARCHITECTURE.md` to understand the design
2. Follow `DEVELOPMENT_SETUP.md` to get started 
3. Start building ! 