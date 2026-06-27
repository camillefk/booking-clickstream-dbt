# Synthetic Data Specification - Clickstream

This document defines the clickstream event JSON schema used by the project, a realistic example event, recommended daily volumes for local testing, and the default event distribution (70% navigation, 20% click, 10% purchase). Short rationales are included so you understand why each field and choice exists.

---

## Goal

Provide a stable, well-documented schema for the synthetic data generator and any producers so that raw data landing in GCS and later processed by dbt is consistent and predictable.

Why this matters:
- Enables automated tests and schema validations.
- Makes dbt transformations predictable and easier to debug.
- Helps ensure analytics and dashboards consume a known shape.

---

## 1. Clickstream event JSON (field descriptions)

Each event is a JSON object. Fields marked (required) are essential for ordering and identification; optional fields enrich events.

- event_id (string, required) — UUID v4 for the event. Rationale: guarantees uniqueness and traceability.
- event_timestamp (string, required) — ISO 8601 UTC timestamp (e.g. "2026-06-22T12:34:56.789Z"). Rationale: ordering and time-window analysis.
- user_id (string|null, required) — user identifier; can be null for anonymous visitors. Rationale: user-level analysis.
- session_id (string, required) — groups events into a browsing session. Rationale: sessionization.
- event_type (string, required) — event category. Allowed: "navigation", "click", "purchase". Rationale: simple actionable categories for modeling.
- page_url (string, required) — page URL where the event happened. Rationale: page context.
- referrer (string|null, optional) — referrer URL (acquisition/source).
- element_id (string|null, optional) — id of clicked element (when applicable).
- product_id (string|null, optional) — product identifier for purchase/add-to-cart events.
- price (number|null, optional) — transaction amount for purchases.
- currency (string|null, optional) — ISO currency code (e.g. "USD", "EUR").
- user_agent (string, optional) — browser/device user agent (useful for device analysis).
- ip_address (string|null, optional) — IP address (mask or omit in production for privacy).
- geo (object, optional) — { country: string, region: string, city: string } for simpler geo-aggregation.
- properties (object, optional) — free-form map for custom attributes (e.g. {"button_color":"red"}).

---

## 2. JSON Schema (use for generator validation)

Validate records before upload using this schema to avoid malformed records entering the pipeline.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_timestamp", "user_id", "session_id", "event_type", "page_url"],
  "properties": {
    "event_id": {"type": "string"},
    "event_timestamp": {"type": "string", "format": "date-time"},
    "user_id": {"type": ["string", "null"]},
    "session_id": {"type": "string"},
    "event_type": {"type": "string", "enum": ["navigation", "click", "purchase"]},
    "page_url": {"type": "string"},
    "referrer": {"type": ["string", "null"]},
    "element_id": {"type": ["string", "null"]},
    "product_id": {"type": ["string", "null"]},
    "price": {"type": ["number", "null"]},
    "currency": {"type": ["string", "null"]},
    "user_agent": {"type": "string"},
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
- required fields enforce a minimum viable event.
- enum restricts event_type to expected categories.
- additionalProperties=false reduces accidental fields.

---

## 3. Example event (full JSON)

A realistic, complete example. Remove comments when generating NDJSON.

```json
{
  "event_id": "b6d9f7c2-3a2e-4f7b-9ef5-1a2b3c4d5e6f",
  "event_timestamp": "2026-06-26T12:34:56.789Z",
  "user_id": "user_12345",
  "session_id": "sess_98765",
  "event_type": "purchase",
  "page_url": "https://www.example.com/checkout",
  "referrer": "https://www.google.com/",
  "element_id": null,
  "product_id": "prod_54321",
  "price": 79.99,
  "currency": "EUR",
  "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
  "ip_address": "203.0.113.45",
  "geo": {"country": "NL", "region": "North Holland", "city": "Amsterdam"},
  "properties": {"coupon": "SUMMER21", "payment_method": "card"}
}
```

---

## 4. File format & partitioning

- Format: NDJSON (newline-delimited JSON), 1 JSON object per line.
- Rationale: streaming-friendly and BigQuery-compatible.
- Compression: optionally gzip (.ndjson.gz) - BigQuery accepts gzipped NDJSON.
- GCS layout (recommended): gs://{bucke}/raw/clickstream/YYYY-MM-DD/part-000.ndjson
- Rationale: date prefixes simplify daily ingestion and partitioning in BigQuery.

---

## 5. Recommended daily volumes (local testing)

Profiles for different testing needs:
- tiny (fast): 1,000 events/day - unit tests and quick iteration.
- small (realistic dev): 10,000 events/day - balanced variety without heavy quota use.
- medium (demo/perf): 100,000 events/day - test performance and estimate costs.

Use smaller profiles for development to save quota and get faster feedback; medium for performance testing.

---

## 6. Generation rules & sessionization

- Timestamps: generate in UTC; distribute events across the day (uniform or simple time-of-day pattern).
- session_id groups events per user. Default session timeout: 30 minutes of inactivity (configurable).
- IDs: event_id and session_id should be UUIDv4. user_id can be "user_N" or UUIDs.
- Conditional fields:
  - product_id, price, currency only when event_type == "purchase".
  - element_id normally present for event_type == "click".
- Edge cases: optionally generate a small percent (e.g., 0.5%) of nulls or malformed values to test pipeline robustness — log and isolate them to an errors prefix.

---

## 7. Validation & error handling

- Validate each record against the JSON Schema before upload (e.g., python jsonschema).
- On validation failure: write invalid lines to gs://{bucket}/raw/errors/YYYY-MM-DD/ and continue processing valid records.
- Keep an error log with reasons for easier debugging and reprocessing.

Rationale: prevents bad data from silently breaking downstream transformations.

---

## 8. NDJSON single-line example

{"event_id":"b6d9f7c2-3a2e-4f7b-9ef5-1a2b3c4d5e6f","event_timestamp":"2026-06-26T12:34:56.789Z","user_id":"user_12345","session_id":"sess_98765","event_type":"purchase","page_url":"https://www.example.com/checkout","referrer":"https://www.google.com/","element_id":null,"product_id":"prod_54321","price":79.99,"currency":"EUR","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...","ip_address":"203.0.113.45","geo":{"country":"NL","region":"North Holland","city":"Amsterdam"},"properties":{"coupon":"SUMMER21","payment_method":"card"}}

---

## 9. Privacy & production considerations

- Do not store raw IP addresses or unmasked PII in production. For testing, use synthetic or masked values.
- Use least-privilege IAM roles for services that write to GCS or BigQuery.
- Clearly tag synthetic data so it is never mixed with production data.

---

Last updated: 2026-06-26