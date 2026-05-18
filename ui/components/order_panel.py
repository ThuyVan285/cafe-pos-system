from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget
)

from utils.formatter import format_currency


class OrderPanel(QWidget):

    def __init__(self):

        super().__init__()

        self.layout = QVBoxLayout()

        self.title = QLabel("Current Order")

        self.list_widget = QListWidget()

        self.total_label = QLabel("Total: 0₫")

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.total_label)

        self.setLayout(self.layout)

    def load_order(self, order):

        self.list_widget.clear()

        if not order:
            return

        for item in order.items:

            self.list_widget.addItem(
                f"{item.product_name} x{item.quantity}"
            )

        self.total_label.setText(
            f"Total: {format_currency(order.subtotal)}"
        )