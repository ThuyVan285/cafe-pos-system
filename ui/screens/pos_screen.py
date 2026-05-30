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
# =========================================================
# TABLE CARD — tự fill ô, thông tin TRONG nút xanh
# =========================================================
class TableCard(QWidget):

    def __init__(self, table, callback, order_data=None):
        super().__init__()
        self.table = table
        self.order_data = order_data
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(3)

        self.btn = QPushButton()
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.btn.clicked.connect(lambda: callback(table))

        # Tên bàn luôn nằm ngoài, bên dưới nút
        self.lbl = QLabel(table.name)
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.lbl.setFixedHeight(16)

        layout.addWidget(self.btn)
        layout.addWidget(self.lbl)
        self.refresh()

    def refresh(self):
        is_using = self.table.status == TableStatus.USING
        is_takeaway = "Away" in self.table.name or "away" in self.table.name

        if is_using and self.order_data:
            total    = self.order_data.get('total', 0)
            items_ct = self.order_data.get('items_count', 0)
            time_str = self.order_data.get('time', '')

            # Chỉ hiện thông tin order trong nút, không có tên bàn
            self.btn.setText(
                f"💲 {total:,}₫\n"
                f"🍽 {items_ct}   {time_str}"
            )
            self.btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            self.btn.setStyleSheet("""
                QPushButton {
                    background: #1565C0;
                    border: 2px solid #0D47A1;
                    border-radius: 14px;
                    color: white;
                    font-size: 10px;
                    text-align: center;
                    padding: 4px;
                }
                QPushButton:hover { background: #1976D2; }
            """)
            self.lbl.setStyleSheet("color: #1565C0; font-weight: bold;")

        elif is_using:
            self.btn.setText("🛍️" if is_takeaway else "")
            self.btn.setFont(QFont("Segoe UI", 18))
            self.btn.setStyleSheet("""
                QPushButton {
                    background: #1565C0;
                    border: 2px solid #0D47A1;
                    border-radius: 14px;
                    color: white;
                }
                QPushButton:hover { background: #1976D2; }
            """)
            self.lbl.setStyleSheet("color: #1565C0; font-weight: bold;")

        else:
            self.btn.setText("🛍️" if is_takeaway else "")
            self.btn.setFont(QFont("Segoe UI", 18))
            self.btn.setStyleSheet("""
                QPushButton {
                    background: white;
                    border: 2px solid #90CAF9;
                    border-radius: 14px;
                    color: #444;
                }
                QPushButton:hover {
                    background: #E3F2FD;
                    border: 2px solid #1565C0;
                }
            """)
            self.lbl.setStyleSheet("color: #555;")
# =========================================================
# ORDER ITEM ROW
# =========================================================
class OrderItemRow(QWidget):
    def __init__(self, index, item, on_delete,
                 on_qty_change=None, on_note_change=None):
        super().__init__()
        self.item = item
        self.on_qty_change = on_qty_change
        self.on_note_change = on_note_change
        self.setStyleSheet("background: white; border-bottom: 1px solid #EEF2F8;")

        v = QVBoxLayout(self)
        v.setContentsMargins(12, 8, 12, 4)
        v.setSpacing(4)

        row = QHBoxLayout()
        row.setSpacing(6)

        # Nút xóa
        btn_del = QPushButton("🗑")
        btn_del.setFixedSize(26, 26)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet("""
            QPushButton { background: transparent; border: none;
                          color: #BDBDBD; font-size: 14px; }
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
        lbl_name.setStyleSheet(
            "color: #1E2D3D; font-size: 13px; font-weight: bold;"
        )
        lbl_name.setWordWrap(True)

        # ── +/- SỐ LƯỢNG ──────────────────────────────────────
        qty_w = QWidget()
        qty_w.setStyleSheet("background: transparent;")
        qty_l = QHBoxLayout(qty_w)
        qty_l.setContentsMargins(0, 0, 0, 0)
        qty_l.setSpacing(3)

        btn_minus = QPushButton("−")
        btn_minus.setFixedSize(22, 22)
        btn_minus.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_minus.setStyleSheet("""
            QPushButton {
                background: #EEF2F8; color: #555;
                border: none; border-radius: 11px;
                font-size: 15px; font-weight: bold;
            }
            QPushButton:hover { background: #E53935; color: white; }
        """)

        self.lbl_qty = QLabel(str(item.quantity))
        self.lbl_qty.setFixedWidth(22)
        self.lbl_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_qty.setStyleSheet(
            "color: #1E2D3D; font-size: 13px; font-weight: bold;"
        )

        btn_plus = QPushButton("+")
        btn_plus.setFixedSize(22, 22)
        btn_plus.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_plus.setStyleSheet("""
            QPushButton {
                background: #EEF2F8; color: #555;
                border: none; border-radius: 11px;
                font-size: 15px; font-weight: bold;
            }
            QPushButton:hover { background: #1565C0; color: white; }
        """)

        btn_minus.clicked.connect(self._on_minus)
        btn_plus.clicked.connect(self._on_plus)

        qty_l.addWidget(btn_minus)
        qty_l.addWidget(self.lbl_qty)
        qty_l.addWidget(btn_plus)

        lbl_unit = QLabel(f"{item.unit_price:,}")
        lbl_unit.setFixedWidth(60)
        lbl_unit.setAlignment(Qt.AlignmentFlag.AlignRight)
        lbl_unit.setStyleSheet("color: #888; font-size: 12px;")

        self.lbl_total = QLabel(f"{item.total_price:,}")
        self.lbl_total.setFixedWidth(65)
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_total.setStyleSheet(
            "color: #1E2D3D; font-size: 13px; font-weight: bold;"
        )

        row.addWidget(btn_del)
        row.addWidget(lbl_idx)
        row.addWidget(lbl_name, 1)
        row.addWidget(qty_w)
        row.addWidget(lbl_unit)
        row.addWidget(self.lbl_total)
        v.addLayout(row)

        # ── GHI CHÚ MÓN ──────────────────────────────────────
        note_text = item.note if item.note else "✏  Ghi chú món"
        self.note_btn = QPushButton(note_text)
        self.note_btn.setFixedHeight(24)
        self.note_btn.setFixedWidth(200)
        self._refresh_note_style()
        self.note_btn.clicked.connect(self._on_note_click)
        v.addWidget(self.note_btn)

    def _refresh_note_style(self):
        has_note = bool(self.item.note)
        self.note_btn.setText(
            f"📝  {self.item.note}" if has_note else "✏  Ghi chú món"
        )
        if has_note:
            self.note_btn.setStyleSheet("""
                QPushButton {
                    background: #E3F2FD; color: #1565C0;
                    border: 1px solid #90CAF9;
                    border-radius: 6px; font-size: 11px;
                    text-align: left; padding-left: 8px;
                    font-weight: bold;
                }
                QPushButton:hover { background: #BBDEFB; }
            """)
        else:
            self.note_btn.setStyleSheet("""
                QPushButton {
                    background: #F0F4FA; color: #90A4AE;
                    border: none; border-radius: 6px;
                    font-size: 11px; text-align: left; padding-left: 8px;
                }
                QPushButton:hover { background: #E3EAF5; color: #607D8B; }
            """)

    def _on_minus(self):
        if self.on_qty_change:
            self.on_qty_change(self.item, -1)

    def _on_plus(self):
        if self.on_qty_change:
            self.on_qty_change(self.item, +1)

    def _on_note_click(self):
        from PyQt6.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout,
            QLineEdit, QPushButton, QLabel
        )
        d = QDialog(self)
        d.setWindowTitle("Ghi chú món")
        d.setFixedWidth(340)
        d.setStyleSheet("background: white;")

        layout = QVBoxLayout(d)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        lbl = QLabel(f"✏  Ghi chú cho: {self.item.product_name}")
        lbl.setStyleSheet(
            "color: #1565C0; font-size: 13px; font-weight: bold;"
        )
        layout.addWidget(lbl)

        inp = QLineEdit(self.item.note or "")
        inp.setPlaceholderText("Ví dụ: ít đường, nhiều đá, không đá...")
        inp.setFixedHeight(42)
        inp.setStyleSheet("""
            QLineEdit {
                background: #F5F8FF; border: 1.5px solid #DDEAF8;
                border-radius: 8px; padding: 0 12px; font-size: 13px;
            }
            QLineEdit:focus { border: 1.5px solid #1565C0; }
        """)
        layout.addWidget(inp)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        btn_cancel = QPushButton("Hủy")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #EEF2F8; color: #555;
                border: none; border-radius: 8px; font-size: 13px;
            }
            QPushButton:hover { background: #CFD8DC; }
        """)
        btn_cancel.clicked.connect(d.reject)

        btn_save = QPushButton("💾  Lưu")
        btn_save.setFixedHeight(38)
        btn_save.setStyleSheet("""
            QPushButton {
                background: #1565C0; color: white;
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        btn_save.clicked.connect(d.accept)
        inp.returnPressed.connect(d.accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

        if d.exec():
            note = inp.text().strip()
            if self.on_note_change:
                self.on_note_change(self.item, note)


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
        self.on_qty_change = None  # thêm
        self.on_note_change = None  # thêm
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

        # ACTION BUTTONS
        action_bar = QWidget()
        action_bar.setFixedHeight(48)
        action_bar.setStyleSheet("background: white; border-top: 1px solid #E8EEF8;")
        ab = QHBoxLayout(action_bar)
        ab.setContentsMargins(10, 6, 10, 6)
        ab.setSpacing(8)

        self.btn_transfer = QPushButton("🔄  Chuyển bàn")
        self.btn_merge = QPushButton("🔀  Gộp bàn")

        for btn, color in [
            (self.btn_transfer, "#F57C00"),
            (self.btn_merge, "#6A1B9A"),
        ]:
            btn.setFixedHeight(36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color}; color: white;
                    border: none; border-radius: 8px;
                    font-size: 12px; font-weight: bold;
                }}
                QPushButton:hover {{ opacity: 0.85; }}
            """)
            ab.addWidget(btn, 1)

        layout.addWidget(action_bar)

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
                               self.on_delete if self.on_delete else lambda x: None,
                               on_qty_change=self.on_qty_change,  # thêm
                               on_note_change=self.on_note_change,  # thêm
                               )
            self.items_layout.insertWidget(self.items_layout.count() - 1, row)

        total_qty = sum(i.quantity for i in order.items)
        self.lbl_count.setText(str(total_qty))
        self.lbl_total.setText(f"{order.subtotal:,}₫")

    def set_notify_state(self, state: str):
        """
        state: 'default' | 'sent' | 'pending'
        """
        if state == "sent":
            self.btn_notify.setText("✅  Đã thông báo")
            self.btn_notify.setStyleSheet("""
                QPushButton {
                    background: #2E7D32; color: white;
                    border: none; border-radius: 8px;
                    font-size: 12px; font-weight: bold;
                }
                QPushButton:hover { background: #388E3C; }
            """)
        elif state == "pending":
            self.btn_notify.setText("🔔  Gửi bếp (mới)")
            self.btn_notify.setStyleSheet("""
                QPushButton {
                    background: #E65100; color: white;
                    border: none; border-radius: 8px;
                    font-size: 12px; font-weight: bold;
                }
                QPushButton:hover { background: #BF360C; }
            """)
        else:
            self.btn_notify.setText("🔔  Thông báo")
            self.btn_notify.setStyleSheet("""
                QPushButton {
                    background: #1565C0; color: white;
                    border: none; border-radius: 8px;
                    font-size: 12px; font-weight: bold;
                }
                QPushButton:hover { background: #1976D2; }
            """)


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
        self.table_cards = {}
        self.all_tables = []
        self.filter_mode = "all"
        self.selected_category = None  # ✅ khởi tạo ở đây
        self.cat_buttons = {}

        # Phân trang
        self.current_page = 0
        self.tables_per_page = 25  # 5 cột x 3 hàng
        self.total_pages = 0

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
        self.btn_tab_menu = self._make_tab_btn("📋  Thực đơn", False)
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

        # Thay đoạn cuối _build_topbar từ chỗ user_lbl trở đi:

        name = self.user.full_name if self.user else "Admin"
        user_lbl = QLabel(f"👤  {name}")
        user_lbl.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")
        layout.addWidget(user_lbl)

        # ✅ THÊM NÚT MENU 3 GẠCH
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setFixedSize(36, 36)
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.15);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover { background: rgba(255,255,255,0.3); }
        """)
        self.menu_btn.clicked.connect(self._show_staff_menu)
        layout.addWidget(self.menu_btn)
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

        # FILTER BAR (phòng bàn)
        self.filter_widget = QWidget()
        filter_bar = QHBoxLayout(self.filter_widget)
        filter_bar.setContentsMargins(0, 0, 0, 0)
        filter_bar.setSpacing(16)

        self.filter_group = QButtonGroup(self)
        self.rb_all = self._make_radio("Tất cả", "all")
        self.rb_using = self._make_radio("Sử dụng", "using")
        self.rb_empty = self._make_radio("Còn trống", "empty")
        self.rb_all.setChecked(True)

        for rb in [self.rb_all, self.rb_using, self.rb_empty]:
            self.filter_group.addButton(rb)
            filter_bar.addWidget(rb)
        filter_bar.addStretch()
        layout.addWidget(self.filter_widget)

        # CATEGORY BAR (thực đơn) — ẩn ban đầu
        self.category_scroll = QScrollArea()
        self.category_scroll.setFixedHeight(52)
        self.category_scroll.setWidgetResizable(True)
        self.category_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.category_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.category_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )
        self.category_widget = QWidget()
        self.category_layout = QHBoxLayout(self.category_widget)
        self.category_layout.setContentsMargins(0, 4, 0, 4)
        self.category_layout.setSpacing(8)
        self.category_scroll.setWidget(self.category_widget)
        self.category_scroll.setVisible(False)
        layout.addWidget(self.category_scroll)

        # TABLE GRID + PAGINATION
        grid_widget = QWidget()
        grid_layout = QVBoxLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(8)

        # Thay đoạn scroll_area + grid_widget bằng:
        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.table_grid = QGridLayout(self.grid_container)
        self.table_grid.setSpacing(8)
        # Không setAlignment — để tự fill

        layout.addWidget(self.grid_container, 1)  # ✅ stretch=1 fill hết chiều cao

        layout.addWidget(self.grid_container, 1)

        # ── PAGINATION BAR ────────────────────────────────────
        self.pagination_bar = QWidget()
        self.pagination_bar.setFixedHeight(40)
        self.pagination_bar.setStyleSheet("background: transparent;")
        pagination_layout = QHBoxLayout(self.pagination_bar)
        pagination_layout.setContentsMargins(0, 0, 0, 0)
        pagination_layout.setSpacing(8)

        self.btn_prev = QPushButton("◀  Trang trước")
        self.btn_prev.setFixedHeight(32)
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.setStyleSheet("""
                    QPushButton {
                        background: white; color: #1565C0;
                        border: 1.5px solid #90CAF9;
                        border-radius: 8px; font-size: 12px; font-weight: bold;
                        padding: 0 16px;
                    }
                    QPushButton:hover { background: #E3F2FD; }
                    QPushButton:pressed { background: #BBDEFB; }
                """)
        self.btn_prev.clicked.connect(self._on_prev_page)

        self.lbl_page = QLabel("1 / 1")
        self.lbl_page.setStyleSheet(
            "color: #1565C0; font-weight: bold; font-size: 13px;"
        )
        self.lbl_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_page.setFixedWidth(60)

        self.btn_next = QPushButton("Trang sau  ▶")
        self.btn_next.setFixedHeight(32)
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setStyleSheet("""
                    QPushButton {
                        background: white; color: #1565C0;
                        border: 1.5px solid #90CAF9;
                        border-radius: 8px; font-size: 12px; font-weight: bold;
                        padding: 0 16px;
                    }
                    QPushButton:hover { background: #E3F2FD; }
                    QPushButton:pressed { background: #BBDEFB; }
                """)
        self.btn_next.clicked.connect(self._on_next_page)

        pagination_layout.addWidget(self.btn_prev)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.lbl_page)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.btn_next)



        # ── SCROLL AREA bọc grid ──────────────────────────────
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
                    QScrollArea { border: none; background: transparent; }
                """)
        self.scroll_area.setWidget(self.grid_container)
        layout.addWidget(self.scroll_area, 1)

        layout.addWidget(self.pagination_bar)

        # PRODUCT SCROLL — ẩn ban đầu
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
        self.product_grid.setSpacing(10)
        self.product_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_product.setWidget(self.product_container)
        self.scroll_product.setVisible(False)
        layout.addWidget(self.scroll_product, 1)

        self._load_tables()
        return self.left_widget

    # ── RIGHT ─────────────────────────────────────────────────
    def _build_right_panel(self) -> QWidget:
        self.order_panel = RichOrderPanel()
        self.order_panel.on_delete = self._on_delete_item
        self.order_panel.on_qty_change = self._on_qty_change  # thêm
        self.order_panel.on_note_change = self._on_note_change  # thêm
        self.order_panel.btn_pay.clicked.connect(self._on_pay)
        self.order_panel.btn_notify.clicked.connect(self._on_notify)
        self.order_panel.btn_transfer.clicked.connect(self._on_transfer_table)
        self.order_panel.btn_merge.clicked.connect(self._on_merge_table)
        self.order_panel.btn_print.clicked.connect(self._on_print_temp)
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
        self.current_page = 0  # Reset về trang 1
        if hasattr(self, 'table_grid'):
            self._load_tables()
            self._render_table_grid()

    # ── CATEGORY BAR ──────────────────────────────────────────
    def _load_categories(self):
        # Xóa buttons cũ
        while self.category_layout.count():
            item = self.category_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Reset về Tất cả
        self.selected_category = None
        self.cat_buttons = {}

        icons = {
            "Cà phê": "☕",
            "Trà sữa": "🧋",
            "Trà": "🍵",
            "Latte và Sữa": "🥛",
            "Nước ép": "🍹",
            "Sữa chua": "🍦",
            "Nước giải khát": "🥤",
            "Sinh tố": "🍓",
            "Topping": "✨",
        }

        # Nút Tất cả — active mặc định
        btn_all = self._make_cat_btn("Tất cả", None, active=True)
        self.category_layout.addWidget(btn_all)
        self.cat_buttons[None] = btn_all

        # Load từ DB
        from models.category import Category
        cats = self.session.query(Category).order_by(Category.name).all()
        for cat in cats:
            icon = icons.get(cat.name, "🍴")
            btn = self._make_cat_btn(f"{icon} {cat.name}", cat.id, active=False)
            self.category_layout.addWidget(btn)
            self.cat_buttons[cat.id] = btn

        self.category_layout.addStretch()

    def _make_cat_btn(self, text, cat_id, active=False) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._set_cat_style(btn, active)
        btn.clicked.connect(
            lambda checked, cid=cat_id, b=btn: self._on_cat_click(cid, b)
        )
        return btn

    def _set_cat_style(self, btn, active: bool):
        if active:
            btn.setStyleSheet("""
                QPushButton {
                    background: #1565C0; color: white;
                    border: none; border-radius: 18px;
                    font-size: 12px; font-weight: bold;
                    padding: 0 16px;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background: white; color: #555;
                    border: 1.5px solid #D0DCF0;
                    border-radius: 18px;
                    font-size: 12px; padding: 0 14px;
                }
                QPushButton:hover {
                    background: #EBF5FF;
                    border: 1.5px solid #1565C0;
                    color: #1565C0;
                }
            """)

    def _on_cat_click(self, cat_id, clicked_btn):
        # ✅ Cập nhật selected_category
        self.selected_category = cat_id
        # Cập nhật style tất cả buttons
        for cid, btn in self.cat_buttons.items():
            self._set_cat_style(btn, cid == cat_id)
        # Load lại products theo category
        self._load_product_grid()

    # ── TABLES ────────────────────────────────────────────────
    def _load_tables(self):
        self.all_tables = self.table_repo.get_all()

        # Lọc theo filter mode
        if self.filter_mode == "using":
            filtered_tables = [t for t in self.all_tables if t.status == TableStatus.USING]
        elif self.filter_mode == "empty":
            filtered_tables = [t for t in self.all_tables if t.status == TableStatus.EMPTY]
        else:
            filtered_tables = self.all_tables

        self.filtered_tables = filtered_tables
        self.total_pages = (len(filtered_tables) + self.tables_per_page - 1) // self.tables_per_page
        if self.total_pages == 0:
            self.total_pages = 1

        # Clamp current_page
        if self.current_page >= self.total_pages:
            self.current_page = self.total_pages - 1

        self._render_table_grid()

    def _render_table_grid(self):
        while self.table_grid.count():
            item = self.table_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.table_cards.clear()

        # Cập nhật filter labels
        using = sum(1 for t in self.all_tables if t.status == TableStatus.USING)
        empty = len(self.all_tables) - using
        self.rb_all.setText(f"Tất cả ({len(self.all_tables)})")
        self.rb_using.setText(f"Sử dụng ({using})")
        self.rb_empty.setText(f"Còn trống ({empty})")

        # Lấy bàn trang hiện tại
        start = self.current_page * self.tables_per_page
        end = start + self.tables_per_page
        tables_page = self.filtered_tables[start:end]

        COLS = 5
        ROWS = 5

        for idx, table in enumerate(tables_page):
            order_data = None
            if table.status == TableStatus.USING:
                order = self.order_service.get_active_order(table.id)
                if order:
                    items_count = sum(i.quantity for i in order.items)
                    order_data = {
                        'total': order.subtotal,
                        'items_count': items_count,
                        'time': order.created_at.strftime("%H:%M"),
                    }

            card = TableCard(table, self.select_table, order_data)
            self.table_cards[table.id] = card
            row = idx // COLS
            col = idx % COLS
            self.table_grid.addWidget(card, row, col)

        # ✅ Stretch đều tất cả cột và hàng
        for col in range(COLS):
            self.table_grid.setColumnStretch(col, 1)
        for row in range(ROWS):
            self.table_grid.setRowStretch(row, 1)

        # Pagination
        self.lbl_page.setText(f"{self.current_page + 1} / {self.total_pages}")
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < self.total_pages - 1)
    def _on_prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._render_table_grid()

    def _on_next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._render_table_grid()

    # ── PRODUCTS ──────────────────────────────────────────────
    def _load_product_grid(self, keyword=""):
        # Xóa grid cũ
        while self.product_grid.count():
            item = self.product_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # ✅ Filter theo keyword → category → tất cả
        if keyword:
            products = self.product_repo.search(keyword)
        elif self.selected_category is not None:
            products = self.product_repo.get_by_category(self.selected_category)
        else:
            products = self.product_repo.get_all_active()

        COLS = 4
        for idx, product in enumerate(products):
            btn = self._make_product_card(product)
            self.product_grid.addWidget(btn, idx // COLS, idx % COLS)

        # Stretch để fill full width
        for col in range(COLS):
            self.product_grid.setColumnStretch(col, 1)

        # Fill ô trống hàng cuối
        total = len(products)
        remainder = total % COLS
        if remainder != 0:
            last_row = total // COLS
            for col in range(remainder, COLS):
                spacer = QWidget()
                spacer.setSizePolicy(
                    QSizePolicy.Policy.Expanding,
                    QSizePolicy.Policy.Fixed
                )
                spacer.setFixedHeight(80)
                self.product_grid.addWidget(spacer, last_row, col)

    def _make_product_card(self, product) -> QPushButton:
        if product.has_size and product.sizes:
            min_delta = min(s.price_delta for s in product.sizes)
            price_text = f"từ {(product.base_price + min_delta):,}₫"
        else:
            price_text = f"{product.base_price:,}₫"

        btn = QPushButton(f"{product.name}\n{price_text}")
        btn.setFixedHeight(80)
        btn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        btn.setFont(QFont("Segoe UI", 10))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: white; color: #1E2D3D;
                border: 1.5px solid #BBDEFB;
                border-radius: 10px;
                font-size: 11px; font-weight: bold;
                padding: 4px; text-align: center;
            }
            QPushButton:hover {
                background: #E3F2FD;
                border: 2px solid #1565C0;
                color: #1565C0;
            }
            QPushButton:pressed { background: #BBDEFB; }
        """)
        btn.clicked.connect(
            lambda checked, p=product: self.add_product(p)
        )
        return btn

    # ── SWITCH VIEW ───────────────────────────────────────────
    def _show_table_view(self):
        # Hiện table, ẩn product
        self.scroll_area.setVisible(True)
        self.scroll_product.setVisible(False)
        # Hiện filter bàn, ẩn category bar
        self.filter_widget.setVisible(True)
        self.category_scroll.setVisible(False)

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

        # Ẩn table, hiện product
        self.scroll_area.setVisible(False)
        self.scroll_product.setVisible(True)
        # Ẩn filter bàn, hiện category bar
        self.filter_widget.setVisible(False)
        self.category_scroll.setVisible(True)
        self.pagination_bar.setVisible(False)

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

        # ✅ Load categories + reset về Tất cả
        self._load_categories()
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

        has_size = product.has_size and product.sizes
        has_topping = bool(product.available_toppings)

        if has_size or has_topping:
            from ui.dialogs.product_dialog import ProductDialog
            dialog = ProductDialog(product, self)
            if dialog.exec():
                result = dialog.get_result()
                size_name = result["size"].size if result["size"] else ""
                self.order_controller.add_product(
                    self.current_order,
                    product.id,
                    size=size_name,
                )
        else:
            self.order_controller.add_product(
                self.current_order, product.id
            )

        self.current_order = self.order_service.get_active_order(
            self.current_table.id
        )
        self.order_panel.load_order(
            self.current_order, self.current_table.name
        )
        self.order_panel.set_notify_state("pending")

    def _on_notify(self):
        if not self.current_order or not self.current_order.items:
            QMessageBox.warning(self, "Thông báo", "Chưa có món nào trong order!")
            return
        from ui.dialogs.notify_dialog import NotifyDialog
        dialog = NotifyDialog(self.current_order, self.current_table, self)
        if dialog.exec():
            self.order_panel.set_notify_state("sent")  # ← THÊM DÒNG NÀY

    def _on_qty_change(self, item, delta: int):
        """Tăng/giảm số lượng món"""
        new_qty = item.quantity + delta
        if new_qty <= 0:
            # Hỏi xóa luôn
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "Xóa món?",
                f"Xóa '{item.product_name}' khỏi order?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._on_delete_item(item)
            return

        try:
            self.order_service.update_item_quantity(item.id, new_qty)
            self.current_order = self.order_service.get_active_order(
                self.current_table.id
            )
            self.order_panel.load_order(
                self.current_order, self.current_table.name
            )
            # Đánh dấu có thay đổi chưa thông báo
            self.order_panel.set_notify_state("pending")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Lỗi", str(e))

    def _on_note_change(self, item, note: str):
        """Lưu ghi chú món"""
        try:
            item.note = note
            self.session.commit()
            self.current_order = self.order_service.get_active_order(
                self.current_table.id
            )
            self.order_panel.load_order(
                self.current_order, self.current_table.name
            )
        except Exception as e:
            self.session.rollback()
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Lỗi", str(e))

    def _on_delete_item(self, item):
        try:
            self.order_service.remove_item(item.id)
            self.current_order = self.order_service.get_active_order(
                self.current_table.id
            )
            self.order_panel.load_order(
                self.current_order, self.current_table.name
            )
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
            self.current_order = None
            self.current_table = None
            self.order_panel.load_order(None, "")
            self._show_table_view()
            self._refresh_cards()

    def _on_print_temp(self):
        if not self.current_order or not self.current_order.items:
            QMessageBox.warning(self, "Thông báo", "Chưa có món nào!")
            return
        from ui.dialogs.invoice_dialog import InvoiceDialog
        dialog = InvoiceDialog(
            self.current_order,
            self.current_table,
            mode="temp",
            parent=self
        )
        dialog.exec()

    def _on_transfer_table(self):
        if not self.current_order or not self.current_order.items:
            QMessageBox.warning(self, "Thông báo", "Chưa có món nào để chuyển bàn!")
            return

        empty_tables = [
            t for t in self.table_repo.get_all()
            if t.status == TableStatus.EMPTY
        ]

        if not empty_tables:
            QMessageBox.warning(self, "Thông báo", "Không còn bàn trống!")
            return

        from ui.dialogs.transfer_table_dialog import TransferTableDialog
        dialog = TransferTableDialog(
            empty_tables, self.current_table, self,
            title=f"Chuyển từ {self.current_table.name}",
            subtitle="Chọn bàn muốn chuyển tới",
            btn_color="#F57C00"
        )

        if dialog.exec():
            target_table = dialog.selected_table
            if not target_table:
                return
            try:
                self.current_order.table_id = target_table.id
                self.current_table.status = TableStatus.EMPTY
                target_table.status = TableStatus.USING
                self.session.commit()

                self.current_table = target_table
                self.current_order = self.order_service.get_active_order(target_table.id)
                self.order_panel.load_order(self.current_order, target_table.name)
                self._refresh_cards()
                QMessageBox.information(self, "Thành công", f"Đã chuyển sang {target_table.name}")
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Lỗi", str(e))

    def _on_merge_table(self):
        if not self.current_order or not self.current_order.items:
            QMessageBox.warning(self, "Thông báo", "Chưa có món nào để gộp bàn!")
            return

        using_tables = [
            t for t in self.table_repo.get_all()
            if t.status == TableStatus.USING and t.id != self.current_table.id
        ]

        if not using_tables:
            QMessageBox.warning(self, "Thông báo", "Không có bàn nào để gộp!")
            return

        from ui.dialogs.transfer_table_dialog import TransferTableDialog
        dialog = TransferTableDialog(
            using_tables, self.current_table, self,
            title="Gộp bàn",
            subtitle="Chọn bàn muốn gộp vào",
            btn_color="#6A1B9A"
        )

        if dialog.exec():
            target_table = dialog.selected_table
            if not target_table:
                return
            try:
                target_order = self.order_service.get_active_order(target_table.id)
                if not target_order:
                    QMessageBox.warning(self, "Lỗi", "Không tìm thấy order bàn đích!")
                    return

                for item in list(self.current_order.items):
                    item.order_id = target_order.id
                self.session.flush()

                old_order = self.current_order
                self.current_table.status = TableStatus.EMPTY
                self.session.commit()

                self.current_order = self.order_service.get_active_order(target_table.id)
                self.current_table = target_table

                try:
                    self.session.delete(old_order)
                    self.session.commit()
                except:
                    self.session.rollback()

                self.order_panel.load_order(self.current_order, target_table.name)
                self._refresh_cards()
                QMessageBox.information(self, "Thành công", f"Đã gộp vào {target_table.name}")
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Lỗi", str(e))

    def _refresh_cards(self):
        self.current_page = 0  # Reset về trang 1
        self._load_tables()

    def _show_staff_menu(self):
        from PyQt6.QtWidgets import QMenu, QWidgetAction
        from PyQt6.QtGui import QAction

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #E0E8F5;
                border-radius: 12px;
                padding: 6px;
                font-size: 13px;
            }
            QMenu::item {
                padding: 10px 20px 10px 12px;
                border-radius: 8px;
                color: #1E2D3D;
            }
            QMenu::item:selected {
                background: #EBF5FF;
                color: #1565C0;
            }
            QMenu::separator {
                height: 1px;
                background: #EEF2F8;
                margin: 4px 8px;
            }
        """)

        # ── Header tài khoản ──────────────────────────────────────
        header_action = QWidgetAction(menu)
        header_w = QWidget()
        header_w.setStyleSheet("background: #F5F8FF; border-radius: 8px;")
        header_l = QHBoxLayout(header_w)
        header_l.setContentsMargins(12, 10, 12, 10)
        header_l.setSpacing(10)

        avatar = QLabel("👤")
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("""
            background: #1565C0;
            border-radius: 20px;
            font-size: 18px;
        """)

        info = QVBoxLayout()
        info.setSpacing(2)
        lbl_name = QLabel(self.user.full_name if self.user else "Staff")
        lbl_name.setStyleSheet(
            "font-weight: bold; font-size: 13px; color: #1E2D3D;"
        )
        lbl_role = QLabel(f"🟢  {self.user.role.value if self.user else 'STAFF'}")
        lbl_role.setStyleSheet("font-size: 11px; color: #888;")
        info.addWidget(lbl_name)
        info.addWidget(lbl_role)

        header_l.addWidget(avatar)
        header_l.addLayout(info)
        header_action.setDefaultWidget(header_w)
        menu.addAction(header_action)
        menu.addSeparator()

        # ── Các tùy chọn ──────────────────────────────────────────
        act_info = QAction("👤  Thông tin tài khoản", self)
        act_info.triggered.connect(self._show_account_info)
        menu.addAction(act_info)

        act_pwd = QAction("🔒  Đổi mật khẩu", self)
        act_pwd.triggered.connect(self._show_change_password)
        menu.addAction(act_pwd)

        act_history = QAction("🕐  Lịch sử ca làm việc", self)
        act_history.triggered.connect(self._show_shift_history)
        menu.addAction(act_history)

        menu.addSeparator()

        act_logout = QAction("🚪  Đăng xuất", self)
        act_logout.triggered.connect(self._on_logout)
        act_logout.setFont(QFont("Segoe UI", 11))
        menu.addAction(act_logout)

        # Hiện menu tại vị trí nút
        pos = self.menu_btn.mapToGlobal(
            self.menu_btn.rect().bottomRight()
        )
        from PyQt6.QtCore import QPoint
        menu.exec(pos - QPoint(menu.sizeHint().width(), 0))

    def _show_account_info(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

        d = QDialog(self)
        d.setWindowTitle("Thông tin tài khoản")
        d.setFixedWidth(340)
        d.setStyleSheet("background: white;")

        layout = QVBoxLayout(d)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("background: #1565C0; border-radius: 0px;")
        h = QVBoxLayout(header)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_av = QLabel("👤")
        lbl_av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_av.setStyleSheet("font-size: 30px;")
        h.addWidget(lbl_av)
        layout.addWidget(header)

        # Info
        body = QWidget()
        body.setStyleSheet("background: white;")
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(20, 16, 20, 16)
        body_l.setSpacing(10)

        for label, value in [
            ("Họ và tên", self.user.full_name if self.user else "—"),
            ("Tên đăng nhập", self.user.username if self.user else "—"),
            ("Vai trò", self.user.role.value if self.user else "—"),
            ("Trạng thái", "🟢 Đang hoạt động"),
        ]:
            row = QHBoxLayout()
            lbl_k = QLabel(label + ":")
            lbl_k.setFixedWidth(120)
            lbl_k.setStyleSheet("color: #888; font-size: 13px;")
            lbl_v = QLabel(value)
            lbl_v.setStyleSheet(
                "color: #1E2D3D; font-size: 13px; font-weight: bold;"
            )
            row.addWidget(lbl_k)
            row.addWidget(lbl_v, 1)
            body_l.addLayout(row)

        btn_close = QPushButton("Đóng")
        btn_close.setFixedHeight(38)
        btn_close.setStyleSheet("""
            QPushButton {
                background: #1565C0; color: white;
                border: none; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        btn_close.clicked.connect(d.accept)
        body_l.addSpacing(8)
        body_l.addWidget(btn_close)

        layout.addWidget(body)
        d.exec()

    def _show_change_password(self):
        from PyQt6.QtWidgets import (
            QDialog, QVBoxLayout, QLabel,
            QLineEdit, QPushButton, QWidget, QMessageBox
        )
        import hashlib

        d = QDialog(self)
        d.setWindowTitle("Đổi mật khẩu")
        d.setFixedWidth(340)
        d.setStyleSheet("background: white;")

        layout = QVBoxLayout(d)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        style = """
            QLineEdit {
                background: #F5F8FF; border: 1.5px solid #DDEAF8;
                border-radius: 8px; padding: 0 12px;
                height: 40px; font-size: 13px;
            }
            QLineEdit:focus { border: 1.5px solid #1565C0; }
        """

        lbl_title = QLabel("🔒  Đổi mật khẩu")
        lbl_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #1565C0;")
        layout.addWidget(lbl_title)

        lbl_old = QLabel("Mật khẩu hiện tại:")
        lbl_old.setStyleSheet("color: #555; font-size: 12px; font-weight: bold;")
        inp_old = QLineEdit()
        inp_old.setEchoMode(QLineEdit.EchoMode.Password)
        inp_old.setPlaceholderText("Nhập mật khẩu cũ...")
        inp_old.setStyleSheet(style)

        lbl_new = QLabel("Mật khẩu mới:")
        lbl_new.setStyleSheet("color: #555; font-size: 12px; font-weight: bold;")
        inp_new = QLineEdit()
        inp_new.setEchoMode(QLineEdit.EchoMode.Password)
        inp_new.setPlaceholderText("Nhập mật khẩu mới...")
        inp_new.setStyleSheet(style)

        lbl_confirm = QLabel("Xác nhận mật khẩu mới:")
        lbl_confirm.setStyleSheet("color: #555; font-size: 12px; font-weight: bold;")
        inp_confirm = QLineEdit()
        inp_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        inp_confirm.setPlaceholderText("Nhập lại mật khẩu mới...")
        inp_confirm.setStyleSheet(style)

        lbl_err = QLabel("")
        lbl_err.setStyleSheet("""
            color: #E53935; font-size: 12px;
            background: #FFEBEE; border-radius: 6px; padding: 6px;
        """)
        lbl_err.setVisible(False)

        def on_save():
            old = inp_old.text().strip()
            new = inp_new.text().strip()
            confirm = inp_confirm.text().strip()

            if not old or not new or not confirm:
                lbl_err.setText("⚠  Vui lòng nhập đầy đủ thông tin!")
                lbl_err.setVisible(True)
                return

            old_hash = hashlib.sha256(old.encode()).hexdigest()
            if self.user.password_hash != old_hash:
                lbl_err.setText("⚠  Mật khẩu hiện tại không đúng!")
                lbl_err.setVisible(True)
                return

            if new != confirm:
                lbl_err.setText("⚠  Mật khẩu mới không khớp!")
                lbl_err.setVisible(True)
                return

            if len(new) < 6:
                lbl_err.setText("⚠  Mật khẩu phải có ít nhất 6 ký tự!")
                lbl_err.setVisible(True)
                return

            self.user.password_hash = hashlib.sha256(new.encode()).hexdigest()
            self.session.commit()
            QMessageBox.information(d, "Thành công", "Đổi mật khẩu thành công!")
            d.accept()

        btn_save = QPushButton("💾  Lưu mật khẩu mới")
        btn_save.setFixedHeight(40)
        btn_save.setStyleSheet("""
            QPushButton {
                background: #1565C0; color: white;
                border: none; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        btn_save.clicked.connect(on_save)

        for w in [lbl_title, lbl_old, inp_old,
                  lbl_new, inp_new, lbl_confirm,
                  inp_confirm, lbl_err, btn_save]:
            layout.addWidget(w)

        d.exec()

    def _show_shift_history(self):
        from PyQt6.QtWidgets import (
            QDialog, QVBoxLayout, QTableWidget,
            QTableWidgetItem, QHeaderView, QPushButton, QLabel
        )
        from models.order import Order, OrderStatus
        from models.payment import Payment
        from datetime import datetime

        d = QDialog(self)
        d.setWindowTitle("Lịch sử ca làm việc")
        d.setFixedSize(560, 480)
        d.setStyleSheet("background: #F5F8FF;")

        layout = QVBoxLayout(d)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        lbl_title = QLabel("🕐  Lịch sử đơn hàng của bạn")
        lbl_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #1565C0;")
        layout.addWidget(lbl_title)

        # Lấy orders của user này
        orders = (
            self.session.query(Order, Payment)
            .outerjoin(Payment, Payment.order_id == Order.id)
            .filter(Order.user_id == self.current_user_id)
            .order_by(Order.created_at.desc())
            .limit(50)
            .all()
        )

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(
            ["Bàn", "Số món", "Tổng tiền", "Trạng thái", "Thời gian"]
        )
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.Stretch
        )
        table.setStyleSheet("""
            QTableWidget {
                background: white; border-radius: 10px;
                gridline-color: #EEF2F8; font-size: 12px; border: none;
            }
            QHeaderView::section {
                background: #F5F8FF; color: #555;
                font-weight: bold; border: none; padding: 8px;
            }
            QTableWidget::item { padding: 6px; border: none; }
            QTableWidget::item:selected { background: #E3F2FD; }
        """)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setRowCount(len(orders))

        status_map = {
            "ACTIVE": ("🟡 Đang mở", "#F57F17"),
            "PAID": ("✅ Đã thanh toán", "#2E7D32"),
            "CANCELLED": ("❌ Đã hủy", "#E53935"),
        }

        for row, (order, payment) in enumerate(orders):
            table_name = order.table.name if order.table else "—"
            items_count = sum(i.quantity for i in order.items)
            total = payment.total_amount if payment else order.subtotal
            status_txt, status_color = status_map.get(
                order.status.value, ("—", "#888")
            )
            time_str = order.created_at.strftime("%d/%m/%Y %H:%M")

            items_data = [
                (table_name, Qt.AlignmentFlag.AlignCenter),
                (str(items_count), Qt.AlignmentFlag.AlignCenter),
                (f"{total:,}₫", Qt.AlignmentFlag.AlignRight),
                (status_txt, Qt.AlignmentFlag.AlignCenter),
                (time_str, Qt.AlignmentFlag.AlignCenter),
            ]

            for col, (text, align) in enumerate(items_data):
                item = QTableWidgetItem(text)
                item.setTextAlignment(align)
                if col == 3:
                    item.setForeground(QColor(status_color))
                table.setItem(row, col, item)
            table.setRowHeight(row, 40)

        layout.addWidget(table)

        btn_close = QPushButton("Đóng")
        btn_close.setFixedHeight(38)
        btn_close.setStyleSheet("""
            QPushButton {
                background: #1565C0; color: white;
                border: none; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        btn_close.clicked.connect(d.accept)
        layout.addWidget(btn_close)
        d.exec()

    def _on_logout(self):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Đăng xuất",
            "Bạn có muốn đăng xuất không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from main import restart_to_login
            restart_to_login(self)
