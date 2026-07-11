import jsonschema
from datetime import datetime
from dateutil import parser as date_parser
from generator import ClickstreamGenerator

SCHEMA = {
    "type": "object",
    "required": ["event_id", "event_timestamp", "user_id", "session_id", "event_type", "page_id", "date_id", "loaded_at"],
    "properties": {
        "event_id": {"type": "string"},
        "event_timestamp": {"type": "string"},
        "loaded_at": {"type": "string"},
        "user_id": {"type": "integer"},
        "session_id": {"type": "string"},
        "event_type": {"type": "string", "enum": ["pageview", "click", "add_to_cart", "purchase"]},
        "page_id": {"type": "integer"},
        "date_id": {"type": "integer"}
    }
}

def test_generate_small():
    gen = ClickstreamGenerator(num_users=5, num_pages=5, num_products=10, p_pageview=0.6, p_click=0.2, p_add_to_cart=0.1, p_purchase=0.1)
    events = list(gen.generate(20, start_date=datetime(2026, 5, 5)))
    assert len(events) == 20

    for ev in events:
        jsonschema.validate(instance=ev, schema=SCHEMA)
        date_parser.isoparse(ev["event_timestamp"])
        date_parser.isoparse(ev["loaded_at"])
