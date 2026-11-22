import ui

PAD = 16
BALANCE_FONT = ('<system-bold>', 16)


class AccountRowView(ui.View):
    """Stacked lines: name, balance (right), institution (...mask), optional tag.

    Each label spans the full row width, so the balance is never truncated.
    """

    def __init__(self, title, balance_text, institution_text="", tag_text=None, tag_color=None,
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

        self.institution_label = ui.Label()
        self.institution_label.text = institution_text
        self.institution_label.font = ('<system>', 13)
        self.institution_label.number_of_lines = 1
        self.institution_label.line_break_mode = ui.LB_TRUNCATE_TAIL
        self.institution_label.text_color = text_color
        self.add_subview(self.institution_label)

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
        lw = max(w - PAD * 2, 0)
        heights = [20, 20, 16] + ([16] if self.tag_label else [])
        y = max((h - sum(heights)) / 2, 0)
        labels = [self.name_label, self.balance_label, self.institution_label]
        if self.tag_label:
            labels.append(self.tag_label)
        for label, lh in zip(labels, heights):
            label.frame = (PAD, y, lw, lh)
            y += lh
