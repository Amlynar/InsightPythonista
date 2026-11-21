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
        # The balance is sized to its full text and pinned right; the name
        # takes the remaining width and truncates with an ellipsis. Layout
        # runs in the row's own layout(), so it follows the real width.
        cell = ui.TableViewCell()
        PYITableViewCellStyle.subtitle(cell, self.theme)
        cell.text_label.text = ''
        cell.detail_text_label.text = ''

        balance_font = ('<system-bold>', 16)
        name = ui.Label()
        name.text = row.title
        name.font = ('<system>', 16)
        name.number_of_lines = 1
        name.line_break_mode = ui.LB_TRUNCATE_TAIL
        name.text_color = 'black'

        tag = None
        if row.tag_text:
            tag = ui.Label()
            tag.text = row.tag_text
            tag.font = ('<system>', 13)
            tag.number_of_lines = 1
            tag.line_break_mode = ui.LB_TRUNCATE_TAIL
            tag.text_color = (BANNER_WARNING_TEXT if row.tag_kind == TAG_REAUTH
                              else self.theme.secondary_text_color)

        balance = ui.Label()
        balance.text = row.balance_text
        balance.font = balance_font
        balance.alignment = ui.ALIGN_RIGHT
        balance.number_of_lines = 1
        balance.text_color = name.text_color

        container = ui.View()
        container.flex = 'WH'
        pad = 16
        gap = 8

        def do_layout(sender):
            w, h = sender.width, sender.height
            bw = ui.measure_string(row.balance_text, font=balance_font)[0]
            bw = min(bw + 2, max(w - pad * 2, 0))
            balance.frame = (w - pad - bw, 0, bw, h)
            nw = max(w - pad * 2 - bw - gap, 0)
            if tag:
                name.frame = (pad, h / 2 - 20, nw, 22)
                tag.frame = (pad, h / 2 + 2, nw, 18)
            else:
                name.frame = (pad, 0, nw, h)

        container.layout = lambda: do_layout(container)
        for v in (name, tag, balance):
            if v is not None:
                container.add_subview(v)
        container.frame = cell.content_view.bounds
        cell.content_view.add_subview(container)
        return cell


