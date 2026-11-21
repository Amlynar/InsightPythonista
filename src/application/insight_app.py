from injector import Injector

from core.app_module import AppModule
from framework.application.app import PYIApp
from framework.mvc.controller import PYIController
from framework.navigation.navigator import PYIRoute
from framework.style.theme import PYITheme
from navigation.routes import AccountListScreenRoute, DashboardScreenRoute, SettingsScreenRoute
from screens.account_list.account_list_controller import AccountListController

from screens.dashboard.dashboard_controller import DashboardController
from screens.settings.settings_controller import SettingsController


class InsightApp(PYIApp):

    def __init__(self):
        super().__init__()
        self.injector = Injector(AppModule())

    def run(self):
        theme = self.injector.get(PYITheme)
        self.present_intial_route(DashboardScreenRoute(), theme)

    def map_route_to_controller(self, route: PYIRoute) -> PYIController:
        match route:
            case DashboardScreenRoute():
                return self.injector.get(DashboardController)
            case SettingsScreenRoute():
                return self.injector.get(SettingsController)
            case AccountListScreenRoute():
                controller = self.injector.get(AccountListController)
                controller.configure(route.category, route.response)
                return controller
            case _:
                raise ValueError(f"Unknown route: {route}")
