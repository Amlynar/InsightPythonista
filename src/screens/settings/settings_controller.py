import ui
from injector import inject

from common.insight_settings import InsightSettings, InsightSettingsStore
from framework.alert.alert_dialog import PYIAlert
from framework.mvc.controller import PYIController
from framework.style.theme import PYITheme
from screens.settings.settings_model import SettingsModel
from screens.settings.settings_view import SettingsView


class SettingsController(PYIController):

    @inject
    def __init__(self, model: SettingsModel, view: SettingsView, theme: PYITheme,
                 settings_store: InsightSettingsStore):
        super().__init__()
        self.model = model
        self.view = view
        self.theme = theme
        self.settings_store = settings_store

        self.view.init_root_view(data_source=self)

    def on_screen_loaded(self):
        settings = self.settings_store.load()
        self.view.base_url_field.text = settings.base_url
        self.view.api_key_field.text = settings.api_key
        self.view.display_content()

    @ui.in_background
    def save_action(self, sender):
        button, spinner = self.view.save_btn, self.view.save_spinner
        try:
            button.hidden = True
            spinner.start()
            self.settings_store.save(InsightSettings(
                base_url=self.view.base_url_field.text.strip(),
                api_key=self.view.api_key_field.text.strip(),
            ))
            self.view.status_label.text = "Saved. Relaunch the app to refresh."
        except Exception as e:
            # Rare + actionable: the one place the modal failure dialog is used.
            PYIAlert.simple_alert(title="Error", message=f"Unable to save settings: {e}")
        finally:
            spinner.stop()
            button.hidden = False
