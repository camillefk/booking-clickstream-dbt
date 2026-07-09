import logging
import tempfile
import json
import os
import time
from google.cloud import storage
from typing import List, Dict

logger = logging.getLogger(__name__)

class GCSUploader:
    def __init__(self, project: str, bucket_name: str, prefix: str = "raw/clickstream"):
        self.project = project
        self.bucket_name = bucket_name
        self.prefix = prefix.rstrip("/")
        self.client = storage.Client(project=self.project)
        self.bucket = self.client.bucket(self.bucket_name)
    
    def _upload_file_with_retries(self, local_path: str, dest_blob_name: str, max_retries: int = 5):
        backoff = 1
        for attempt in range(1, max_retries + 1):
            try:
                blob = self.bucket.blob(dest_blob_name)
                blob.upload_from_filename(local_path)
                logger.info("Uploaded %s to gs://%s/%s", local_path, self.bucket_name, dest_blob_name)
                return True
            except Exception as e:
                logger.warning("Upload attempt %d failed: %s", attempt, e)
                time.sleep(backoff)
                backoff *= 2
        logger.error("Failed to upload %s after %d attempts", local_path, max_retries)
        return False

    def upload_records_batch(self, records: List[Dict], target_date: str, batch_index: int) -> bool:
        """
        Writes records to a temp NDJSON file and uploads to GCS.
        path: {prefix}/{YYYY-MM-DD}/events_batch_{batch_index:03d}.ndjson
        """
        prefix_path = f"{self.prefix}/{target_date}"
        dest_blob_name = f"{prefix_path}/events_batch_{batch_index:03d}.ndjson"

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ndjson") as tmp:
            tmp_path = tmp.name
            for rec in records:
                tmp.write(json.dumps(rec, ensure_ascii=False))
                tmp.write("\n")
        try:
            success = self._upload_file_with_retries(tmp_path, dest_blob_name)
            return success
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
