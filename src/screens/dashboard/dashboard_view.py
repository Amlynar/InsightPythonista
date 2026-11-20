import ui
from injector import inject

from common.palette import (
    BANNER_ERROR_BACKGROUND, BANNER_ERROR_TEXT,
    BANNER_WARNING_BACKGROUND, BANNER_WARNING_TEXT,
    CARD_BACKGROUND, CASH_ACCENT, LIABILITY_ACCENT,
)
from framework.mvc.screen import PYIScreen
from framework.style.style_label import PYILabelStyle
from framework.style.style_spinner import PYISpinnerStyle
from framework.style.theme import PYITheme


class DashboardView(PYIScreen):
    @inject
    def __init__(self, theme: PYITheme):
        super().__init__(theme=theme)
        self.theme = theme
        self.name = 'Insight'

    def layout(self):
        super().layout()
        if not hasattr(self, 'net_card'):
            return

        pad = 16
        gap = 12
        width = self.width - (pad * 2)
        top = pad

        # Banners (only the visible ones take space)
        for banner in (self.refresh_banner, self.reauth_banner):
            if banner.hidden:
                continue
            banner.frame = (pad, top, width, 40)
            top += 40 + 8

        if self.empty_label.hidden is False:
            self.empty_label.frame = (pad, top + pad, width, 80)
            return

        self.net_card.frame = (pad, top, width, 130)
        top += 130 + gap

        half = (width - gap) / 2
        self.cash_card.frame = (pad, top, half, 90)
        self.liability_card.frame = (pad + half + gap, top, half, 90)
        top += 90 + gap

        status_height = 20
        self.last_updated_label.frame = (pad, top, width - 30, status_height)
        self.refresh_spinner.center = (self.width - pad - 10, top + status_height / 2)

    def init_root_view(self, data_source):
        self.net_card, self.net_title, self.net_value = self._make_card(
            'NET POSITION', self.theme.accent_color, value_size=40)
        self.cash_card, self.cash_title, self.cash_value = self._make_card(
            'TOTAL CASH', CASH_ACCENT, value_size=22)
        self.liability_card, self.liability_title, self.liability_value = self._make_card(
            'TOTAL LIABILITY', LIABILITY_ACCENT, value_size=22)

        self.last_updated_label = ui.Label()
        PYILabelStyle.caption(self.last_updated_label, self.theme)

        self.refresh_spinner = ui.ActivityIndicator()
        PYISpinnerStyle.loading(self.refresh_spinner, self.theme)

        self.refresh_banner = self._make_banner(BANNER_ERROR_BACKGROUND, BANNER_ERROR_TEXT)
        self.reauth_banner = self._make_banner(BANNER_WARNING_BACKGROUND, BANNER_WARNING_TEXT)

        self.empty_label = ui.Label()
        PYILabelStyle.normal(self.empty_label, self.theme)
        self.empty_label.alignment = ui.ALIGN_CENTER
        self.empty_label.hidden = True

        for v in (
            self.net_card, self.cash_card, self.liability_card,
            self.last_updated_label, self.refresh_spinner,
            self.refresh_banner, self.reauth_banner, self.empty_label,
        ):
            self.root_view.add_subview(v)

        self.settings_button_item = ui.ButtonItem(image=ui.Image.named('iob:gear_a_24'))
        self.settings_button_item.action = data_source.settings_action
        self.right_button_items = [self.settings_button_item]

    # --- rendering -------------------------------------------------------

    def render(self, *, net, cash, liability, last_updated, refresh_error,
               reauth_text, empty_text):
        """Any of net/cash/liability/last_updated may be None when there is no data."""
        has_data = empty_text is None
        for v in (self.net_card, self.cash_card, self.liability_card, self.last_updated_label):
            v.hidden = not has_data
        self.empty_label.hidden = has_data
        self.empty_label.text = empty_text or ''

        if has_data:
            self.net_value.text = net
            self.cash_value.text = cash
            self.liability_value.text = liability
            self.last_updated_label.text = last_updated

        self._set_banner(self.refresh_banner, refresh_error)
        self._set_banner(self.reauth_banner, reauth_text)
        self.layout()

    def display_content(self):
        self.show_content(self.root_view)

    def set_refreshing(self, refreshing: bool):
        if refreshing:
            self.refresh_spinner.start()
        else:
            self.refresh_spinner.stop()

    # --- builders --------------------------------------------------------

    def _set_banner(self, banner, text):
        banner.text = text or ''
        banner.hidden = not text

    def _make_banner(self, background, text_color):
        label = ui.Label()
        label.font = ('<system>', 13)
        label.number_of_lines = 0
        label.alignment = ui.ALIGN_CENTER
        label.background_color = background
        label.text_color = text_color
        label.corner_radius = 6
        label.hidden = True
        return label

    def _make_card(self, title, accent, value_size):
        card = ui.View()
        card.background_color = CARD_BACKGROUND
        card.corner_radius = 10
        card.border_width = 0

        title_label = ui.Label()
        PYILabelStyle.section_header(title_label, self.theme)
        title_label.background_color = CARD_BACKGROUND
        title_label.text = title
        title_label.text_color = accent
        title_label.flex = 'W'
        title_label.frame = (14, 12, 200, 18)

        value_label = ui.Label()
        value_label.background_color = CARD_BACKGROUND
        value_label.font = ('<system-bold>', value_size)
        value_label.text_color = accent
        value_label.adjusts_font_size_to_fit = True
        value_label.flex = 'WH'
        value_label.frame = (14, 34, 200, value_size + 14)

        card.add_subview(title_label)
        card.add_subview(value_label)
        return card, title_label, value_label
