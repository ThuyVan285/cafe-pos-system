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
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.btn = QPushButton()
        self.btn.setFixedHeight(46)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn.clicked.connect(lambda: callback(table))

        self.lbl = QLabel(table.name)
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setFont(QFont("Segoe UI", 9))

        layout.addWidget(self.btn)
        layout.addWidget(self.lbl)
        self.refresh()

    def refresh(self):
        is_using = self.table.status == TableStatus.USING
        is_takeaway = "Away" in self.table.name or "away" in self.table.name
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
                QPushButton:hover { background: #1976D2; }
            """)
            self.lbl.setStyleSheet("color: #1565C0; font-weight: bold; background: transparent;")
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
            self.lbl.setStyleSheet("color: #333; background: transparent;")


# =========================================================
# ORDER ITEM ROW
# =========================================================
class OrderItemRow(QWidget):
    def __init__(self, index, item, on_delete):
        super().__init__()
        self.setStyleSheet("background: white; border-bottom: 1px solid #EEF2F8;")

        v = QVBoxLayout(self)
        v.setContentsMargins(12, 8, 12, 4)
        v.setSpacing(4)

        row = QHBoxLayout()
        row.setSpacing(6)

        btn_del = QPushButton("🗑")
        btn_del.setFixedSize(26, 26)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet("""
            QPushButton { background: transparent; border: none; color: #BDBDBD; font-size: 14px; }
            QPushButton:hover { color: #E53935; }
        """)
        btn_del.clicked.connect(lambda: on_delete(item))

        lbl_idx = QLabel(f"{index}.")
        lbl_idx.setFixedWidth(20)
        lbl_idx.setStyleSheet("color: #888; font-size: 13px;")

        name = item.product_name
        if item.size:
            name += f" ({item.size})"
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("color: #1E2D3D; font-size: 13px; font-weight: bold;")
        lbl_name.setWordWrap(True)

        lbl_qty = QLabel(str(item.quantity))
        lbl_qty.setFixedWidth(24)
        lbl_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_qty.setStyleSheet("color: #555; font-size: 13px;")

        lbl_unit = QLabel(f"{item.unit_price:,}")
        lbl_unit.setFixedWidth(65)
        lbl_unit.setAlignment(Qt.AlignmentFlag.AlignRight)
        lbl_unit.setStyleSheet("color: #888; font-size: 12px;")

        lbl_total = QLabel(f"{item.total_price:,}")
        lbl_total.setFixedWidth(65)
        lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        lbl_total.setStyleSheet("color: #1E2D3D; font-size: 13px; font-weight: bold;")

        row.addWidget(btn_del)
        row.addWidget(lbl_idx)
        row.addWidget(lbl_name, 1)
        row.addWidget(lbl_qty)
        row.addWidget(lbl_unit)
        row.addWidget(lbl_total)
        v.addLayout(row)

        note_btn = QPushButton("✏  Ghi chú món")
        note_btn.setFixedHeight(24)
        note_btn.setFixedWidth(160)
        note_btn.setStyleSheet("""
            QPushButton {
                background: #F0F4FA; color: #90A4AE;
                border: none; border-radius: 6px;
                font-size: 11px; text-align: left; padding-left: 8px;
            }
            QPushButton:hover { background: #E3EAF5; color: #607D8B; }
        """)
        v.addWidget(note_btn)


# =========================================================
# RICH ORDER PANEL
# =========================================================
class RichOrderPanel(QWidget):

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(360)
        self.setMaximumWidth(650)
        self.setStyleSheet("background: white; border-left: 1px solid #DDE7F5;")
        self.order = None
        self.on_delete = None
        self.on_pay = None
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # HEADER
        header = QWidget()
        header.setFixedHeight(44)
        header.setStyleSheet("background: #1565C0;")
        h = QHBoxLayout(header)
        h.setContentsMargins(12, 0, 12, 0)
        h.setSpacing(8)

        self.table_label = QLabel("🏠  Chưa chọn bàn")
        self.table_label.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")

        cart_btn = QPushButton("🛒")
        cart_btn.setFixedSize(32, 32)
        cart_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.2); border: none;
                border-radius: 16px; color: white; font-size: 16px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.35); }
        """)

        h.addWidget(self.table_label, 1)
        h.addWidget(cart_btn)
        layout.addWidget(header)

        # COLUMN HEADER
        col_hdr = QWidget()
        col_hdr.setFixedHeight(28)
        col_hdr.setStyleSheet("background: #F5F8FF; border-bottom: 1px solid #E0E8F5;")
        ch = QHBoxLayout(col_hdr)
        ch.setContentsMargins(12, 0, 12, 0)
        ch.setSpacing(0)
        for text, stretch, width in [
            ("Món", 1, 0),
            ("SL", 0, 28),
            ("Đơn giá", 0, 65),
            ("T.Tiền", 0, 65),
        ]:
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #999; font-size: 11px;")
            if stretch:
                lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
                ch.addWidget(lbl, 1)
            else:
                lbl.setFixedWidth(width)
                lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
                ch.addWidget(lbl)
        layout.addWidget(col_hdr)

        # SCROLL
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea { border: none; background: white; }
            QScrollBar:vertical { background: #F0F4FA; width: 5px; border-radius: 2px; }
            QScrollBar::handle:vertical { background: #B0C8E8; border-radius: 2px; }
        """)
        self.items_widget = QWidget()
        self.items_widget.setStyleSheet("background: white;")
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(0)
        self.items_layout.addStretch()
        self.scroll.setWidget(self.items_widget)
        layout.addWidget(self.scroll, 1)

        # TOTAL BAR
        total_bar = QWidget()
        total_bar.setFixedHeight(44)
        total_bar.setStyleSheet("background: #F5F8FF; border-top: 1.5px solid #DDEAF8;")
        tb = QHBoxLayout(total_bar)
        tb.setContentsMargins(14, 0, 14, 0)

        gift = QLabel("🎁")
        gift.setStyleSheet("font-size: 16px;")
        lbl_tong = QLabel("Tổng tiền")
        lbl_tong.setStyleSheet("color: #555; font-size: 13px; font-weight: bold;")

        self.lbl_count = QLabel("0")
        self.lbl_count.setFixedSize(22, 22)
        self.lbl_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_count.setStyleSheet("""
            background: #1565C0; color: white;
            border-radius: 11px; font-size: 11px; font-weight: bold;
        """)

        self.lbl_total = QLabel("0₫")
        self.lbl_total.setStyleSheet("color: #1565C0; font-size: 17px; font-weight: bold;")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)

        tb.addWidget(gift)
        tb.addSpacing(4)
        tb.addWidget(lbl_tong)
        tb.addSpacing(6)
        tb.addWidget(self.lbl_count)
        tb.addStretch()
        tb.addWidget(self.lbl_total)
        layout.addWidget(total_bar)

        # BUTTONS
        btn_bar = QWidget()
        btn_bar.setFixedHeight(56)
        btn_bar.setStyleSheet("background: white; border-top: 1px solid #E8EEF8;")
        bb = QHBoxLayout(btn_bar)
        bb.setContentsMargins(10, 8, 10, 8)
        bb.setSpacing(8)

        self.btn_print = QPushButton("🖨  In tạm tính")
        self.btn_notify = QPushButton("🔔  Thông báo")
        self.btn_pay = QPushButton("💳  Thanh toán")

        styles = [
            ("background: #607D8B;", self.btn_print),
            ("background: #1565C0;", self.btn_notify),
            ("background: #2E7D32;", self.btn_pay),
        ]
        for color, btn in styles:
            btn.setFixedHeight(38)
            btn.setStyleSheet(f"""
                QPushButton {{
                    {color} color: white; border: none;
                    border-radius: 8px; font-size: 12px; font-weight: bold;
                }}
                QPushButton:hover {{ opacity: 0.85; }}
            """)
            bb.addWidget(btn, 1)

        layout.addWidget(btn_bar)

    def load_order(self, order, table_name=""):
        self.order = order
        if table_name:
            self.table_label.setText(f"🏠  {table_name}")

        while self.items_layout.count() > 1:
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not order or not order.items:
            self.lbl_total.setText("0₫")
            self.lbl_count.setText("0")
            return

        for idx, item in enumerate(order.items, 1):
            row = OrderItemRow(idx, item,
                               self.on_delete if self.on_delete else lambda x: None)
            self.items_layout.insertWidget(self.items_layout.count() - 1, row)

        total_qty = sum(i.quantity for i in order.items)
        self.lbl_count.setText(str(total_qty))
        self.lbl_total.setText(f"{order.subtotal:,}₫")


# =========================================================
# POS SCREEN
# =========================================================
class PosScreen(QWidget):

    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.current_user_id = user.id if user else 1
        self.setStyleSheet("background: #EEF4FC;")

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
        self.table_cards = {}
        self.all_tables = []
        self.filter_mode = "all"

        self.build_ui()

    # ── BUILD ─────────────────────────────────────────────────
    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_topbar())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("QSplitter::handle { background: #D6E4F5; }")

        left = self._build_left()
        right = self._build_right_panel()

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)
        splitter.setSizes([900, 500])
        right.setMinimumWidth(400)
        right.setMaximumWidth(560)

        root.addWidget(splitter, 1)

    # ── TOPBAR ────────────────────────────────────────────────
    def _build_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(52)
        bar.setStyleSheet("background: #1565C0;")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 16, 0)
        layout.setSpacing(4)

        self.btn_tab_table = self._make_tab_btn("🏠  Phòng bàn", True)
        self.btn_tab_menu  = self._make_tab_btn("📋  Thực đơn",  False)
        self.btn_tab_table.clicked.connect(self._show_table_view)
        self.btn_tab_menu.clicked.connect(self._show_menu_view)

        layout.addWidget(self.btn_tab_table)
        layout.addWidget(self.btn_tab_menu)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍  Tìm món (F3)")
        self.search_box.setFixedSize(240, 34)
        self.search_box.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.15);
                border: 1.5px solid rgba(255,255,255,0.4);
                border-radius: 17px; padding: 0 14px;
                font-size: 13px; color: white;
            }
            QLineEdit:focus {
                background: rgba(255,255,255,0.25);
                border: 1.5px solid white;
            }
        """)
        self.search_box.textChanged.connect(self._on_search)
        layout.addWidget(self.search_box)
        layout.addStretch()

        name = self.user.full_name if self.user else "Admin"
        role = self.user.role.value if self.user else ""
        user_lbl = QLabel(f"👤  {name}")
        user_lbl.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")
        layout.addWidget(user_lbl)

        return bar

    def _make_tab_btn(self, text, active) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(36)
        btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if active:
            btn.setStyleSheet("""
                QPushButton {
                    background: white; color: #1565C0;
                    border: none; border-radius: 8px;
                    padding: 0 18px; font-weight: bold;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent; color: rgba(255,255,255,0.8);
                    border: none; border-radius: 8px; padding: 0 18px;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.15); color: white;
                }
            """)
        return btn

    # ── LEFT ──────────────────────────────────────────────────
    def _build_left(self) -> QWidget:
        self.left_widget = QWidget()
        self.left_widget.setStyleSheet("background: #EEF4FC;")
        layout = QVBoxLayout(self.left_widget)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Filter bar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(16)
        self.filter_group = QButtonGroup(self)
        self.rb_all   = self._make_radio("Tất cả",    "all")
        self.rb_using = self._make_radio("Sử dụng",   "using")
        self.rb_empty = self._make_radio("Còn trống", "empty")
        self.rb_all.setChecked(True)
        for rb in [self.rb_all, self.rb_using, self.rb_empty]:
            self.filter_group.addButton(rb)
            filter_bar.addWidget(rb)
        filter_bar.addStretch()
        layout.addLayout(filter_bar)

        # Table scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: #DDE8F8; width: 7px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: #90B4D8; border-radius: 3px; }
        """)
        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.table_grid = QGridLayout(self.grid_container)
        self.table_grid.setSpacing(10)
        self.table_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll_area.setWidget(self.grid_container)
        layout.addWidget(self.scroll_area, 1)

        # Product scroll (ẩn ban đầu)
        self.scroll_product = QScrollArea()
        self.scroll_product.setWidgetResizable(True)
        self.scroll_product.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: #DDE8F8; width: 7px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: #90B4D8; border-radius: 3px; }
        """)
        self.product_container = QWidget()
        self.product_container.setStyleSheet("background: transparent;")
        self.product_grid = QGridLayout(self.product_container)
        self.product_grid.setSpacing(8)
        self.product_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll_product.setWidget(self.product_container)
        self.scroll_product.setVisible(False)
        layout.addWidget(self.scroll_product, 1)

        self._load_tables()
        return self.left_widget

    # ── RIGHT ─────────────────────────────────────────────────
    def _build_right_panel(self) -> QWidget:
        self.order_panel = RichOrderPanel()
        self.order_panel.on_delete = self._on_delete_item
        self.order_panel.btn_pay.clicked.connect(self._on_pay)
        self.order_panel.btn_notify.clicked.connect(self._on_notify)
        return self.order_panel


    # ── RADIO ─────────────────────────────────────────────────
    def _make_radio(self, text, mode) -> QRadioButton:
        rb = QRadioButton(text)
        rb.setStyleSheet("""
            QRadioButton { font-size: 13px; font-weight: bold; color: #1E2D3D; spacing: 5px; }
            QRadioButton::indicator { width: 15px; height: 15px; }
            QRadioButton::indicator:checked {
                background: #1565C0; border-radius: 7px; border: 2px solid #1565C0;
            }
            QRadioButton::indicator:unchecked {
                background: white; border-radius: 7px; border: 2px solid #90CAF9;
            }
        """)
        rb.toggled.connect(
            lambda checked, m=mode: self._on_filter(m) if checked else None
        )
        return rb

    def _on_filter(self, mode):
        self.filter_mode = mode
        if hasattr(self, 'table_grid'):
            self._render_table_grid()

    # ── TABLES ────────────────────────────────────────────────
    def _load_tables(self):
        self.all_tables = self.table_repo.get_all()
        self._render_table_grid()

    def _render_table_grid(self):
        while self.table_grid.count():
            item = self.table_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.table_cards.clear()

        if self.filter_mode == "using":
            tables = [t for t in self.all_tables if t.status == TableStatus.USING]
        elif self.filter_mode == "empty":
            tables = [t for t in self.all_tables if t.status == TableStatus.EMPTY]
        else:
            tables = self.all_tables

        using = sum(1 for t in self.all_tables if t.status == TableStatus.USING)
        empty = len(self.all_tables) - using
        self.rb_all.setText(f"Tất cả ({len(self.all_tables)})")
        self.rb_using.setText(f"Sử dụng ({using})")
        self.rb_empty.setText(f"Còn trống ({empty})")

        COLS = 7
        for idx, table in enumerate(tables):
            card = TableCard(table, self.select_table)
            self.table_cards[table.id] = card
            self.table_grid.addWidget(card, idx // COLS, idx % COLS)
        for col in range(COLS):
            self.table_grid.setColumnStretch(col, 1)

    # ── MENU ──────────────────────────────────────────────────
    def _load_product_grid(self, keyword=""):
        while self.product_grid.count():
            item = self.product_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        products = self.product_repo.search(keyword) if keyword else self.product_repo.get_all_active()

        COLS = 4
        for idx, product in enumerate(products):
            btn = self._make_product_card(product)
            self.product_grid.addWidget(btn, idx // COLS, idx % COLS)

    def _make_product_card(self, product) -> QPushButton:
        if product.has_size and product.sizes:
            min_delta = min(s.price_delta for s in product.sizes)
            price_text = f"từ {(product.base_price + min_delta):,}₫"
        else:
            price_text = f"{product.base_price:,}₫"

        btn = QPushButton(f"{product.name}\n{price_text}")
        btn.setFixedSize(168, 76)
        btn.setFont(QFont("Segoe UI", 10))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: white; color: #1E2D3D;
                border: 1.5px solid #BBDEFB; border-radius: 10px;
                font-size: 11px; font-weight: bold;
                padding: 4px; text-align: center;
            }
            QPushButton:hover {
                background: #E3F2FD; border: 2px solid #1565C0; color: #1565C0;
            }
            QPushButton:pressed { background: #BBDEFB; }
        """)
        btn.clicked.connect(lambda checked, p=product: self.add_product(p))
        return btn

    # ── SWITCH VIEW ───────────────────────────────────────────
    def _show_table_view(self):
        self.scroll_area.setVisible(True)
        self.scroll_product.setVisible(False)
        self.btn_tab_table.setStyleSheet("""
            QPushButton {
                background: white; color: #1565C0;
                border: none; border-radius: 8px;
                padding: 0 18px; font-weight: bold;
            }
        """)
        self.btn_tab_menu.setStyleSheet("""
            QPushButton {
                background: transparent; color: rgba(255,255,255,0.8);
                border: none; border-radius: 8px; padding: 0 18px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.15); color: white; }
        """)
        self._load_tables()

    def _show_menu_view(self):
        if not self.current_table:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn bàn trước!")
            return
        self.scroll_area.setVisible(False)
        self.scroll_product.setVisible(True)
        self.btn_tab_menu.setStyleSheet("""
            QPushButton {
                background: white; color: #1565C0;
                border: none; border-radius: 8px;
                padding: 0 18px; font-weight: bold;
            }
        """)
        self.btn_tab_table.setStyleSheet("""
            QPushButton {
                background: transparent; color: rgba(255,255,255,0.8);
                border: none; border-radius: 8px; padding: 0 18px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.15); color: white; }
        """)
        self._load_product_grid()

    def _on_search(self, keyword: str):
        if self.scroll_product.isVisible():
            self._load_product_grid(keyword.strip())

    # ── ACTIONS ───────────────────────────────────────────────
    def select_table(self, table):
        self.current_table = table
        self.current_order = self.order_controller.create_or_get_order(
            table.id, self.current_user_id
        )
        self.order_panel.load_order(self.current_order, table.name)
        self._show_menu_view()
        self._refresh_cards()

    def add_product(self, product):
        if not self.current_order:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn bàn trước!")
            return

        if (product.has_size and product.sizes) or (
            hasattr(product, 'available_toppings') and product.available_toppings
        ):
            from ui.dialogs.product_dialog import ProductDialog
            dialog = ProductDialog(product, self)
            if dialog.exec():
                result = dialog.get_result()
                size_name = result["size"].size if result["size"] else ""
                self.order_controller.add_product(
                    self.current_order, product.id, size=size_name
                )
        else:
            self.order_controller.add_product(self.current_order, product.id)

        self.current_order = self.order_service.get_active_order(self.current_table.id)
        self.order_panel.load_order(self.current_order, self.current_table.name)

    def _on_delete_item(self, item):
        try:
            self.order_service.remove_item(item.id)
            self.current_order = self.order_service.get_active_order(self.current_table.id)
            self.order_panel.load_order(self.current_order, self.current_table.name)
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def _on_pay(self):
        if not self.current_order or not self.current_order.items:
            QMessageBox.warning(self, "Thông báo", "Chưa có món nào!")
            return

        from ui.dialogs.payment_dialog import PaymentDialog
        dialog = PaymentDialog(
            self.current_order,
            self.current_table,
            self.session,
            self
        )
        if dialog.exec():
            # Reset sau thanh toán
            self.current_order = None
            self.current_table = None
            self.order_panel.load_order(None, "")
            self._show_table_view()
            self._refresh_cards()
    def _refresh_cards(self):
        self.all_tables = self.table_repo.get_all()
        if hasattr(self, 'table_grid'):
            self._render_table_grid()

    def _on_notify(self):
        if not self.current_order or not self.current_order.items:
            QMessageBox.warning(self, "Thông báo", "Chưa có món nào trong order!")
            return

        from ui.dialogs.notify_dialog import NotifyDialog
        dialog = NotifyDialog(self.current_order, self.current_table, self)
        dialog.exec()