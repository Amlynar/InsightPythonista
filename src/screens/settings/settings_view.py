import ui
from injector import inject

from framework.mvc.screen import PYIScreen
from framework.style.style_button import PYIButtonStyle
from framework.style.style_label import PYILabelStyle
from framework.style.style_spinner import PYISpinnerStyle
from framework.style.theme import PYITheme


class SettingsView(PYIScreen):
    @inject
    def __init__(self, theme: PYITheme):
        super().__init__(theme=theme)
        self.theme = theme
        self.name = 'Settings'

    def layout(self):
        super().layout()
        if not hasattr(self, 'save_btn'):
            return

        pad = 16
        width = self.width - (pad * 2)
        field_height = 40

        top = pad
        self.base_url_header.frame = (pad, top, width, 20)
        self.base_url_field.frame = (pad, top + 24, width, field_height)
        top = self.base_url_field.y + field_height + pad

        self.api_key_header.frame = (pad, top, width, 20)
        self.api_key_field.frame = (pad, top + 24, width, field_height)
        top = self.api_key_field.y + field_height + pad

        self.save_btn.frame = (pad, top, width, 44)
        self.save_spinner.center = self.save_btn.center
        self.status_label.frame = (pad, top + 44 + 6, width, 36)

    def init_root_view(self, data_source):
        self.base_url_header = self._make_section_header('BASE URL')
        self.base_url_field = self._make_field('https://insight.home.arpa')
        self.base_url_field.keyboard_type = ui.KEYBOARD_URL

        self.api_key_header = self._make_section_header('API KEY')
        self.api_key_field = self._make_field('API key')
        self.api_key_field.secure = True

        self.save_btn = ui.Button(title='Save')
        PYIButtonStyle.prominent(self.save_btn, self.theme)
        self.save_btn.action = data_source.save_action

        self.save_spinner = ui.ActivityIndicator()
        PYISpinnerStyle.loading(self.save_spinner, self.theme)

        self.status_label = ui.Label()
        PYILabelStyle.caption(self.status_label, self.theme)

        for v in (
            self.base_url_header, self.base_url_field,
            self.api_key_header, self.api_key_field,
            self.save_btn, self.save_spinner, self.status_label,
        ):
            self.root_view.add_subview(v)

    def display_content(self):
        self.show_content(self.root_view)

    def _make_section_header(self, text):
        label = ui.Label()
        PYILabelStyle.section_header(label, self.theme)
        label.text = text
        return label

    def _make_field(self, placeholder):
        field = ui.TextField()
        field.placeholder = placeholder
        field.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
        field.autocorrection_type = False
        field.spellchecking_type = False
        field.clear_button_mode = 'while_editing'
        return field
