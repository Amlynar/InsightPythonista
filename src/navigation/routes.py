from framework.navigation.navigator import PYIRoute


class DashboardScreenRoute(PYIRoute): pass

class SettingsScreenRoute(PYIRoute): pass


class AccountListScreenRoute(PYIRoute):
    """Drill-down into the accounts behind a total.

    Carries a snapshot of the /accounts response the dashboard was showing, so
    the list never needs its own fetch and agrees with the tapped number.
    """

    def __init__(self, category: str, response: dict):
        self.category = category
        self.response = response
