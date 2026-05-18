from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QComboBox
)


class PaymentDialog(QDialog):

    def __init__(self, total_amount):

        super().__init__()

        self.selected_method = "CASH"

        self.setWindowTitle("Payment")

        layout = QVBoxLayout()

        layout.addWidget(
            QLabel(f"Total: {total_amount:,}₫")
        )

        self.combo = QComboBox()

        self.combo.addItems([
            "CASH",
            "BANKING",
            "CARD"
        ])

        layout.addWidget(self.combo)

        pay_btn = QPushButton("Confirm Payment")

        pay_btn.clicked.connect(self.accept)

        layout.addWidget(pay_btn)

        self.setLayout(layout)

    def get_method(self):
        return self.combo.currentText()