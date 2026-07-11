import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Iterator, Dict, Any, Optional
from faker import Faker


fake = Faker()

class ClickstreamGenerator:
    def __init__(
        self,
        num_users: int = 500,
        num_pages: int = 50,
        num_products: int = 1000,
        p_pageview: float = 0.6,
        p_click: float = 0.2,
        p_add_to_cart: float = 0.1,
        p_purchase: float = 0.1,
        session_timeout_minutes: int = 30,
    ):
        self.num_users = num_users
        self.num_pages = num_pages
        self.num_products = num_products

        # Normalize probabilities
        s = p_pageview + p_click + p_add_to_cart + p_purchase
        self.p_pageview = p_pageview / s
        self.p_click = p_click / s
        self.p_add_to_cart = p_add_to_cart / s
        self.p_purchase = p_purchase / s
        self.session_timeout = timedelta(minutes=session_timeout_minutes)

        # Pre-generate pools using Integers (DATA_MODELING.md)
        self.users = list(range(1, self.num_users + 1))
        self.pages = list(range(1, self.num_pages + 1))
        self.products = list(range(1, self.num_products + 1))

        # Per-user session state: {user_id: (session_id, last_event_time)}
        self.sessions = {}

    def _new_session(self, user_id: int, ts: datetime) -> str:
        # Generates format like 's_123_abc123'
        sid = f"s_{user_id}_{uuid.uuid4().hex[:6]}"
        self.sessions[user_id] = (sid, ts)
        return sid

    def _maybe_get_session(self, user_id: int, ts: datetime) -> str:
        st = self.sessions.get(user_id)
        if st is None:
            return self._new_session(user_id, ts)
        session_id, last_ts = st
        if ts - last_ts > self.session_timeout:
            return self._new_session(user_id, ts)
        # update last timestamp
        self.sessions[user_id] = (session_id, ts)
        return session_id

    def _random_event_type(self, prev_type: Optional[str] = None) -> str:
        # General rule with the new event types
        return random.choices(
            population=["pageview", "click", "add_to_cart", "purchase"],
            weights=[self.p_pageview, self.p_click, self.p_add_to_cart, self.p_purchase],
            k=1,
        )[0]

    def _make_event(
        self, event_ts: datetime, user_id: int, session_id: str, event_type: str
    ) -> Dict[str, Any]:

        # Formating dates according to the target table constraints
        event_timestamp_str = event_ts.isoformat(timespec="milliseconds") + "Z"
        date_id = int(event_ts.strftime("%Y%m%d"))
        loaded_at_str = datetime.now(timezone.utc).isoformat(timespec="milliseconds")

        event = {
            "event_id": f"evt_{uuid.uuid4().hex[:8]}",
            "user_id": user_id,
            "session_id": session_id,
            "page_id": random.choice(self.pages),
            "product_id": None,
            "date_id": date_id,
            "event_timestamp": event_timestamp_str,
            "event_type": event_type,
            "event_value": None,
            "user_agent": fake.user_agent(),
            "referrer_url": random.choice([None, "https://www.google.com/", "https://www.facebook.com/"]),
            "loaded_at": loaded_at_str
        }

        # Contextual rules based on event_type
        if event_type in ["click", "add_to_cart", "purchase"]:
            event["product_id"] = random.choice(self.products)

        if event_type == "purchase":
            event["event_value"] = round(random.uniform(5.0, 500.0), 2)

        return event

    def generate(self, num_events: int, start_date: Optional[datetime] = None) -> Iterator[Dict[str, Any]]:
        if start_date is None:
            start_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        events_emitted = 0
        while events_emitted < num_events:
            user = random.choice(self.users)
            session_start = start_date + timedelta(seconds=random.randint(0, 24 * 3600 - 1))
            session_id = self._new_session(user, session_start)

            session_length = random.randint(1, 8)
            prev_type = None
            ts = session_start

            for i in range(session_length):
                if events_emitted >= num_events:
                    break

                if i == 0:
                    event_type = "pageview"
                else:
                    event_type = self._random_event_type(prev_type)

                ev = self._make_event(ts, user, session_id, event_type)
                yield ev

                events_emitted += 1
                prev_type = event_type
                ts = ts + timedelta(seconds=random.randint(2, 120))
