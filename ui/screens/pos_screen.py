# FILE: ui/screens/pos_screen.py

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QGridLayout, QMessageBox,
    QScrollArea, QButtonGroup, QRadioButton,
    QFrame, QLineEdit, QSizePolicy,
    QSplitter, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
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
from models.table import TableStatus


# =========================================================
# TABLE CARD
# =========================================================
class TableCard(QWidget):

    def __init__(self, table, callback):
        super().__init__()

        self.table = table

        self.setFixedHeight(74)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.btn = QPushButton()
        self.btn.setFixedHeight(46)

        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        self.btn.clicked.connect(
            lambda: callback(table)
        )

        self.lbl = QLabel(table.name)

        self.lbl.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.lbl.setFont(
            QFont("Segoe UI", 9)
        )

        layout.addWidget(self.btn)
        layout.addWidget(self.lbl)

        self.refresh()

    def refresh(self):

        is_using = (
                self.table.status == TableStatus.USING
        )

        is_takeaway = (
                "Away" in self.table.name or
                "away" in self.table.name
        )

        icon = "🛍️" if is_takeaway else ""

        self.btn.setText(icon)

        if is_using:

            self.btn.setStyleSheet("""
                QPushButton {
                    background: #1565C0;
                    border: 2px solid #0D47A1;
                    border-radius: 10px;
                    color: white;
                    font-size: 18px;
                }

                QPushButton:hover {
                    background: #1976D2;
                }
            """)

            self.lbl.setStyleSheet("""
                color: #1565C0;
                font-weight: bold;
                background: transparent;
            """)

        else:

            self.btn.setStyleSheet("""
                QPushButton {
                    background: white;
                    border: 2px solid #90CAF9;
                    border-radius: 10px;
                    color: #666;
                    font-size: 18px;
                }

                QPushButton:hover {
                    background: #E3F2FD;
                    border: 2px solid #1565C0;
                }
            """)

            self.lbl.setStyleSheet("""
                color: #333;
                background: transparent;
            """)


# =========================================================
# ORDER PANEL
# =========================================================
class RichOrderPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumWidth(360)
        self.setMaximumWidth(650)

        self.setStyleSheet("""
            QWidget {
                background: white;
                border-left: 1px solid #DDE7F5;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)

        shadow.setBlurRadius(18)
        shadow.setOffset(-2, 0)
        shadow.setColor(QColor(0, 0, 0, 40))

        self.setGraphicsEffect(shadow)

        self.order = None
        self.on_delete = None
        self.on_pay = None

        self._build()

    def _build(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # =================================================
        # HEADER
        # =================================================

        header = QWidget()

        header.setFixedHeight(42)

        header.setStyleSheet("""
            background: #1976D2;
        """)

        h = QHBoxLayout(header)

        h.setContentsMargins(8, 0, 8, 0)
        h.setSpacing(6)

        self.table_label = QPushButton("")

        self.table_label.setFixedHeight(30)

        self.table_label.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.2);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 0 10px;
            }
        """)

        search = QLineEdit()

        search.setPlaceholderText(
            "🔍  Tìm khách hàng (F4)"
        )

        search.setFixedHeight(30)

        search.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.15);
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 15px;
                padding: 0 12px;
                color: white;
            }
        """)

        h.addWidget(self.table_label)
        h.addWidget(search)

        layout.addWidget(header)

        # =================================================
        # SCROLL
        # =================================================

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(True)

        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: white;
            }
        """)

        self.items_widget = QWidget()

        self.items_layout = QVBoxLayout(
            self.items_widget
        )

        self.items_layout.setContentsMargins(
            0, 0, 0, 0
        )

        self.items_layout.addStretch()

        self.scroll.setWidget(
            self.items_widget
        )

        layout.addWidget(self.scroll, 1)

        # =================================================
        # TOTAL BAR
        # =================================================

        total_bar = QWidget()

        total_bar.setFixedHeight(50)

        total_bar.setStyleSheet("""
            background: white;
            border-top: 1px solid #E5EDF7;
        """)

        tb = QHBoxLayout(total_bar)

        tb.setContentsMargins(14, 0, 14, 0)

        lbl = QLabel("Tổng tiền")

        lbl.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #444;
        """)

        self.lbl_total = QLabel("0₫")

        self.lbl_total.setStyleSheet("""
            color: #1565C0;
            font-size: 18px;
            font-weight: bold;
        """)

        tb.addWidget(lbl)
        tb.addStretch()
        tb.addWidget(self.lbl_total)

        layout.addWidget(total_bar)

        # =================================================
        # BUTTONS
        # =================================================

        btn_bar = QWidget()

        btn_bar.setFixedHeight(60)

        bb = QHBoxLayout(btn_bar)

        bb.setContentsMargins(10, 8, 10, 8)

        self.btn_print = QPushButton(
            "🖨  In tạm tính"
        )

        self.btn_pay = QPushButton(
            "💲  Thanh toán (F9)"
        )

        self.btn_notify = QPushButton(
            "🔔  Thông báo"
        )

        buttons = [
            self.btn_print,
            self.btn_pay,
            self.btn_notify
        ]

        for btn in buttons:

            btn.setFixedHeight(38)

            btn.setStyleSheet("""
                QPushButton {
                    background: #1565C0;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                }

                QPushButton:hover {
                    background: #1976D2;
                }
            """)

            bb.addWidget(btn)

        layout.addWidget(btn_bar)

    # =====================================================
    # LOAD ORDER
    # =====================================================

    def load_order(self, order, table_name=""):

        self.order = order

        self.table_label.setText(
            f"🏠  {table_name}"
        )

        while self.items_layout.count() > 1:

            item = self.items_layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        if not order or not order.items:

            self.lbl_total.setText("0₫")
            return

        for idx, item in enumerate(order.items, 1):

            row = QLabel(
                f"{idx}. {item.product_name}  x{item.quantity}"
            )

            row.setStyleSheet("""
                padding: 10px 14px;
                border-bottom: 1px solid #EEF2F8;
                font-size: 13px;
            """)

            self.items_layout.insertWidget(
                self.items_layout.count() - 1,
                row
            )

        self.lbl_total.setText(
            f"{order.subtotal:,}₫"
        )


# =========================================================
# POS SCREEN
# =========================================================
class PosScreen(QWidget):

    def __init__(self):

        super().__init__()

        self.setStyleSheet("""
            background: #EEF4FC;
        """)

        self.session = get_session()

        self.table_repo = TableRepository(
            self.session
        )

        self.product_repo = ProductRepository(
            self.session
        )

        self.order_service = OrderService(
            self.session
        )

        self.order_controller = OrderController(
            self.order_service
        )

        self.product_controller = ProductController(
            ProductService(self.session)
        )

        self.payment_controller = PaymentController(
            PaymentService(self.session)
        )

        self.current_order = None
        self.current_table = None
        self.current_user_id = 1

        self.table_cards = {}

        self.all_tables = []

        self.filter_mode = "all"

        self.build_ui()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        root = QVBoxLayout(self)

        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(
            self._build_topbar()
        )

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        splitter.setHandleWidth(2)

        left_panel = self._build_left()

        right_panel = self._build_right_panel()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        # 6 / 4
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)
        splitter.setSizes([1200, 800])

        left_panel.setMinimumWidth(0)

        right_panel.setMinimumWidth(460)
        right_panel.setMaximumWidth(520)

        splitter.setStyleSheet("""
            QSplitter::handle {
                background: #D6E4F5;
            }
        """)

        root.addWidget(splitter, 1)

    # =====================================================
    # TOPBAR
    # =====================================================

    def _build_topbar(self):

        bar = QWidget()

        bar.setFixedHeight(52)

        bar.setStyleSheet("""
            background: #1565C0;
        """)

        layout = QHBoxLayout(bar)

        layout.setContentsMargins(
            12, 0, 16, 0
        )

        self.btn_tab_table = QPushButton(
            "🏠  Phòng bàn"
        )

        self.btn_tab_table.setFixedHeight(36)

        self.btn_tab_table.setStyleSheet("""
            QPushButton {
                background: white;
                color: #1565C0;
                border-radius: 8px;
                border: none;
                padding: 0 18px;
                font-weight: bold;
            }
        """)

        layout.addWidget(self.btn_tab_table)

        search = QLineEdit()

        search.setPlaceholderText(
            "🔍  Tìm món (F3)"
        )

        search.setFixedSize(260, 34)

        search.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.15);
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 17px;
                padding: 0 14px;
                color: white;
            }
        """)

        layout.addWidget(search)

        layout.addStretch()

        admin = QLabel("👤 Admin")

        admin.setStyleSheet("""
            color: white;
            font-weight: bold;
        """)

        layout.addWidget(admin)

        return bar

    # =====================================================
    # LEFT
    # =====================================================

    def _build_left(self):

        self.left_widget = QWidget()

        layout = QVBoxLayout(
            self.left_widget
        )

        layout.setContentsMargins(
            12, 10, 12, 10
        )

        layout.setSpacing(8)

        # FILTER
        filter_bar = QHBoxLayout()

        self.filter_group = QButtonGroup(self)

        self.rb_all = self._make_radio(
            "Tất cả",
            "all"
        )

        self.rb_using = self._make_radio(
            "Sử dụng",
            "using"
        )

        self.rb_empty = self._make_radio(
            "Còn trống",
            "empty"
        )

        self.rb_all.setChecked(True)

        radios = [
            self.rb_all,
            self.rb_using,
            self.rb_empty
        ]

        for rb in radios:

            self.filter_group.addButton(rb)
            filter_bar.addWidget(rb)

        filter_bar.addStretch()

        layout.addLayout(filter_bar)

        # SCROLL
        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(True)

        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        self.grid_container = QWidget()

        self.table_grid = QGridLayout(
            self.grid_container
        )

        # tạo xong grid rồi mới checked
        self.rb_all.setChecked(True)

        self.table_grid.setSpacing(12)

        self.table_grid.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.scroll_area.setWidget(
            self.grid_container
        )

        layout.addWidget(self.scroll_area, 1)

        self._load_tables()

        return self.left_widget

    # =====================================================
    # RIGHT PANEL
    # =====================================================

    def _build_right_panel(self):

        self.order_panel = RichOrderPanel()

        self.order_panel.btn_pay.clicked.connect(
            self._on_pay
        )

        return self.order_panel

    # =====================================================
    # RADIO
    # =====================================================

    def _make_radio(self, text, mode):

        rb = QRadioButton(text)

        rb.setStyleSheet("""
            QRadioButton {
                font-size: 13px;
                font-weight: bold;
            }
        """)

        rb.toggled.connect(
            lambda checked, m=mode:
            self._on_filter(m)
            if checked else None
        )

        return rb

    # =====================================================
    # FILTER
    # =====================================================

    def _on_filter(self, mode):
        self.filter_mode = mode

        if hasattr(self, "table_grid"):
            self._render_table_grid()

    # =====================================================
    # TABLES
    # =====================================================

    def _load_tables(self):

        self.all_tables = (
            self.table_repo.get_all()
        )

        self._render_table_grid()

    def _render_table_grid(self):

        while self.table_grid.count():

            item = self.table_grid.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        self.table_cards.clear()

        if self.filter_mode == "using":

            tables = [
                t for t in self.all_tables
                if t.status == TableStatus.USING
            ]

        elif self.filter_mode == "empty":

            tables = [
                t for t in self.all_tables
                if t.status == TableStatus.EMPTY
            ]

        else:
            tables = self.all_tables

        COLS = 7

        for idx, table in enumerate(tables):

            card = TableCard(
                table,
                self.select_table
            )

            self.table_cards[table.id] = card

            self.table_grid.addWidget(
                card,
                idx // COLS,
                idx % COLS
            )

        for col in range(COLS):
            self.table_grid.setColumnStretch(col, 1)

    # =====================================================
    # SELECT TABLE
    # =====================================================

    def select_table(self, table):

        self.current_table = table

        self.current_order = (
            self.order_controller
            .create_or_get_order(
                table.id,
                self.current_user_id
            )
        )

        self.order_panel.load_order(
            self.current_order,
            table.name
        )

        self._refresh_cards()

    # =====================================================
    # PAYMENT
    # =====================================================

    def _on_pay(self):

        if not self.current_order:

            QMessageBox.warning(
                self,
                "Thông báo",
                "Chưa có order!"
            )

            return

        QMessageBox.information(
            self,
            "Thanh toán",
            f"Tổng: {self.current_order.subtotal:,}₫"
        )

    # =====================================================
    # REFRESH
    # =====================================================

    def _refresh_cards(self):

        self.all_tables = (
            self.table_repo.get_all()
        )

        self._render_table_grid()