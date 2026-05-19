# FILE: ui/screens/pos_screen.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QGridLayout,
    QTabWidget, QMessageBox, QScrollArea,
    QButtonGroup, QRadioButton, QHBoxLayout,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

from database.db import get_session
from repositories.table_repository import TableRepository
from repositories.product_repository import ProductRepository
from services.order_service import OrderService
from services.product_service import ProductService
from services.payment_service import PaymentService
from controllers.order_controller import OrderController
from controllers.product_controller import ProductController
from controllers.payment_controller import PaymentController
from ui.components.order_panel import OrderPanel
from models.table import TableStatus


class TableCard(QPushButton):
    """Card bàn giống hình mẫu"""

    def __init__(self, table, callback):
        super().__init__()
        self.table = table
        self.callback = callback
        self.setFixedSize(150, 110)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(lambda: callback(table))
        self.refresh()

    def refresh(self):
        is_using = self.table.status == TableStatus.USING

        # Icon bàn SVG-style bằng text
        icon = "🛋️" if self.table.table_type.value == "TAKE_AWAY" else "🪑"

        self.setText(f"{icon}\n{self.table.name}")
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))

        if is_using:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(
                        x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4A9FE8, stop:1 #2176C7
                    );
                    color: white;
                    border: none;
                    border-radius: 18px;
                    font-size: 13px;
                    font-weight: bold;
                    padding-bottom: 8px;
                }
                QPushButton:hover {
                    background: qlineargradient(
                        x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5AAFF8, stop:1 #3186D7
                    );
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: white;
                    color: #2C3E50;
                    border: 2.5px solid #B0C8E8;
                    border-radius: 18px;
                    font-size: 13px;
                    font-weight: bold;
                    padding-bottom: 8px;
                }
                QPushButton:hover {
                    background: #EBF4FF;
                    border: 2.5px solid #4A9FE8;
                }
            """)


class PosScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.session = get_session()
        self.table_repo = TableRepository(self.session)
        self.product_repo = ProductRepository(self.session)
        self.order_service = OrderService(self.session)
        self.order_controller = OrderController(self.order_service)
        self.product_controller = ProductController(ProductService(self.session))
        self.payment_controller = PaymentController(PaymentService(self.session))

        self.current_order = None
        self.current_table = None
        self.current_user_id = 1
        self.table_cards = {}       # table.id -> TableCard
        self.all_tables = []
        self.filter_mode = "all"    # all | using | empty

        self.build_ui()

    # ─────────────────────────────────────────────────────────
    def build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.left_tabs = QTabWidget()
        self.left_tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #F0F4FA; }
            QTabBar::tab {
                padding: 10px 28px;
                font-size: 13px;
                font-weight: bold;
                color: #555;
                background: #E0E8F0;
                border-radius: 0px;
            }
            QTabBar::tab:selected {
                background: #2176C7;
                color: white;
            }
        """)

        self.left_tabs.addTab(self._build_table_tab(), "🪑  Phòng bàn")
        self.left_tabs.addTab(self._build_menu_tab(),  "🍹  Thực đơn")

        # Right panel
        right_widget = QWidget()
        right_widget.setFixedWidth(320)
        right_widget.setStyleSheet("background: white; border-left: 1px solid #DDE3EC;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        order_header = QLabel("  🧾  Hóa đơn")
        order_header.setFixedHeight(48)
        order_header.setStyleSheet("""
            background: #2176C7;
            color: white;
            font-size: 15px;
            font-weight: bold;
        """)
        right_layout.addWidget(order_header)

        self.order_panel = OrderPanel()
        right_layout.addWidget(self.order_panel)

        main_layout.addWidget(self.left_tabs, 1)
        main_layout.addWidget(right_widget)

    # ── TABLE TAB ────────────────────────────────────────────
    def _build_table_tab(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: #F0F4FA;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # Filter bar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(12)

        self.filter_group = QButtonGroup(self)

        self.rb_all   = self._make_radio("Tất cả",   "all")
        self.rb_using = self._make_radio("Sử dụng",  "using")
        self.rb_empty = self._make_radio("Còn trống","empty")
        self.rb_all.setChecked(True)

        self.filter_group.addButton(self.rb_all)
        self.filter_group.addButton(self.rb_using)
        self.filter_group.addButton(self.rb_empty)

        filter_bar.addWidget(self.rb_all)
        filter_bar.addWidget(self.rb_using)
        filter_bar.addWidget(self.rb_empty)
        filter_bar.addStretch()

        layout.addLayout(filter_bar)

        # Scroll + grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background: transparent;")
        self.table_grid = QGridLayout(self.grid_widget)
        self.table_grid.setSpacing(12)
        self.table_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)

        self._load_tables()
        return container

    def _make_radio(self, text, mode) -> QRadioButton:
        rb = QRadioButton(text)
        rb.setStyleSheet("""
            QRadioButton {
                font-size: 13px;
                font-weight: bold;
                color: #2C3E50;
                spacing: 6px;
            }
            QRadioButton::indicator {
                width: 16px; height: 16px;
            }
        """)
        rb.toggled.connect(lambda checked, m=mode: self._on_filter(m) if checked else None)
        return rb

    def _on_filter(self, mode: str):
        self.filter_mode = mode
        if hasattr(self, 'table_grid'):  # ✅ chỉ render khi grid đã tồn tại
            self._render_table_grid()
    def _load_tables(self):
        self.all_tables = self.table_repo.get_all()
        self._render_table_grid()

    def _render_table_grid(self):
        # Xóa grid cũ
        while self.table_grid.count():
            item = self.table_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.table_cards.clear()

        # Filter
        if self.filter_mode == "using":
            tables = [t for t in self.all_tables if t.status == TableStatus.USING]
        elif self.filter_mode == "empty":
            tables = [t for t in self.all_tables if t.status == TableStatus.EMPTY]
        else:
            tables = self.all_tables

        # Cập nhật label radio
        all_count   = len(self.all_tables)
        using_count = sum(1 for t in self.all_tables if t.status == TableStatus.USING)
        empty_count = all_count - using_count
        self.rb_all.setText(f"Tất cả ({all_count})")
        self.rb_using.setText(f"Sử dụng ({using_count})")
        self.rb_empty.setText(f"Còn trống ({empty_count})")

        COLS = 5
        for idx, table in enumerate(tables):
            card = TableCard(table, self.select_table)
            self.table_cards[table.id] = card
            self.table_grid.addWidget(card, idx // COLS, idx % COLS)

    # ── MENU TAB ─────────────────────────────────────────────
    def _build_menu_tab(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: #F0F4FA;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        self.menu_title = QLabel("⬅  Vui lòng chọn bàn trước")
        self.menu_title.setStyleSheet(
            "font-size:15px; font-weight:bold; color:#2176C7;"
        )
        layout.addWidget(self.menu_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        grid_widget = QWidget()
        grid_widget.setStyleSheet("background: transparent;")
        self.product_grid = QGridLayout(grid_widget)
        self.product_grid.setSpacing(10)
        self.product_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        scroll.setWidget(grid_widget)
        layout.addWidget(scroll)
        return container

    def _load_product_grid(self):
        while self.product_grid.count():
            item = self.product_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        products = self.product_repo.get_all_active()
        COLS = 4
        for idx, product in enumerate(products):
            btn = self._make_product_card(product)
            self.product_grid.addWidget(btn, idx // COLS, idx % COLS)

    def _make_product_card(self, product) -> QPushButton:
        if product.has_size and product.sizes:
            min_delta = min(s.price_delta for s in product.sizes)
            display_price = product.base_price + min_delta
            price_text = f"từ {display_price:,}₫"
        else:
            price_text = f"{product.base_price:,}₫"

        btn = QPushButton(f"{product.name}\n{price_text}")
        btn.setFixedSize(160, 80)
        btn.setFont(QFont("Segoe UI", 11))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: white;
                color: #2C3E50;
                border: 1.5px solid #C8D8EE;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                padding: 6px;
            }
            QPushButton:hover {
                background: #EBF4FF;
                border: 2px solid #2176C7;
                color: #2176C7;
            }
        """)
        btn.clicked.connect(lambda checked, p=product: self.add_product(p))
        return btn

    # ── ACTIONS ──────────────────────────────────────────────
    def select_table(self, table):
        self.current_table = table
        self.current_order = self.order_controller.create_or_get_order(
            table.id, self.current_user_id
        )
        self.order_panel.load_order(self.current_order)
        self.menu_title.setText(f"🍹  Thực đơn  —  {table.name}")
        self._load_product_grid()
        self.left_tabs.setCurrentIndex(1)
        self._refresh_table_cards()

    def add_product(self, product):
        if not self.current_order:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn bàn trước!")
            return
        self.order_controller.add_product(self.current_order, product.id)
        self.current_order = self.order_service.get_active_order(self.current_table.id)
        self.order_panel.load_order(self.current_order)

    def _refresh_table_cards(self):
        self.all_tables = self.table_repo.get_all()
        self._render_table_grid()