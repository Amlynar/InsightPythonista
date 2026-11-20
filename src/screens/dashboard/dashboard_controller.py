from decimal import ROUND_HALF_UP, Decimal

import ui
from injector import inject

from common.insight_cache import InsightCache
from common.insight_client import InsightClient
from common.insight_settings import InsightSettingsStore
from common.insight_totals import compute_totals
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


class DashboardController(PYIController):

    @inject
    def __init__(self, model: DashboardModel, view: DashboardView, theme: PYITheme,
                 settings_store: InsightSettingsStore, cache: InsightCache,
                 client: InsightClient):
        super().__init__()
        self.model = model
        self.view = view
        self.theme = theme
        self.settings_store = settings_store
        self.cache = cache
        self.client = client

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

    @ui.in_background
    def refresh(self):
        settings = self.settings_store.load()
        if not settings.is_complete:
            self.model.settings_missing = True
            self.model.refresh_error = None
            self.render()
            return

        self.model.settings_missing = False
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
                             reauth_text=None, empty_text=empty)
            return

        totals = compute_totals(response.get("accounts"))
        self.view.render(
            net=format_money(totals.net_position),
            cash=format_money(totals.total_cash),
            liability=format_money(totals.total_liability),
            last_updated=f"Last updated: {relative_time(self.model.cached_at)}",
            refresh_error=self.model.refresh_error,
            reauth_text=self._reauth_text(response),
            empty_text=None,
        )

    @staticmethod
    def _reauth_text(response: dict) -> str | None:
        if not response.get("hasStaleData"):
            return None
        names = []
        for link in response.get("linksNeedingReauth") or []:
            name = link.get("institutionName") or "An institution"
            if name not in names:
                names.append(name)
        if not names:
            return "Some accounts need reauthorization \u2014 totals may be out of date"
        if len(names) == 1:
            subject, verb = names[0], "needs"
        else:
            subject, verb = ", ".join(names[:-1]) + " and " + names[-1], "need"
        return f"{subject} {verb} reauthorization \u2014 totals may be out of date"
