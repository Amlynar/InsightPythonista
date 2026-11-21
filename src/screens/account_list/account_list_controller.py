from injector import inject

from common.account_rows import build_rows
from common.formatting import format_money
from common.insight_totals import CASH, LIABILITY, compute_totals
from framework.mvc.controller import PYIController
from framework.style.theme import PYITheme
from screens.account_list.account_list_model import AccountListModel
from screens.account_list.account_list_view import AccountListView

_LABELS = {
    CASH: ("Cash Accounts", "Total Cash"),
    LIABILITY: ("Liability Accounts", "Total Liability"),
}


class AccountListController(PYIController):
    """Read-only list of the accounts behind a Dashboard total.

    Also acts as the table's data source. Built from a snapshot passed in via
    the route; makes no network calls.
    """

    @inject
    def __init__(self, model: AccountListModel, view: AccountListView, theme: PYITheme):
        super().__init__()
        self.model = model
        self.view = view
        self.theme = theme
        self.view.init_root_view(data_source=self)

    def configure(self, category: str, response: dict):
        title, total_label = _LABELS[category]
        totals = compute_totals(response.get("accounts"))
        total = totals.total_cash if category == CASH else totals.total_liability
        self.model.title = title
        self.view.name = title
        self.model.header = f"{total_label}: {format_money(total)}"
        self.model.rows = build_rows(response, category)

    def on_screen_loaded(self):
        self.view.display_content()
        self.view.render(header=self.model.header, has_rows=bool(self.model.rows))

    # --- ui.TableView data source ---------------------------------------

    def tableview_number_of_sections(self, tableview):
        return 1

    def tableview_number_of_rows(self, tableview, section):
        return len(self.model.rows)

    def tableview_cell_for_row(self, tableview, section, row):
        return self.view.make_row_cell(self.model.rows[row])

