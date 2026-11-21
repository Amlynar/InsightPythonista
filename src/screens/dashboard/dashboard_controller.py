import threading
import time
from decimal import ROUND_HALF_UP, Decimal

import ui
from injector import inject

from common.insight_cache import InsightCache
from common.insight_client import SYNC_RUNNING, InsightClient
from common.insight_settings import InsightSettingsStore
from common.insight_totals import compute_totals
from common.settings_changed_notifier import SettingsChangedNotifier
from common.time_utils import relative_time
from framework.mvc.controller import PYIController
from framework.style.theme import PYITheme
from navigation.routes import SettingsScreenRoute
from screens.dashboard.dashboard_model import DashboardModel
from screens.dashboard.dashboard_view import DashboardView


def format_money(value: Decimal) -> str:
    cents = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sign = "-" if cents < 0 else ""
    return f"{sign}${abs(cents):,.2f}"


SYNC_POLL_INTERVAL_SECONDS = 2
SYNC_TIMEOUT_SECONDS = 60


class DashboardController(PYIController):

    @inject
    def __init__(self, model: DashboardModel, view: DashboardView, theme: PYITheme,
                 settings_store: InsightSettingsStore, cache: InsightCache,
                 client: InsightClient, settings_notifier: SettingsChangedNotifier):
        super().__init__()
        self.model = model
        self.view = view
        self.theme = theme
        self.settings_store = settings_store
        self.cache = cache
        self.client = client

        # One network operation at a time; a request that arrives while busy
        # (e.g. Settings save) is re-run once the current one finishes.
        self._lock = threading.Lock()
        self._rerun_refresh = False

        settings_notifier.subscribe(self.refresh)
        self.view.init_root_view(data_source=self)

    def on_screen_loaded(self):
        # Cache-first: render synchronously, never a blank/loading screen.
        cached = self.cache.read()
        if cached:
            self.model.response = cached["response"]
            self.model.cached_at = cached["cachedAt"]
        self.view.display_content()
        self.render()
        self.refresh()

    def settings_action(self, sender):
        self.navigate(SettingsScreenRoute())

    def refresh_action(self, sender):
        self.refresh()

    # --- Refresh (GET /accounts) ----------------------------------------

    @ui.in_background
    def refresh(self):
        if not self._lock.acquire(blocking=False):
            self._rerun_refresh = True
            return
        try:
            self._refresh_work()
        finally:
            self._lock.release()
        if self._rerun_refresh:
            self._rerun_refresh = False
            self.refresh()

    def _refresh_work(self):
        """Fetch /accounts, update model + cache. Caller must hold the lock."""
        settings = self.settings_store.load()   # read fresh on every request
        if not settings.is_complete:
            self.model.settings_missing = True
            self.model.refresh_error = None
            self.render()
            return

        self.model.settings_missing = False
        self.model.sync_notice = None
        try:
            self.view.set_refreshing(True)
            response = self.client.fetch_accounts(settings.base_url, settings.api_key)
            wrapped = self.cache.write(response)
            self.model.response = wrapped["response"]
            self.model.cached_at = wrapped["cachedAt"]
            self.model.refresh_error = None
        except Exception as e:
            # Routine/expected: inline banner, not the modal dialog.
            self.model.refresh_error = self._refresh_error_text(e)
        finally:
            self.view.set_refreshing(False)
            self.render()

    # --- Sync Now (POST /sync, poll /sync/status, then Refresh) ---------

    @ui.in_background
    def sync_now_action(self, sender):
        if not self._lock.acquire(blocking=False):
            return
        try:
            self.view.set_syncing(True)
            self._sync_work()
        finally:
            self.view.set_syncing(False)
            self._lock.release()

    def _sync_work(self):
        settings = self.settings_store.load()
        if not settings.is_complete:
            self.model.settings_missing = True
            self.model.refresh_error = None
            self.render()
            return

        self.model.settings_missing = False
        self.model.sync_notice = None
        self.model.refresh_error = None
        self.render()

        started = time.monotonic()
        try:
            result = self.client.start_sync(settings.base_url, settings.api_key)
            if result.needs_polling:
                # Covers both a fresh 202 and a joined 202: poll the same way.
                while True:
                    if time.monotonic() - started >= SYNC_TIMEOUT_SECONDS:
                        self.model.sync_notice = (
                            "Sync still running in the background \u2014 "
                            "refresh later to see updated numbers.")
                        self.render()
                        return
                    time.sleep(SYNC_POLL_INTERVAL_SECONDS)
                    status = self.client.get_sync_status(
                        settings.base_url, settings.api_key, result.run_id)
                    if status != SYNC_RUNNING:
                        break
        except Exception as e:
            self.model.refresh_error = self._refresh_error_text(e)
            self.render()
            return

        # Finished (any non-RUNNING status) or skipped (SYNCED_RECENTLY):
        # plain Refresh. PARTIAL/FAILED is surfaced by the reauth banner logic.
        self._refresh_work()

    def _refresh_error_text(self, error: Exception) -> str:
        if isinstance(error, RuntimeError):
            # e.g. PYIHomeLabSession's "CA cert not downloaded" - surface verbatim.
            return str(error)
        if self.model.cached_at:
            return f"Couldn't refresh \u2014 showing data from {relative_time(self.model.cached_at)}"
        return "Couldn't refresh"
    def render(self):
        response = self.model.response
        if response is None:
            if self.model.settings_missing:
                empty = "No data yet \u2014 open Settings (gear icon) to enter your Base URL and API key"
            else:
                empty = "No data yet \u2014 check Settings and your connection"
            self.view.render(net=None, cash=None, liability=None, last_updated=None,
                             refresh_error=self.model.refresh_error,
                             sync_notice=self.model.sync_notice,
                             reauth_text=None, empty_text=empty)
            return

        accounts = response.get("accounts")
        if not accounts:
            # hasStaleData is false here, but that means "nothing flagged",
            # not "up to date" - show an empty state.
            self.view.render(net=None, cash=None, liability=None, last_updated=None,
                             refresh_error=self.model.refresh_error,
                             sync_notice=self.model.sync_notice,
                             reauth_text=None,
                             empty_text="No accounts yet \u2014 nothing has been imported")
            return

        totals = compute_totals(accounts)
        self.view.render(
            net=format_money(totals.net_position),
            cash=format_money(totals.total_cash),
            liability=format_money(totals.total_liability),
            last_updated=self._last_updated_text(response),
            refresh_error=self.model.refresh_error,
            sync_notice=self.model.sync_notice,
            reauth_text=self._stale_text(response),
            empty_text=None,
        )

    @staticmethod
    def _last_updated_text(response: dict) -> str:
        # asOf = newest fetchedAt across accounts (display only).
        as_of = response.get("asOf")
        if not as_of:
            return "No balance data yet"
        return f"Newest data: {relative_time(as_of)}"

    @staticmethod
    def _stale_text(response: dict) -> str | None:
        if not response.get("hasStaleData"):
            return None
        names = []
        for link in response.get("linksNeedingReauth") or []:
            name = link.get("institutionName") or "An institution"
            if name not in names:
                names.append(name)
        missing = sum(1 for a in response.get("accounts") or []
                      if a.get("balance") is None)

        parts = []
        if names:
            if len(names) == 1:
                subject, verb = names[0], "needs"
            else:
                subject, verb = ", ".join(names[:-1]) + " and " + names[-1], "need"
            parts.append(f"{subject} {verb} reauthorization")
        if missing:
            noun = "account has" if missing == 1 else "accounts have"
            parts.append(f"{missing} {noun} no data yet (not in totals)")
        if not parts:
            parts.append("Some accounts have old data")
        return "; ".join(parts) + " \u2014 totals may be out of date"

