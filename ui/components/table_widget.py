from PyQt6.QtWidgets import QPushButton
from models.table import TableStatus


class TableWidget(QPushButton):

    def __init__(self, table):
        super().__init__()

        self.table = table

        self.setFixedSize(140, 100)

        self.refresh()

    def refresh(self):

        self.setText(
            f"{self.table.name}\n{self.table.status.value}"
        )

        if self.table.status == TableStatus.EMPTY:

            self.setStyleSheet("""
                QPushButton{
                    background:white;
                    border:2px solid #ccc;
                    border-radius:10px;
                    font-size:16px;
                }
            """)

        else:

            self.setStyleSheet("""
                QPushButton{
                    background:#4CAF50;
                    color:white;
                    border:none;
                    border-radius:10px;
                    font-size:16px;
                }
            """)