class DashboardModel:
    def __init__(self):
        self.response: dict | None = None   # latest /accounts body in hand (cached or fresh)
        self.cached_at: str | None = None   # ISO timestamp of last successful fetch
        self.refresh_error: str | None = None
        self.sync_notice: str | None = None  # "sync still running" inline notice
        self.settings_missing: bool = False
