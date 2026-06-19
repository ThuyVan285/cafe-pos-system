# FILE: ui/dialogs/payment_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QFrame, QCheckBox,
    QLineEdit, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import qtawesome as qta


class PaymentDialog(QDialog):

    def __init__(self, order, table, session, parent=None):
        super().__init__(parent)
        self.order = order
        self.table = table
        self.session = session
        self.selected_method = "CASH"
        self.apply_discount = False

        self.setWindowTitle("Thanh toán")
        self.setFixedWidth(460)
        self.setModal(True)
        self.setStyleSheet("background: #F5F8FF;")
        self._build()
        self._update_total()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── HEADER ────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet("background: #2E7D32;")
        h = QHBoxLayout(header)
        h.setContentsMargins(16, 0, 16, 0)

        icon = QLabel()
        icon.setPixmap(qta.icon('fa5s.credit-card', color='white').pixmap(22, 22))

        title = QLabel(f"Thanh toán  —  {self.table.name}")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")

        h.addWidget(icon)
        h.addSpacing(8)
        h.addWidget(title, 1)
        layout.addWidget(header)

        # ── BODY ──────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet("background: white;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(16, 14, 16, 14)
        body_layout.setSpacing(12)

        # Danh sách món
        items_widget = QWidget()
        items_widget.setStyleSheet("""
            background: #F8FAFF;
            border-radius: 10px;
            border: 1px solid #E0E8F5;
        """)
        items_layout = QVBoxLayout(items_widget)
        items_layout.setContentsMargins(12, 10, 12, 10)
        items_layout.setSpacing(6)

        for idx, item in enumerate(self.order.items, 1):
            row = QHBoxLayout()
            name = item.product_name
            if item.size:
                name += f" ({item.size})"
            lbl_name = QLabel(f"{idx}. {name}  x{item.quantity}")
            lbl_name.setStyleSheet("color: #1E2D3D; font-size: 13px;")
            lbl_price = QLabel(f"{item.total_price:,}₫")
            lbl_price.setStyleSheet(
                "color: #1E2D3D; font-size: 13px; font-weight: bold;"
            )
            lbl_price.setAlignment(Qt.AlignmentFlag.AlignRight)
            row.addWidget(lbl_name, 1)
            row.addWidget(lbl_price)
            items_layout.addLayout(row)

        # Đường kẻ
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #E0E8F5;")
        items_layout.addWidget(sep)

        # Tổng tạm tính
        sub_row = QHBoxLayout()
        lbl_sub = QLabel("Tạm tính:")
        lbl_sub.setStyleSheet("color: #888; font-size: 13px;")
        self.lbl_subtotal = QLabel(f"{self.order.subtotal:,}₫")
        self.lbl_subtotal.setStyleSheet("color: #555; font-size: 13px;")
        self.lbl_subtotal.setAlignment(Qt.AlignmentFlag.AlignRight)
        sub_row.addWidget(lbl_sub, 1)
        sub_row.addWidget(self.lbl_subtotal)
        items_layout.addLayout(sub_row)

        body_layout.addWidget(items_widget)

        # ── GIẢM GIÁ ──────────────────────────────────────────
        discount_widget = QWidget()
        discount_widget.setStyleSheet("""
            background: #FFF8E1;
            border-radius: 10px;
            border: 1px solid #FFE082;
        """)
        dw = QHBoxLayout(discount_widget)
        dw.setContentsMargins(12, 8, 12, 8)

        self.chk_discount = QCheckBox("  Giảm giá nhân viên (20%)")
        self.chk_discount.setIcon(qta.icon('fa5s.gift', color='#E65100'))
        self.chk_discount.setStyleSheet("""
            QCheckBox {
                font-size: 13px; font-weight: bold; color: #E65100;
            }
            QCheckBox::indicator { width: 18px; height: 18px; }
            QCheckBox::indicator:checked {
                background: #E65100; border-radius: 4px; border: 2px solid #E65100;
            }
            QCheckBox::indicator:unchecked {
                background: white; border-radius: 4px; border: 2px solid #FFB300;
            }
        """)
        self.chk_discount.toggled.connect(self._on_discount_toggled)

        self.lbl_discount_amt = QLabel("")
        self.lbl_discount_amt.setStyleSheet(
            "color: #E65100; font-size: 13px; font-weight: bold;"
        )
        self.lbl_discount_amt.setAlignment(Qt.AlignmentFlag.AlignRight)

        dw.addWidget(self.chk_discount, 1)
        dw.addWidget(self.lbl_discount_amt)
        body_layout.addWidget(discount_widget)

        # ── TỔNG TIỀN ─────────────────────────────────────────
        total_widget = QWidget()
        total_widget.setStyleSheet("""
            background: #E8F5E9;
            border-radius: 10px;
            border: 1px solid #A5D6A7;
        """)
        tw = QHBoxLayout(total_widget)
        tw.setContentsMargins(12, 10, 12, 10)

        lbl_total_title = QLabel("  Tổng thanh toán:")
        icon_total = qta.icon('fa5s.coins', color='#2E7D32')
        lbl_total_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_total_title.setStyleSheet("color: #2E7D32;")

        self.lbl_final = QLabel(f"{self.order.subtotal:,}₫")
        self.lbl_final.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.lbl_final.setStyleSheet("color: #2E7D32;")
        self.lbl_final.setAlignment(Qt.AlignmentFlag.AlignRight)

        tw.addWidget(lbl_total_title, 1)
        tw.addWidget(self.lbl_final)
        body_layout.addWidget(total_widget)

        total_row = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(icon_total.pixmap(18, 18))
        total_row.addWidget(icon_lbl)
        total_row.addWidget(lbl_total_title)

        # ── PHƯƠNG THỨC THANH TOÁN ────────────────────────────
        lbl_method = QLabel("Phương thức thanh toán:")
        lbl_method.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #444;"
        )
        body_layout.addWidget(lbl_method)

        method_row = QHBoxLayout()
        method_row.setSpacing(8)

        self.method_group = QButtonGroup(self)
        self.method_btns = {}

        methods = [
            ("CASH", "  Tiền mặt", 'fa5s.money-bill-wave'),
            ("TRANSFER", "  Chuyển khoản", 'fa5s.university'),
            ("CARD", "  Thẻ", 'fa5s.credit-card'),
        ]

        for code, label, icon_name in methods:
            btn = QPushButton(label)
            btn.setIcon(qta.icon(icon_name, color='#1E2D3D'))
            btn.setFixedHeight(40)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            btn.setStyleSheet(self._method_style(False))
            btn.toggled.connect(
                lambda checked, c=code, b=btn:
                    self._on_method(c, b, checked)
            )
            self.method_group.addButton(btn)
            self.method_btns[code] = btn
            method_row.addWidget(btn)

        body_layout.addLayout(method_row)

        # Chọn mặc định Tiền mặt
        self.method_btns["CASH"].setChecked(True)

        # ── TIỀN KHÁCH ĐƯA ───────────────────────────────────
        self.cash_widget = QWidget()
        cash_layout = QVBoxLayout(self.cash_widget)
        cash_layout.setContentsMargins(0, 0, 0, 0)
        cash_layout.setSpacing(6)

        lbl_cash = QLabel("Tiền khách đưa:")
        lbl_cash.setStyleSheet("font-size: 13px; font-weight: bold; color: #444;")
        cash_layout.addWidget(lbl_cash)

        input_row = QHBoxLayout()

        self.inp_cash = QLineEdit()
        self.inp_cash.setPlaceholderText("Nhập số tiền...")
        self.inp_cash.setFixedHeight(40)
        self.inp_cash.setStyleSheet("""
            QLineEdit {
                background: #F5F8FF;
                border: 1.5px solid #BBDEFB;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px; font-weight: bold;
                color: #1E2D3D;
            }
            QLineEdit:focus {
                border: 1.5px solid #1565C0;
                background: white;
            }
        """)
        self.inp_cash.textChanged.connect(self._on_cash_changed)

        input_row.addWidget(self.inp_cash)
        cash_layout.addLayout(input_row)

        # Tiền thừa
        change_row = QHBoxLayout()
        lbl_change_title = QLabel("Tiền thừa:")
        lbl_change_title.setStyleSheet("color: #888; font-size: 13px;")
        self.lbl_change = QLabel("0₫")
        self.lbl_change.setStyleSheet(
            "color: #1565C0; font-size: 14px; font-weight: bold;"
        )
        self.lbl_change.setAlignment(Qt.AlignmentFlag.AlignRight)
        change_row.addWidget(lbl_change_title, 1)
        change_row.addWidget(self.lbl_change)
        cash_layout.addLayout(change_row)

        body_layout.addWidget(self.cash_widget)
        layout.addWidget(body, 1)

        # ── FOOTER ────────────────────────────────────────────
        footer = QWidget()
        footer.setFixedHeight(64)
        footer.setStyleSheet("background: white; border-top: 1px solid #E0E8F5;")
        f = QHBoxLayout(footer)
        f.setContentsMargins(16, 10, 16, 10)
        f.setSpacing(10)

        btn_cancel = QPushButton("Hủy")
        btn_cancel.setFixedHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #ECEFF1; color: #546E7A;
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background: #CFD8DC; }
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_confirm = QPushButton("  Xác nhận thanh toán")
        self.btn_confirm.setIcon(qta.icon('fa5s.check-circle', color='white'))
        self.btn_confirm.setFixedHeight(40)
        self.btn_confirm.setStyleSheet("""
            QPushButton {
                background: #2E7D32; color: white;
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background: #388E3C; }
        """)
        self.btn_confirm.clicked.connect(self._on_confirm)

        f.addWidget(btn_cancel, 1)
        f.addWidget(self.btn_confirm, 2)
        layout.addWidget(footer)

    # ── HELPERS ───────────────────────────────────────────────
    @staticmethod
    def _method_style(active: bool) -> str:
        if active:
            return """
                QPushButton {
                    background: #1565C0; color: white;
                    border: 2px solid #1565C0; border-radius: 8px;
                    font-weight: bold;
                }
            """
        return """
            QPushButton {
                background: #F0F4FA; color: #1E2D3D;
                border: 2px solid #DDEAF8; border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 2px solid #1565C0; background: #E3F2FD;
            }
        """

    def _on_method(self, code, btn, checked):
        if checked:
            self.selected_method = code
            btn.setStyleSheet(self._method_style(True))
            # ✅ Kiểm tra trước khi dùng
            if hasattr(self, 'cash_widget'):
                self.cash_widget.setVisible(code == "CASH")
        else:
            btn.setStyleSheet(self._method_style(False))
    def _on_discount_toggled(self, checked):
        self.apply_discount = checked
        self._update_total()

    def _update_total(self):
        subtotal = self.order.subtotal
        if self.apply_discount:
            discount = int(subtotal * 0.20)
            final = subtotal - discount
            self.lbl_discount_amt.setText(f"-{discount:,}₫")
        else:
            discount = 0
            final = subtotal
            self.lbl_discount_amt.setText("")

        self.final_amount = final
        self.lbl_final.setText(f"{final:,}₫")
        self._on_cash_changed(self.inp_cash.text())

    def _on_cash_changed(self, text):
        try:
            cash = int(text.replace(",", "").replace(".", ""))
            change = cash - self.final_amount
            if change >= 0:
                self.lbl_change.setText(f"{change:,}₫")
                self.lbl_change.setStyleSheet(
                    "color: #2E7D32; font-size: 14px; font-weight: bold;"
                )
            else:
                self.lbl_change.setText(f"-{abs(change):,}₫")  # bỏ ⚠ text, dùng icon nếu cần
                self.lbl_change.setStyleSheet(
                    "color: #E53935; font-size: 14px; font-weight: bold;"
                )
        except ValueError:
            self.lbl_change.setText("0₫")

    def _on_confirm(self):
        from models.payment import PaymentMethod
        from services.payment_service import PaymentService

        try:
            method_map = {
                "CASH":     PaymentMethod.CASH,
                "TRANSFER": PaymentMethod.BANKING,
                "CARD":     PaymentMethod.CARD,
            }
            service = PaymentService(self.session)
            service.process_payment(
                self.order.id,
                method_map[self.selected_method],
                apply_discount=self.apply_discount,
            )

            self.btn_confirm.setText("  Thanh toán thành công!")
            self.btn_confirm.setIcon(qta.icon('fa5s.check-circle', color='white'))
            self.btn_confirm.setEnabled(False)
            QTimer.singleShot(1200, self.accept)

        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Lỗi", str(e))

    # Trong _on_confirm, sau khi thanh toán thành công:
    def _on_confirm(self):
        from models.payment import PaymentMethod
        from services.payment_service import PaymentService

        try:
            method_map = {
                "CASH": PaymentMethod.CASH,
                "TRANSFER": PaymentMethod.BANKING,
                "CARD": PaymentMethod.CARD,
            }
            service = PaymentService(self.session)
            payment = service.process_payment(
                self.order.id,
                method_map[self.selected_method],
                apply_discount=self.apply_discount,
            )

            # Lưu số tiền khách đưa
            try:
                cash_text = self.inp_cash.text().replace(",", "").replace(".", "")
                payment.amount_received = int(cash_text) if cash_text else self.final_amount
                payment.change_amount = payment.amount_received - payment.total_amount
                self.session.commit()
            except:
                pass

            # Hiện hóa đơn chính thức
            from ui.dialogs.invoice_dialog import InvoiceDialog
            invoice = InvoiceDialog(
                self.order,
                self.table,
                mode="final",
                payment=payment,
                parent=self.parent()
            )
            self.accept()
            invoice.exec()

        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Lỗi", str(e))