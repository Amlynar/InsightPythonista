import ui

PAD = 16
GAP = 8
BALANCE_FONT = ('<system-bold>', 16)


class AccountRowView(ui.View):
    """Name (and optional tag) on the left, balance pinned on the right.

    The balance is sized to its full text and never truncated; the name and
    tag take the remaining width and truncate with an ellipsis.
    """

    def __init__(self, title, balance_text, tag_text=None, tag_color=None,
                 text_color='black', **kwargs):
        super().__init__(**kwargs)
        self.flex = 'WH'
        self.balance_text = balance_text

        self.name_label = ui.Label()
        self.name_label.text = title
        self.name_label.font = ('<system>', 16)
        self.name_label.number_of_lines = 1
        self.name_label.line_break_mode = ui.LB_TRUNCATE_TAIL
        self.name_label.text_color = text_color
        self.add_subview(self.name_label)

        self.tag_label = None
        if tag_text:
            self.tag_label = ui.Label()
            self.tag_label.text = tag_text
            self.tag_label.font = ('<system>', 13)
            self.tag_label.number_of_lines = 1
            self.tag_label.line_break_mode = ui.LB_TRUNCATE_TAIL
            self.tag_label.text_color = tag_color
            self.add_subview(self.tag_label)

        self.balance_label = ui.Label()
        self.balance_label.text = balance_text
        self.balance_label.font = BALANCE_FONT
        self.balance_label.alignment = ui.ALIGN_RIGHT
        self.balance_label.number_of_lines = 1
        self.balance_label.text_color = text_color
        self.add_subview(self.balance_label)

    def layout(self):
        w, h = self.width, self.height
        bw = ui.measure_string(self.balance_text, font=BALANCE_FONT)[0]
        bw = min(bw + 2, max(w - PAD * 2, 0))
        self.balance_label.frame = (w - PAD - bw, 0, bw, h)
        nw = max(w - PAD * 2 - bw - GAP, 0)
        if self.tag_label:
            self.name_label.frame = (PAD, h / 2 - 20, nw, 22)
            self.tag_label.frame = (PAD, h / 2 + 2, nw, 18)
        else:
            self.name_label.frame = (PAD, 0, nw, h)
