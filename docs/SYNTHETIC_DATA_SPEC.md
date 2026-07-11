# Synthetic Data Specification - Clickstream (aligned with DATA_MODELING.md)

This specification documents the JSON schema used by the synthetic generator and the fields expected by the data model (fct_clickstream_events). It defines types, required fields, timestamp formats, an example event, recommended volumes and distribution, and validation guindance.

---

## Goal

Make raw clickstream events consistent with the dimensional model so ingestion, dbt transformations and analytics run without surprises.

Why this matters:
- Aligns generator output with BigQuery table schema.
- Avoids schema drift between raw → staging → analytics.
- Ensures reproducible tests and predictable dbt models.

---

## 1. Clickstream event JSON (field descriptions)

Each event is a JSON object. Fields marked (required) are mandatory for ingestion and modelling.

- event_id (string, required) — Unique event identifier (e.g. "evt_...").  Rationale: primary key for the event row.
- event_timestamp (string, required) — ISO 8601 UTC timestamp with milliseconds and trailing Z (example: "2026-05-11T10:30:45.123Z").  Rationale: unambiguous time for BigQuery TIMESTAMP.
- user_id (integer|null, required) — Numeric user identifier (FK to dim_users). Null for anonymous visitors.  Rationale: user-level joins and aggregates.
- session_id (string, required) — Session identifier (e.g. "s_123_abc123").  Rationale: sessionization and session-level facts.
- page_id (integer, required) — Numeric page identifier (FK to dim_pages).  Rationale: matches dimensional model and makes joins efficient.
- product_id (integer|null, optional) — Product identifier (FK to dim_products). Present for click/add_to_cart/purchase events.
- date_id (integer, required) — Partition/date key in YYYYMMDD (e.g. 20260511).  Rationale: date dimension FK and partitioning.
- event_type (string, required) — Allowed values: "pageview", "click", "add_to_cart", "purchase".  Rationale: consistent categories for modeling and funnels.
- event_value (number|null, optional) — Numeric value (e.g. price). Present for purchase events (FLOAT).
- user_agent (string|null, optional) — Browser / device string.
- referrer_url (string|null, optional) — Referrer URL or null.
- ip_address (string|null, optional) — IP (mask or omit in production).
- loaded_at (string, required) — ISO 8601 UTC timestamp when the record was created/loaded (audit).
- geo (object, optional) — { country: string, region: string, city: string }.
- properties (object, optional) — Free-form attributes (e.g. {"coupon":"SUMMER21"}).

Notes:
- "pageview" corresponds to previous "navigation" terminology.
---

## 2. JSON Schema (use for generator validation)

Validate records before upload using this schema to avoid malformed records entering the pipeline.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_timestamp", "user_id", "session_id", "page_id", "date_id", "event_type", "loaded_at"],
  "properties": {
    "event_id": {"type": "string"},
    "event_timestamp": {"type": "string", "format": "date-time"},
    "loaded_at": {"type": "string", "format": "date-time"},
    "user_id": {"type": ["integer", "null"]},
    "session_id": {"type": "string"},
    "page_id": {"type": "integer"},
    "product_id": {"type": ["integer", "null"]},
    "date_id": {"type": "integer"},
    "event_type": {"type": "string", "enum": ["pageview", "click", "add_to_cart", "purchase"]},
    "event_value": {"type": ["number", "null"]},
    "user_agent": {"type": ["string", "null"]},
    "referrer_url": {"type": ["string", "null"]},
    "ip_address": {"type": ["string", "null"]},
    "geo": {
      "type": "object",
      "properties": {
        "country": {"type": "string"},
        "region": {"type": "string"},
        "city": {"type": "string"}
      },
      "additionalProperties": false
    },
    "properties": {"type": "object"}
  },
  "additionalProperties": false
}
```

Rationale:
- required fields match the dimensional model.
- enum restricts event_type to expected categories.
- event_timestamp and loaded_at use ISO 8601 "date-time" strings suitable for BigQuery TIMESTAMP conversion.

---

## 3. Example event (full JSON)

A realistic, complete example.

```json
{
  "event_id": "evt_b6d9f7c2",
  "event_timestamp": "2026-05-11T10:30:45.123Z",
  "loaded_at": "2026-05-11T10:31:00.456Z",
  "user_id": 123,
  "session_id": "s_123_abc123",
  "page_id": 456,
  "product_id": 999,
  "date_id": 20260511,
  "event_type": "purchase",
  "event_value": 150.00,
  "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
  "referrer_url": "https://www.google.com/",
  "ip_address": "203.0.113.45",
  "geo": {"country": "NL", "region": "North Holland", "city": "Amsterdam"},
  "properties": {"coupon": "SUMMER21", "payment_method": "card"}
}
```

---

## 4. File format & partitioning

- Format: NDJSON (newline-delimited JSON), 1 JSON object per line.
- Compression: optionally gzip (.ndjson.gz) - BigQuery accepts gzipped NDJSON.
- GCS layout: gs://{bucket}/raw/clickstream/YYYY-MM-DD/events_batch_001.ndjson
- Partitioning: load to partitioned BigQuery tables by date_id or use ingestion-time partitioning. Prefer date_id partitioning for reproducibility.

---

## 5. Recommended daily volumes (local testing)

Profiles for different testing needs:
- tiny (fast): 1,000 events/day - unit tests and quick iteration.
- small (realistic dev): 10,000 events/day - balanced variety without heavy quota use.
- medium (demo/perf): 100,000 events/day - test performance and estimate costs.

Use smaller profiles for development to save quota and get faster feedback; medium for performance testing.

---

## 6. Generation rules & sessionization

- Timestamps: generate in UTC ISO 8601 with millisecond precision and trailing Z.
- session_id groups events per user. Default session timeout: 30 minutes of inactivity (configurable).
- IDs: user_id, page_id, product_id integers; event_id string UUID or prefixed id.
- Conditional fields:
  - product_id and event_value populated for add_to_cart/purchase events.
  - event_value is numeric for purchases (total_amount or final amount).
- Small fraction of intentionally invalid or null fields may be generated for robustness tests; these should be routed to an errors prefix.
---

## 7. Validation & error handling

- Validate each record against the JSON Schema before upload (e.g., python jsonschema).
- On validation failure: write invalid lines to gs://{bucket}/raw/errors/YYYY-MM-DD/ and continue processing valid records.
- Keep an error log with reasons for easier debugging and reprocessing.

Rationale: prevents bad data from silently breaking downstream transformations.

---

## 8. NDJSON single-line example

{"event_id":"evt_b6d9f7c2","event_timestamp":"2026-05-11T10:30:45.123Z","loaded_at":"2026-05-11T10:31:00.456Z","user_id":123,"session_id":"s_123_abc123","page_id":456,"product_id":999,"date_id":20260511,"event_type":"purchase","event_value":150.00,"user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...","referrer_url":"https://www.google.com/","ip_address":"203.0.113.45","geo":{"country":"NL","region":"North Holland","city":"Amsterdam"},"properties":{"coupon":"SUMMER21","payment_method":"card"}}

---

## 9. Privacy & production considerations

- Do not store raw IP addresses or unmasked PII in production. For testing, use synthetic or masked values.
- Use least-privilege IAM roles for services that write to GCS or BigQuery.
- Clearly tag synthetic data so it is never mixed with production data.

---

Last updated: 2026-07-11