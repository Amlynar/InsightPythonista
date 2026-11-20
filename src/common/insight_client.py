import logging

from framework.network.home_lab_session import PYIHomeLabSession

log = logging.getLogger("insight")

REQUEST_TIMEOUT_SECONDS = 15


class InsightFetchError(Exception):
    pass


class InsightClient:
    """GET {baseUrl}/api/v1/accounts via the shared home-lab session.

    Any exception raised here (including PYIHomeLabSession's CA-cert
    RuntimeError) means "treat this fetch as failed".
    """

    def fetch_accounts(self, base_url: str, api_key: str) -> dict:
        url = base_url.strip().rstrip("/") + "/api/v1/accounts"
        session = PYIHomeLabSession()
        response = session.get(
            url,
            headers={"X-API-Key": api_key.strip()},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if not response.ok:
            log.warning("GET %s -> %s: %.500s", url, response.status_code, response.text)
            raise InsightFetchError(f"HTTP {response.status_code}")
        try:
            data = response.json()
        except ValueError as e:
            raise InsightFetchError("Invalid JSON response") from e
        if not isinstance(data, dict) or not isinstance(data.get("accounts"), list):
            raise InsightFetchError("Unexpected response shape")
        return data
