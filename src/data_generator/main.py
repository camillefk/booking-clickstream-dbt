import argparse
import logging
from datetime import datetime
from generator import ClickstreamGenerator
from gcs_uploader import GCSUploader
from config import Config

def setup_logging(level: str):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

def parse_args():
    parser = argparse.ArgumentParser(description="Clickstream synthetic data generator")
    parser.add_argument("--events", type=int, help="number of events to generate (overrides env)", default=None)
    parser.add_argument("--date", type=str, help="target date (YYYY-MM-DD) for file paths", default=None)
    parser.add_argument("--batch-size", type=int, help="events per batch (overrides env)", default=None)
    return parser.parse_args()

def main():
    args = parse_args()
    cfg = Config

    setup_logging(cfg.LOG_LEVEL)
    logger = logging.getLogger("main")

    num_events = args.events or cfg.GENERATOR_NUM_EVENTS
    batch_size = args.batch_size or cfg.GENERATOR_BATCH_SIZE
    target_date = args.date or datetime.utcnow().strftime("%Y-%m-%d")

    logger.info("Starting generator: events=%d batch_size=%d date=%s", num_events, batch_size, target_date)

    gen = ClickstreamGenerator(
        num_users=cfg.GENERATOR_UNIQUE_USERS,
        num_pages=cfg.GENERATOR_UNIQUE_PAGES,
        num_products=cfg.GENERATOR_UNIQUE_PRODUCTS,
        p_pageview=cfg.GENERATOR_P_PAGEVIEW,
        p_click=cfg.GENERATOR_P_CLICK,
        p_add_to_cart=cfg.GENERATOR_P_ADD_TO_CART,
        p_purchase=cfg.GENERATOR_P_PURCHASE,
        session_timeout_minutes=cfg.GENERATOR_SESSION_TIMEOUT_MINUTES,
    )

    uploader = GCSUploader(project=cfg.GCP_PROJECT_ID, bucket_name=cfg.BUCKET_NAME, prefix=cfg.GCS_PATH_PREFIX)

    events_iter = gen.generate(num_events)
    batch = []
    batch_index = 1
    total_sent = 0
    for ev in events_iter:
        batch.append(ev)
        if len(batch) >= batch_size:
            logger.info("Uploading batch %d with %d events", batch_index, len(batch))
            ok = uploader.upload_records_batch(batch, target_date, batch_index)
            if not ok:
                logger.error("Upload failed for batch %d", batch_index)
            total_sent += len(batch)
            batch = []
            batch_index += 1

    # remaining
    if batch:
        logger.info("Uploading final batch %d with %d events", batch_index, len(batch))
        uploader.upload_records_batch(batch, target_date, batch_index)
        total_sent += len(batch)

    logger.info("Finished. Total events generated and uploaded: %d", total_sent)

if __name__ == "__main__":
    main()
