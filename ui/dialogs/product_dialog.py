# FILE: ui/dialogs/product_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QButtonGroup, QScrollArea,
    QWidget, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ProductDialog(QDialog):
    """Popup chọn size và topping khi click món"""

    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        self.selected_size = None
        self.selected_toppings = {}   # topping_id -> MockTopping
        self.confirmed = False

        self.setWindowTitle(product.name)
        self.setFixedWidth(420)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background: #F5F8FF;
            }
        """)

        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── HEADER ────────────────────────────────────────────
        header = QWidget()
        header.setStyleSheet("background: #1565C0;")
        header.setFixedHeight(60)
        h = QHBoxLayout(header)
        h.setContentsMargins(16, 0, 16, 0)

        lbl_name = QLabel(self.product.name)
        lbl_name.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_name.setStyleSheet("color: white;")

        self.lbl_price = QLabel(f"{self.product.base_price:,}₫")
        self.lbl_price.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.lbl_price.setStyleSheet("color: #FFD54F;")
        self.lbl_price.setAlignment(Qt.AlignmentFlag.AlignRight)

        h.addWidget(lbl_name, 1)
        h.addWidget(self.lbl_price)
        layout.addWidget(header)

        # ── BODY ──────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet("background: #F5F8FF;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(16, 14, 16, 14)
        body_layout.setSpacing(16)

        # SIZE
        if self.product.has_size and self.product.sizes:
            body_layout.addWidget(self._build_size_section())

        # TOPPING

        if hasattr(self.product, 'available_toppings') and self.product.available_toppings:
            body_layout.addWidget(self._build_topping_section())
        layout.addWidget(body, 1)

        # ── FOOTER ────────────────────────────────────────────
        footer = QWidget()
        footer.setFixedHeight(64)
        footer.setStyleSheet("""
            background: white;
            border-top: 1px solid #E0E8F8;
        """)
        f = QHBoxLayout(footer)
        f.setContentsMargins(16, 10, 16, 10)
        f.setSpacing(10)

        btn_cancel = QPushButton("Hủy")
        btn_cancel.setFixedHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #ECEFF1;
                color: #546E7A;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background: #CFD8DC; }
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_add = QPushButton("✚  Thêm vào order")
        self.btn_add.setFixedHeight(40)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background: #2E7D32;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background: #388E3C; }
        """)
        self.btn_add.clicked.connect(self._on_confirm)

        f.addWidget(btn_cancel, 1)
        f.addWidget(self.btn_add, 2)
        layout.addWidget(footer)

        # Nếu có size thì chọn mặc định size đầu tiên
        if self.product.has_size and self.product.sizes:
            first_btn = self.size_btn_group.buttons()[0]
            first_btn.setChecked(True)
            self._on_size_selected(self.product.sizes[0])

    # ── SIZE SECTION ──────────────────────────────────────────
    def _build_size_section(self) -> QWidget:
        section = QWidget()
        section.setStyleSheet("""
            QWidget { background: white; border-radius: 12px; }
        """)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        lbl = QLabel(" Chọn size")
        lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #1565C0;")
        layout.addWidget(lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.size_btn_group = QButtonGroup(self)
        self.size_btn_group.setExclusive(True)

        seen = set()
        unique_sizes = []
        for size in self.product.sizes:
            if size.size not in seen:
                seen.add(size.size)
                unique_sizes.append(size)

        for size in unique_sizes:
            price = self.product.base_price + size.price_delta
            btn = QPushButton(f"{size.size}\n{price:,}₫")
            btn.setFixedSize(100, 56)
            btn.setCheckable(True)
            btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            btn.setStyleSheet(self._size_style(False))
            btn.toggled.connect(
                lambda checked, s=size, b=btn:
                self._on_size_toggled(s, b, checked)
            )
            self.size_btn_group.addButton(btn)
            btn_row.addWidget(btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)
        return section

    def _on_size_selected(self, size):
        self.selected_size = size
        self._update_price()

    @staticmethod
    def _size_style(active: bool) -> str:
        if active:
            return """
                QPushButton {
                    background: #1565C0;
                    color: white;
                    border: 2px solid #1565C0;
                    border-radius: 10px;
                    font-weight: bold;
                }
            """
        return """
            QPushButton {
                background: #F0F4FA;
                color: #1E2D3D;
                border: 2px solid #DDEAF8;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 2px solid #1565C0;
                background: #E3F2FD;
            }
        """

    # ── TOPPING SECTION ───────────────────────────────────────
    def _build_topping_section(self) -> QWidget:
        section = QWidget()
        section.setStyleSheet("""
            QWidget { background: white; border-radius: 12px; }
        """)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        lbl = QLabel("🧋  Chọn topping  (có thể chọn nhiều)")
        lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #1565C0;")
        layout.addWidget(lbl)

        grid = QGridLayout()
        grid.setSpacing(8)

        self.topping_buttons = {}

        toppings = self.product.available_toppings

        for idx, topping in enumerate(toppings):
            btn = QPushButton(f"{topping.name}\n+{topping.price:,}₫")
            btn.setFixedSize(120, 52)
            btn.setCheckable(True)
            btn.setFont(QFont("Segoe UI", 9))
            btn.setStyleSheet(self._topping_style(False))
            btn.toggled.connect(
                lambda checked, t=topping, b=btn:
                self._on_topping_toggled(t, b, checked)
            )
            self.topping_buttons[topping.id] = btn
            grid.addWidget(btn, idx // 3, idx % 3)

        layout.addLayout(grid)
        return section

    def _on_topping_toggled(self, topping, btn, checked):
        if checked:
            self.selected_toppings[topping.id] = topping
            btn.setStyleSheet(self._topping_style(True))
        else:
            self.selected_toppings.pop(topping.id, None)
            btn.setStyleSheet(self._topping_style(False))
        self._update_price()

    @staticmethod
    def _topping_style(active: bool) -> str:
        if active:
            return """
                QPushButton {
                    background: #E8F5E9;
                    color: #2E7D32;
                    border: 2px solid #2E7D32;
                    border-radius: 10px;
                    font-weight: bold;
                }
            """
        return """
            QPushButton {
                background: #F0F4FA;
                color: #1E2D3D;
                border: 2px solid #DDEAF8;
                border-radius: 10px;
            }
            QPushButton:hover {
                border: 2px solid #2E7D32;
                background: #F1F8E9;
            }
        """

    # ── PRICE UPDATE ──────────────────────────────────────────
    def _update_price(self):
        base = self.product.base_price
        size_extra = self.selected_size.price_delta if self.selected_size else 0
        topping_extra = sum(t.price for t in self.selected_toppings.values())
        total = base + size_extra + topping_extra
        self.lbl_price.setText(f"{total:,}₫")

    # ── CONFIRM ───────────────────────────────────────────────
    def _on_confirm(self):
        if self.product.has_size and not self.selected_size:
            return
        self.confirmed = True
        self.accept()

    def get_result(self):
        """Trả về dict kết quả sau khi confirm"""
        return {
            "product": self.product,
            "size": self.selected_size,
            "toppings": list(self.selected_toppings.values()),
        }

    def _on_size_toggled(self, size, btn, checked: bool):
        btn.setStyleSheet(self._size_style(checked))
        if checked:
            self._on_size_selected(size)
        for b in self.size_btn_group.buttons():
            if b is not btn:
                b.setStyleSheet(self._size_style(False))