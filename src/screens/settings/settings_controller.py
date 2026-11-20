import ui
from injector import inject

from common.insight_settings import InsightSettings, InsightSettingsStore
from common.settings_changed_notifier import SettingsChangedNotifier
from framework.alert.alert_dialog import PYIAlert
from framework.mvc.controller import PYIController
from framework.style.theme import PYITheme
from screens.settings.settings_model import SettingsModel
from screens.settings.settings_view import SettingsView


class SettingsController(PYIController):

    @inject
    def __init__(self, model: SettingsModel, view: SettingsView, theme: PYITheme,
                 settings_store: InsightSettingsStore, settings_notifier: SettingsChangedNotifier):
        super().__init__()
        self.model = model
        self.view = view
        self.theme = theme
        self.settings_store = settings_store
        self.settings_notifier = settings_notifier

        self.view.init_root_view(data_source=self)

    def on_screen_loaded(self):
        settings = self.settings_store.load()
        self.view.base_url_field.text = settings.base_url
        self.view.api_key_field.text = settings.api_key
        self.view.display_content()

    @ui.in_background
    def save_action(self, sender):
        button, spinner = self.view.save_btn, self.view.save_spinner
        saved = False
        try:
            button.hidden = True
            spinner.start()
            self.settings_store.save(InsightSettings(
                base_url=self.view.base_url_field.text.strip(),
                api_key=self.view.api_key_field.text.strip(),
            ))
            saved = True
        except Exception as e:
            # Rare + actionable: the one place the modal failure dialog is used.
            PYIAlert.simple_alert(title="Error", message=f"Unable to save settings: {e}")
        finally:
            spinner.stop()
            button.hidden = False

        if saved:
            # framework's navigator has no pop; use the view's own nav view.
            if self.view.navigation_view:
                self.view.navigation_view.pop_view()
            self.settings_notifier.notify()   # Dashboard refreshes with new values
