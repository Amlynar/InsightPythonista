import logging
from dataclasses import dataclass

from framework.network.home_lab_session import PYIHomeLabSession

log = logging.getLogger("insight")

REQUEST_TIMEOUT_SECONDS = 15
SYNC_RUNNING = "RUNNING"


class InsightFetchError(Exception):
    pass


@dataclass(frozen=True)
class SyncStartResult:
    run_id: str | None
    status: str | None
    joined: bool
    skipped_reason: str | None

    @property
    def needs_polling(self) -> bool:
        """True for 202 (new or joined run); False for the 200 SYNCED_RECENTLY skip."""
        return self.skipped_reason is None and self.status == SYNC_RUNNING


class InsightClient:
    """Talks to InsightBE via the shared home-lab session.

    Settings are passed in per call (read fresh from disk by the caller),
    so nothing is cached here. Any exception raised means "treat as failed",
    including PYIHomeLabSession's CA-cert RuntimeError.
    """

    def __init__(self):
        # Explicit ctor: Injector can't inspect object.__init__ on Pythonista.
        pass

    def fetch_accounts(self, base_url: str, api_key: str) -> dict:
        data = self._request("GET", base_url, api_key, "/api/v1/accounts")
        if not isinstance(data.get("accounts"), list):
            raise InsightFetchError("Unexpected response shape")
        return data

    def start_sync(self, base_url: str, api_key: str) -> SyncStartResult:
        data = self._request("POST", base_url, api_key, "/api/v1/sync")
        return SyncStartResult(
            run_id=data.get("runId"),
            status=data.get("status"),
            joined=bool(data.get("joined")),
            skipped_reason=data.get("skippedReason"),
        )

    def get_sync_status(self, base_url: str, api_key: str, run_id: str | None) -> str | None:
        params = {"runId": run_id} if run_id else None
        data = self._request("GET", base_url, api_key, "/api/v1/sync/status", params=params)
        return data.get("status")

    def _request(self, method, base_url, api_key, path, params=None) -> dict:
        url = base_url.strip().rstrip("/") + path
        session = PYIHomeLabSession()
        response = session.request(
            method,
            url,
            headers={"X-API-Key": api_key.strip()},
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if not response.ok:
            log.warning("%s %s -> %s: %.500s", method, url, response.status_code, response.text)
            raise InsightFetchError(f"HTTP {response.status_code}")
        try:
            data = response.json()
        except ValueError as e:
            raise InsightFetchError("Invalid JSON response") from e
        if not isinstance(data, dict):
            raise InsightFetchError("Unexpected response shape")
        return data
