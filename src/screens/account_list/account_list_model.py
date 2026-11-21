from common.account_rows import AccountRow


class AccountListModel:
    def __init__(self):
        self.title: str = ""
        self.header: str = ""
        self.rows: list[AccountRow] = []
