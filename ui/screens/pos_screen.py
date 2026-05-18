from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QGridLayout,
    QVBoxLayout,
    QMessageBox,
)

from database.db import get_session

from repositories.table_repository import TableRepository

from services.order_service import OrderService
from services.product_service import ProductService
from services.payment_service import PaymentService

from controllers.order_controller import OrderController
from controllers.product_controller import ProductController
from controllers.payment_controller import PaymentController

from ui.components.table_widget import TableWidget
from ui.components.product_list import ProductList
from ui.components.order_panel import OrderPanel

from ui.dialogs.payment_dialog import PaymentDialog


class PosScreen(QWidget):

    def __init__(self):

        super().__init__()

        self.session = get_session()

        self.table_repo = TableRepository(self.session)

        self.order_controller = OrderController(
            OrderService(self.session)
        )

        self.product_controller = ProductController(
            ProductService(self.session)
        )

        self.payment_controller = PaymentController(
            PaymentService(self.session)
        )

        self.current_order = None

        self.current_user_id = 1

        self.build_ui()

    def build_ui(self):

        main_layout = QHBoxLayout()

        # TABLES

        table_layout = QGridLayout()

        tables = self.table_repo.get_all()

        row = 0
        col = 0

        for table in tables:

            widget = TableWidget(table)

            widget.clicked.connect(
                lambda checked=False, t=table: self.select_table(t)
            )

            table_layout.addWidget(widget, row, col)

            col += 1

            if col >= 4:
                col = 0
                row += 1

        # PRODUCTS

        self.product_list = ProductList()

        products = self.product_controller.get_products()

        self.product_list.load_products(
            products,
            self.add_product
        )

        # ORDER PANEL

        self.order_panel = OrderPanel()

        # LAYOUT

        left = QWidget()
        left.setLayout(table_layout)

        main_layout.addWidget(left, 2)
        main_layout.addWidget(self.product_list, 2)
        main_layout.addWidget(self.order_panel, 1)

        self.setLayout(main_layout)

    def select_table(self, table):

        self.current_order = self.order_controller.create_or_get_order(
            table.id,
            self.current_user_id
        )

        self.order_panel.load_order(self.current_order)

    def add_product(self, product):

        if not self.current_order:

            QMessageBox.warning(
                self,
                "Warning",
                "Please select a table first"
            )

            return

        self.order_controller.add_product(
            self.current_order,
            product.id
        )

        self.current_order = self.order_controller._service.get_active_order(
            self.current_order.table_id
        )

        self.order_panel.load_order(self.current_order)