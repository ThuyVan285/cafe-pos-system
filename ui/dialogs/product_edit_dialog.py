# FILE: ui/dialogs/product_edit_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QCheckBox,
    QWidget, QScrollArea, QGridLayout, QMessageBox,
    QDoubleSpinBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import qtawesome as qta

class ProductEditDialog(QDialog):
    """Popup thêm/sửa sản phẩm đầy đủ"""

    def __init__(self, session, product=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.product = product
        self.is_edit = product is not None

        self.setWindowTitle("Sửa sản phẩm" if self.is_edit else "Thêm sản phẩm")
        self.setFixedWidth(480)
        self.setModal(True)
        self.setStyleSheet("background: #F5F8FF;")
        self._build()

        if self.is_edit:
            self._fill()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── HEADER ────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(52)
        header.setStyleSheet("background: #1565C0;")
        h = QHBoxLayout(header)
        h.setContentsMargins(16, 0, 16, 0)
        title_text = "Sửa sản phẩm" if self.is_edit else "Thêm sản phẩm mới"
        icon_name = 'fa5s.edit' if self.is_edit else 'fa5s.plus-circle'

        header_icon = QLabel()
        header_icon.setPixmap(qta.icon(icon_name, color='white').pixmap(18, 18))

        lbl = QLabel(f"  {title_text}")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet("color: white;")

        h.addWidget(header_icon)
        h.addWidget(lbl)
        layout.addWidget(header)

        # ── SCROLL BODY ───────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        body = QWidget()
        body.setStyleSheet("background: white;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 16, 20, 16)
        body_layout.setSpacing(14)

        # Tên sản phẩm
        body_layout.addWidget(self._lbl("Tên sản phẩm *"))
        self.inp_name = self._input("Nhập tên sản phẩm...")
        body_layout.addWidget(self.inp_name)

        # Danh mục
        body_layout.addWidget(self._lbl("Danh mục *"))
        self.cmb_category = QComboBox()
        self.cmb_category.setFixedHeight(40)
        self.cmb_category.setStyleSheet(self._combo_style())
        self._load_categories()
        body_layout.addWidget(self.cmb_category)

        # Giá cơ bản
        body_layout.addWidget(self._lbl("Giá cơ bản (₫) *"))
        self.inp_price = QLineEdit()
        self.inp_price.setPlaceholderText("Nhập giá...")
        self.inp_price.setFixedHeight(40)
        self.inp_price.setStyleSheet(self._input_style())
        body_layout.addWidget(self.inp_price)

        # Has size
        self.chk_size = QCheckBox("Sản phẩm có size (S / M / L)")
        self.chk_size.setStyleSheet("""
            QCheckBox { font-size: 13px; font-weight: bold; color: #1E2D3D; }
            QCheckBox::indicator { width: 18px; height: 18px; }
            QCheckBox::indicator:checked {
                background: #1565C0; border-radius: 4px; border: 2px solid #1565C0;
            }
            QCheckBox::indicator:unchecked {
                background: white; border-radius: 4px; border: 2px solid #BBDEFB;
            }
        """)
        self.chk_size.toggled.connect(self._on_size_toggled)
        body_layout.addWidget(self.chk_size)

        # Size prices
        self.size_widget = QWidget()
        self.size_widget.setStyleSheet("""
            background: #F5F8FF;
            border-radius: 10px;
            border: 1px solid #DDEAF8;
        """)
        size_layout = QGridLayout(self.size_widget)
        size_layout.setContentsMargins(12, 10, 12, 10)
        size_layout.setSpacing(8)

        for col, size in enumerate(["S", "M", "L"]):
            lbl_s = QLabel(f"Size {size} — chênh lệch (₫)")
            lbl_s.setStyleSheet("color: #888; font-size: 11px;")
            size_layout.addWidget(lbl_s, 0, col)

        self.inp_size_s = self._input("-5000", small=True)
        self.inp_size_m = self._input("0", small=True)
        self.inp_size_l = self._input("5000", small=True)

        size_layout.addWidget(self.inp_size_s, 1, 0)
        size_layout.addWidget(self.inp_size_m, 1, 1)
        size_layout.addWidget(self.inp_size_l, 1, 2)

        self.size_widget.setVisible(False)
        body_layout.addWidget(self.size_widget)

        # Has topping
        self.chk_topping = QCheckBox("Sản phẩm có topping")
        self.chk_topping.setStyleSheet(self.chk_size.styleSheet())
        self.chk_topping.toggled.connect(self._on_topping_toggled)
        body_layout.addWidget(self.chk_topping)

        # Topping list
        self.topping_widget = QWidget()
        self.topping_widget.setStyleSheet("""
            background: #F5F8FF;
            border-radius: 10px;
            border: 1px solid #DDEAF8;
        """)
        topping_layout = QVBoxLayout(self.topping_widget)
        topping_layout.setContentsMargins(12, 10, 12, 10)
        topping_layout.setSpacing(6)

        lbl_tp = QLabel("Chọn topping cho sản phẩm:")
        lbl_tp.setStyleSheet("color: #888; font-size: 11px; font-weight: bold;")
        topping_layout.addWidget(lbl_tp)

        self.topping_checks = {}
        toppings = self._get_all_toppings()
        grid = QGridLayout()
        grid.setSpacing(6)
        for idx, t in enumerate(toppings):
            chk = QCheckBox(f"{t.name}  (+{t.price:,}₫)")
            chk.setStyleSheet("""
                QCheckBox { font-size: 12px; color: #1E2D3D; }
                QCheckBox::indicator { width: 15px; height: 15px; }
            """)
            self.topping_checks[t.id] = (chk, t)
            grid.addWidget(chk, idx // 2, idx % 2)
        topping_layout.addLayout(grid)

        self.topping_widget.setVisible(False)
        body_layout.addWidget(self.topping_widget)

        # Active
        self.chk_active = QCheckBox("Hiển thị sản phẩm (đang kinh doanh)")
        self.chk_active.setChecked(True)
        self.chk_active.setStyleSheet(self.chk_size.styleSheet())
        body_layout.addWidget(self.chk_active)

        scroll.setWidget(body)
        layout.addWidget(scroll, 1)

        # ── FOOTER ────────────────────────────────────────────
        footer = QWidget()
        footer.setFixedHeight(60)
        footer.setStyleSheet("background: white; border-top: 1px solid #E0E8F5;")
        f = QHBoxLayout(footer)
        f.setContentsMargins(16, 10, 16, 10)
        f.setSpacing(10)

        btn_cancel = QPushButton("Hủy")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #ECEFF1; color: #546E7A;
                border: none; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #CFD8DC; }
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("  Lưu sản phẩm")
        btn_save.setIcon(qta.icon('fa5s.save', color='white'))
        btn_save.setFixedHeight(38)
        btn_save.setStyleSheet("""
            QPushButton {
                background: #1565C0; color: white;
                border: none; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        btn_save.clicked.connect(self._on_save)

        f.addWidget(btn_cancel, 1)
        f.addWidget(btn_save, 2)
        layout.addWidget(footer)

    # ── HELPERS ───────────────────────────────────────────────
    def _lbl(self, text) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #555; font-size: 12px; font-weight: bold;")
        return lbl

    def _input(self, placeholder="", small=False) -> QLineEdit:
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(36 if small else 40)
        inp.setStyleSheet(self._input_style())
        return inp

    @staticmethod
    def _input_style() -> str:
        return """
            QLineEdit {
                background: #F5F8FF; border: 1.5px solid #DDEAF8;
                border-radius: 8px; padding: 0 12px;
                font-size: 13px; color: #1E2D3D;
            }
            QLineEdit:focus { border: 1.5px solid #1565C0; background: white; }
        """

    @staticmethod
    def _combo_style() -> str:
        return """
            QComboBox {
                background: #F5F8FF; border: 1.5px solid #DDEAF8;
                border-radius: 8px; padding: 0 12px;
                font-size: 13px; color: #1E2D3D;
            }
            QComboBox:focus { border: 1.5px solid #1565C0; }
            QComboBox::drop-down { border: none; }
        """

    def _load_categories(self):
        from models.category import Category
        cats = self.session.query(Category).order_by(Category.name).all()
        self.categories = cats
        for cat in cats:
            self.cmb_category.addItem(cat.name, cat.id)

    def _get_all_toppings(self):
        from models.product import Topping
        return self.session.query(Topping).all()

    def _on_size_toggled(self, checked):
        self.size_widget.setVisible(checked)

    def _on_topping_toggled(self, checked):
        self.topping_widget.setVisible(checked)

    # ── FILL khi sửa ──────────────────────────────────────────
    def _fill(self):
        p = self.product
        self.inp_name.setText(p.name)
        self.inp_price.setText(str(p.base_price))
        self.chk_active.setChecked(p.is_active)

        # Category
        for i in range(self.cmb_category.count()):
            if self.cmb_category.itemData(i) == p.category_id:
                self.cmb_category.setCurrentIndex(i)
                break

        # Size
        if p.has_size and p.sizes:
            self.chk_size.setChecked(True)
            for s in p.sizes:
                if s.size == "S":
                    self.inp_size_s.setText(str(s.price_delta))
                elif s.size == "M":
                    self.inp_size_m.setText(str(s.price_delta))
                elif s.size == "L":
                    self.inp_size_l.setText(str(s.price_delta))

        # Topping
        current_topping_ids = {pt.topping_id for pt in p.product_toppings}
        if current_topping_ids:
            self.chk_topping.setChecked(True)
            for tid, (chk, t) in self.topping_checks.items():
                if tid in current_topping_ids:
                    chk.setChecked(True)

    # ── SAVE ──────────────────────────────────────────────────
    def _on_save(self):
        name = self.inp_name.text().strip()
        price_text = self.inp_price.text().strip()
        category_id = self.cmb_category.currentData()

        if not name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên sản phẩm!")
            return
        if not price_text:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập giá!")
            return

        try:
            price = int(price_text.replace(",", ""))
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Giá không hợp lệ!")
            return

        has_size    = self.chk_size.isChecked()
        has_topping = self.chk_topping.isChecked()
        is_active   = self.chk_active.isChecked()

        try:
            from models.product import Product, ProductSize, ProductTopping

            if self.is_edit:
                p = self.product
                p.name        = name
                p.base_price  = price
                p.category_id = category_id
                p.has_size    = has_size
                p.is_active   = is_active

                # Xóa sizes cũ rồi tạo lại
                for s in p.sizes:
                    self.session.delete(s)
                self.session.flush()

                # Xóa toppings cũ
                for pt in p.product_toppings:
                    self.session.delete(pt)
                self.session.flush()

            else:
                p = Product(
                    name=name,
                    base_price=price,
                    category_id=category_id,
                    has_size=has_size,
                    is_active=is_active,
                    description="",
                    image_path="",
                )
                self.session.add(p)
                self.session.flush()

            # Thêm sizes mới
            if has_size:
                try:
                    s_delta = int(self.inp_size_s.text() or "0")
                    m_delta = int(self.inp_size_m.text() or "0")
                    l_delta = int(self.inp_size_l.text() or "0")
                except ValueError:
                    s_delta, m_delta, l_delta = -5000, 0, 5000

                for size, delta in [("S", s_delta), ("M", m_delta), ("L", l_delta)]:
                    self.session.add(ProductSize(
                        product_id=p.id,
                        size=size,
                        price_delta=delta,
                    ))

            # Thêm toppings mới
            if has_topping:
                for tid, (chk, t) in self.topping_checks.items():
                    if chk.isChecked():
                        self.session.add(ProductTopping(
                            product_id=p.id,
                            topping_id=tid,
                        ))

            self.session.commit()
            QMessageBox.information(
                self, "Thành công",
                "Đã lưu sản phẩm thành công!"
            )
            self.accept()

        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(self, "Lỗi", str(e))