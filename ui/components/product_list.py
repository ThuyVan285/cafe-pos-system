from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QScrollArea
)


class ProductList(QWidget):

    def __init__(self):

        super().__init__()

        self.layout = QVBoxLayout()

        self.setLayout(self.layout)

    def load_products(self, products, callback):

        while self.layout.count():

            child = self.layout.takeAt(0)

            if child.widget():
                child.widget().deleteLater()

        for product in products:

            btn = QPushButton(
                f"{product.name}\n{product.base_price:,}₫"
            )

            btn.setMinimumHeight(60)

            btn.clicked.connect(
                lambda checked=False, p=product: callback(p)
            )

            self.layout.addWidget(btn)