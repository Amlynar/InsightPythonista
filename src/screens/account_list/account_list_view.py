import ui
from injector import inject

from common.account_rows import TAG_REAUTH
from common.palette import BANNER_WARNING_TEXT
from framework.mvc.screen import PYIScreen
from framework.style.style_label import PYILabelStyle
from framework.style.style_table_view import PYITableViewStyle
from framework.style.style_table_view_cell import PYITableViewCellStyle
from framework.style.theme import PYITheme

ROW_HEIGHT = 64


class AccountListView(PYIScreen):
    @inject
    def __init__(self, theme: PYITheme):
        super().__init__(theme=theme)
        self.theme = theme
        self._last_table_width = None

    def layout(self):
        super().layout()
        if not hasattr(self, 'header_label'):
            return
        pad = 16
        width = self.width - (pad * 2)
        self.header_label.frame = (pad, pad, width, 30)
        top = pad + 30 + 8
        self.table.frame = (0, top, self.width, max(self.height - top, 0))
        self.empty_label.frame = (pad, top + pad, width, 40)
        # Rebuild cells whenever the width changes (rotation) so none keep a
        # stale width from before the table reached its final size.
        if self._last_table_width != self.table.width:
            self._last_table_width = self.table.width
            self.table.reload()

    def init_root_view(self, data_source):
        self.header_label = ui.Label()
        PYILabelStyle.title(self.header_label, self.theme)
        self.header_label.font = ('<system-bold>', 20)
        self.header_label.adjusts_font_size_to_fit = True

        self.table = ui.TableView()
        PYITableViewStyle.normal(self.table, self.theme)
        self.table.row_height = ROW_HEIGHT
        self.table.allows_selection = False
        self.table.data_source = data_source

        self.empty_label = ui.Label()
        PYILabelStyle.normal(self.empty_label, self.theme)
        self.empty_label.alignment = ui.ALIGN_CENTER
        self.empty_label.text = 'No accounts'
        self.empty_label.hidden = True

        for v in (self.header_label, self.table, self.empty_label):
            self.root_view.add_subview(v)

    def render(self, *, header, has_rows):

        self.header_label.text = header
        self.table.hidden = not has_rows
        self.empty_label.hidden = has_rows
        self.table.reload()

    def display_content(self):
        self.show_content(self.root_view)

    def make_row_cell(self, row):
        # Native 'value1' cell: title left, balance right. iOS lays this out
        # for the cell's real width, so there is no hand-computed geometry
        # that could go stale across rotation.
        cell = ui.TableViewCell('value1')
        PYITableViewCellStyle.subtitle(cell, self.theme)

        title = row.title
        if row.tag_text:
            title = f"{row.title}\n{row.tag_text}"
        cell.text_label.text = title
        cell.text_label.number_of_lines = 0
        cell.text_label.font = ('<system>', 16)
        if row.tag_kind == TAG_REAUTH:
            cell.text_label.text_color = BANNER_WARNING_TEXT

        cell.detail_text_label.text = row.balance_text
        cell.detail_text_label.font = ('<system-bold>', 16)
        return cell


