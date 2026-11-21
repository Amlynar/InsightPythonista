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
BALANCE_WIDTH = 120


class AccountListView(PYIScreen):
    @inject
    def __init__(self, theme: PYITheme):
        super().__init__(theme=theme)
        self.theme = theme

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
        cell = ui.TableViewCell()
        PYITableViewCellStyle.subtitle(cell, self.theme)
        width = self.table.width
        pad = 16

        title = ui.Label()
        title.font = ('<system>', 16)
        title.text = row.title
        title.flex = 'W'
        title.frame = (pad, 8, width - pad * 2 - BALANCE_WIDTH, 24)

        balance = ui.Label()
        balance.font = ('<system-bold>', 16)
        balance.alignment = ui.ALIGN_RIGHT
        balance.text = row.balance_text
        balance.flex = 'L'
        balance.frame = (width - pad - BALANCE_WIDTH, 8, BALANCE_WIDTH, 24)

        cell.content_view.add_subview(title)
        cell.content_view.add_subview(balance)

        if row.tag_text:
            tag = ui.Label()
            tag.text = row.tag_text
            tag.flex = 'W'
            tag.frame = (pad, 36, width - pad * 2, 18)
            if row.tag_kind == TAG_REAUTH:
                tag.font = ('<system-bold>', 13)
                tag.text_color = BANNER_WARNING_TEXT
            else:
                tag.font = ('<system>', 13)
                tag.text_color = self.theme.secondary_text_color
            cell.content_view.add_subview(tag)
        return cell

