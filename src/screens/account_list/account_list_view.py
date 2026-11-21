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
        content = AccountRowContent(row, self.theme)
        content.frame = (0, 0, self.table.width, ROW_HEIGHT)
        content.flex = 'WH'
        cell.content_view.add_subview(content)
        return cell


class AccountRowContent(ui.View):
    """Row content that lays itself out from its *current* width.

    Cells are created before the table has its final size and survive
    rotation, so frames must be recomputed in layout(), not at creation.
    """

    def __init__(self, row, theme):
        super().__init__()
        self.background_color = theme.view_background_color

        self.title = ui.Label()
        self.title.font = ('<system>', 16)
        self.title.text = row.title
        self.title.line_break_mode = ui.LB_TRUNCATE_TAIL

        self.balance = ui.Label()
        self.balance.font = ('<system-bold>', 16)
        self.balance.alignment = ui.ALIGN_RIGHT
        self.balance.text = row.balance_text
        self.balance.adjusts_font_size_to_fit = True

        self.tag = None
        if row.tag_text:
            self.tag = ui.Label()
            self.tag.text = row.tag_text
            if row.tag_kind == TAG_REAUTH:
                self.tag.font = ('<system-bold>', 13)
                self.tag.text_color = BANNER_WARNING_TEXT
            else:
                self.tag.font = ('<system>', 13)
                self.tag.text_color = theme.secondary_text_color
            self.add_subview(self.tag)

        self.add_subview(self.title)
        self.add_subview(self.balance)

    def layout(self):
        pad = 16
        w = self.width
        self.balance.frame = (w - pad - BALANCE_WIDTH, 8, BALANCE_WIDTH, 24)
        self.title.frame = (pad, 8, max(w - pad * 3 - BALANCE_WIDTH, 0), 24)
        if self.tag:
            self.tag.frame = (pad, 36, max(w - pad * 2, 0), 18)
