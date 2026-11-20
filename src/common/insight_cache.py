import json
import os

from common.paths import CACHE_PATH
from common.time_utils import utc_now_iso


class InsightCache:
    """Reads/writes Documents/insight_cache.json: {"cachedAt": ..., "response": {...}}."""

    def __init__(self, path: str = CACHE_PATH):
        self.path = path

    def read(self) -> dict | None:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return None
        if (
            not isinstance(data, dict)
            or not isinstance(data.get("response"), dict)
            or not isinstance(data.get("cachedAt"), str)
        ):
            return None
        return data

    def write(self, response: dict) -> dict:
        wrapped = {"cachedAt": utc_now_iso(), "response": response}
        tmp_path = self.path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(wrapped, f)
        os.replace(tmp_path, self.path)
        return wrapped
