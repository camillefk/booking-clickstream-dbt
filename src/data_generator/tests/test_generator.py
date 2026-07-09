import jsonschema
from datetime import datetime
from generator import ClickstreamGenerator

SCHEMA = {
    "type": "object",
    "required": [
        "event_id", "user_id", "session_id", "page_id", "date_id", 
        "event_timestamp", "event_type", "loaded_at"
    ],
    "properties": {
        "event_id": {"type": "string"},
        "user_id": {"type": "integer"},
        "session_id": {"type": "string"},
        "page_id": {"type": "integer"},
        "product_id": {"type": ["integer", "null"]},
        "date_id": {"type": "integer"},
        "event_timestamp": {"type": "string"},
        "event_type": {"type": "string", "enum": ["pageview", "click", "purchase", "add_to_cart"]},
        "event_value": {"type": ["number", "null"]},
        "user_agent": {"type": ["string", "null"]},
        "referrer_url": {"type": ["string", "null"]},
        "loaded_at": {"type": "string"}
    }
}

def test_generate_small():

    gen = ClickstreamGenerator(
        num_users=5,
        num_pages=5,
        num_products=10,
        p_pageview=0.6,
        p_click=0.2,
        p_add_to_cart=0.1,
        p_purchase=0.1
    )

    events = list(gen.generate(20, start_date=datetime(2026, 5, 5)))
    assert len(events) == 20

    for ev in events:
        jsonschema.validate(instance=ev, schema=SCHEMA)
