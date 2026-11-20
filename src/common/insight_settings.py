import json
import os
from dataclasses import dataclass

from common.paths import SETTINGS_PATH


@dataclass(frozen=True)
class InsightSettings:
    base_url: str = ""
    api_key: str = ""

    @property
    def is_complete(self) -> bool:
        return bool(self.base_url.strip()) and bool(self.api_key.strip())


class InsightSettingsStore:
    """Reads/writes Documents/insight_settings.json (two plain string fields)."""

    def __init__(self, path: str = SETTINGS_PATH):
        self.path = path

    def load(self) -> InsightSettings:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return InsightSettings()
        if not isinstance(data, dict):
            return InsightSettings()
        base_url = data.get("baseUrl")
        api_key = data.get("apiKey")
        return InsightSettings(
            base_url=base_url if isinstance(base_url, str) else "",
            api_key=api_key if isinstance(api_key, str) else "",
        )

    def save(self, settings: InsightSettings) -> None:
        """Raises OSError on failure (caller shows the modal failure dialog)."""
        tmp_path = self.path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump({"baseUrl": settings.base_url, "apiKey": settings.api_key}, f)
        os.replace(tmp_path, self.path)
