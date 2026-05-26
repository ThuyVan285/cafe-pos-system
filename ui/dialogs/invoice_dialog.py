# FILE: ui/dialogs/invoice_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime


class InvoiceDialog(QDialog):
    """Popup xem hóa đơn — dùng cho cả In tạm tính và In hóa đơn"""

    def __init__(self, order, table, mode="temp", payment=None, parent=None):
        super().__init__(parent)
        self.order = order
        self.table = table
        self.mode = mode        # "temp" = tạm tính, "final" = hóa đơn chính thức
        self.payment = payment  # Payment object (chỉ dùng khi mode="final")

        title = "In tạm tính" if mode == "temp" else "Hóa đơn thanh toán"
        self.setWindowTitle(title)
        self.setFixedWidth(400)
        self.setModal(True)
        self.setStyleSheet("background: white;")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── HEADER ────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(52)
        color = "#607D8B" if self.mode == "temp" else "#2E7D32"
        header.setStyleSheet(f"background: {color};")
        h = QHBoxLayout(header)
        h.setContentsMargins(16, 0, 16, 0)

        icon = "🖨" if self.mode == "temp" else "🧾"
        title = "Phiếu tạm tính" if self.mode == "temp" else "Hóa đơn thanh toán"
        lbl = QLabel(f"{icon}  {title}")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet("color: white;")
        h.addWidget(lbl)
        layout.addWidget(header)

        # ── SCROLL ────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        content = QWidget()
        content.setStyleSheet("background: white;")
        c = QVBoxLayout(content)
        c.setContentsMargins(24, 20, 24, 20)
        c.setSpacing(8)

        # Tên quán
        lbl_shop = QLabel("☕  CAFE POS")
        lbl_shop.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_shop.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_shop.setStyleSheet("color: #1565C0;")
        c.addWidget(lbl_shop)

        lbl_addr = QLabel("Đà Nẵng, Việt Nam")
        lbl_addr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_addr.setStyleSheet("color: #888; font-size: 12px;")
        c.addWidget(lbl_addr)

        c.addWidget(self._sep())

        # Thông tin hóa đơn
        now = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
        info_data = [
            ("Bàn:",        self.table.name),
            ("Thời gian:",  now),
        ]
        if self.mode == "final" and self.payment:
            method_map = {
                "CASH":     "Tiền mặt",
                "BANKING":  "Chuyển khoản",
                "CARD":     "Thẻ",
            }
            info_data.append((
                "Thanh toán:",
                method_map.get(self.payment.method.value, self.payment.method.value)
            ))

        for key, val in info_data:
            row = QHBoxLayout()
            lbl_k = QLabel(key)
            lbl_k.setStyleSheet("color: #888; font-size: 12px;")
            lbl_v = QLabel(val)
            lbl_v.setStyleSheet("color: #1E2D3D; font-size: 12px; font-weight: bold;")
            lbl_v.setAlignment(Qt.AlignmentFlag.AlignRight)
            row.addWidget(lbl_k)
            row.addWidget(lbl_v)
            c.addLayout(row)

        c.addWidget(self._sep())

        # Header cột
        col_hdr = QWidget()
        col_hdr.setFixedHeight(28)
        col_hdr.setStyleSheet("background: #F5F8FF; border-radius: 6px;")
        ch = QHBoxLayout(col_hdr)
        ch.setContentsMargins(8, 0, 8, 0)
        for text, stretch, align in [
            ("Món", 1, Qt.AlignmentFlag.AlignLeft),
            ("SL", 0, Qt.AlignmentFlag.AlignCenter),
            ("Đ.Giá", 0, Qt.AlignmentFlag.AlignRight),
            ("T.Tiền", 0, Qt.AlignmentFlag.AlignRight),
        ]:
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #888; font-size: 11px; font-weight: bold;")
            lbl.setAlignment(align)
            if not stretch:
                lbl.setFixedWidth(55)
            ch.addWidget(lbl, stretch)
        c.addWidget(col_hdr)

        # Danh sách món
        for item in self.order.items:
            name = item.product_name
            if item.size:
                name += f" ({item.size})"

            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 6, 0, 6)
            item_layout.setSpacing(2)

            row = QHBoxLayout()
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet(
                "color: #1E2D3D; font-size: 13px; font-weight: bold;"
            )
            lbl_name.setWordWrap(True)

            lbl_qty = QLabel(str(item.quantity))
            lbl_qty.setFixedWidth(55)
            lbl_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_qty.setStyleSheet("color: #555; font-size: 13px;")

            lbl_unit = QLabel(f"{item.unit_price:,}")
            lbl_unit.setFixedWidth(55)
            lbl_unit.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl_unit.setStyleSheet("color: #888; font-size: 12px;")

            lbl_total = QLabel(f"{item.total_price:,}")
            lbl_total.setFixedWidth(55)
            lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl_total.setStyleSheet(
                "color: #1E2D3D; font-size: 13px; font-weight: bold;"
            )

            row.addWidget(lbl_name, 1)
            row.addWidget(lbl_qty)
            row.addWidget(lbl_unit)
            row.addWidget(lbl_total)
            item_layout.addLayout(row)

            # Topping
            if item.toppings:
                topping_names = ", ".join(
                    t.topping_name for t in item.toppings
                )
                lbl_tp = QLabel(f"  + {topping_names}")
                lbl_tp.setStyleSheet("color: #90A4AE; font-size: 11px;")
                item_layout.addWidget(lbl_tp)

            item_widget.setStyleSheet(
                "border-bottom: 1px dashed #E0E8F5;"
            )
            c.addWidget(item_widget)

        c.addWidget(self._sep())

        # Tổng tiền
        subtotal = self.order.subtotal

        sub_row = QHBoxLayout()
        lbl_sub_k = QLabel("Tạm tính:")
        lbl_sub_k.setStyleSheet("color: #888; font-size: 13px;")
        lbl_sub_v = QLabel(f"{subtotal:,}₫")
        lbl_sub_v.setStyleSheet("color: #555; font-size: 13px;")
        lbl_sub_v.setAlignment(Qt.AlignmentFlag.AlignRight)
        sub_row.addWidget(lbl_sub_k, 1)
        sub_row.addWidget(lbl_sub_v)
        c.addLayout(sub_row)

        # Giảm giá (nếu có)
        if self.mode == "final" and self.payment and self.payment.discount_amount > 0:
            disc_row = QHBoxLayout()
            lbl_dk = QLabel(f"Giảm giá ({int(self.payment.discount_rate*100)}%):")
            lbl_dk.setStyleSheet("color: #E65100; font-size: 13px;")
            lbl_dv = QLabel(f"-{self.payment.discount_amount:,}₫")
            lbl_dv.setStyleSheet("color: #E65100; font-size: 13px; font-weight: bold;")
            lbl_dv.setAlignment(Qt.AlignmentFlag.AlignRight)
            disc_row.addWidget(lbl_dk, 1)
            disc_row.addWidget(lbl_dv)
            c.addLayout(disc_row)

        # Tổng cuối
        final = self.payment.total_amount if (
            self.mode == "final" and self.payment
        ) else subtotal

        c.addWidget(self._sep())

        total_widget = QWidget()
        total_widget.setStyleSheet("""
            background: #E8F5E9;
            border-radius: 10px;
        """)
        tw = QHBoxLayout(total_widget)
        tw.setContentsMargins(12, 10, 12, 10)

        lbl_tk = QLabel("TỔNG THANH TOÁN:")
        lbl_tk.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_tk.setStyleSheet("color: #2E7D32;")

        lbl_tv = QLabel(f"{final:,}₫")
        lbl_tv.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_tv.setStyleSheet("color: #2E7D32;")
        lbl_tv.setAlignment(Qt.AlignmentFlag.AlignRight)

        tw.addWidget(lbl_tk, 1)
        tw.addWidget(lbl_tv)
        c.addWidget(total_widget)

        # Tiền thừa (nếu là hóa đơn chính thức)
        if self.mode == "final" and self.payment:
            change = self.payment.amount_received - self.payment.total_amount
            if change >= 0:
                change_row = QHBoxLayout()
                lbl_ck = QLabel("Tiền khách đưa:")
                lbl_ck.setStyleSheet("color: #888; font-size: 12px;")
                lbl_cv = QLabel(f"{self.payment.amount_received:,}₫")
                lbl_cv.setStyleSheet("color: #555; font-size: 12px;")
                lbl_cv.setAlignment(Qt.AlignmentFlag.AlignRight)
                change_row.addWidget(lbl_ck, 1)
                change_row.addWidget(lbl_cv)
                c.addLayout(change_row)

                ret_row = QHBoxLayout()
                lbl_rk = QLabel("Tiền thừa:")
                lbl_rk.setStyleSheet("color: #888; font-size: 12px;")
                lbl_rv = QLabel(f"{change:,}₫")
                lbl_rv.setStyleSheet(
                    "color: #1565C0; font-size: 12px; font-weight: bold;"
                )
                lbl_rv.setAlignment(Qt.AlignmentFlag.AlignRight)
                ret_row.addWidget(lbl_rk, 1)
                ret_row.addWidget(lbl_rv)
                c.addLayout(ret_row)

        c.addSpacing(8)

        # Footer
        lbl_thanks = QLabel("Cảm ơn quý khách! Hẹn gặp lại 😊")
        lbl_thanks.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_thanks.setStyleSheet("color: #888; font-size: 12px;")
        c.addWidget(lbl_thanks)

        # Nếu là tạm tính thì hiện chữ "CHƯA THANH TOÁN"
        if self.mode == "temp":
            lbl_unpaid = QLabel("⚠  CHƯA THANH TOÁN")
            lbl_unpaid.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_unpaid.setStyleSheet(
                "color: #E53935; font-size: 13px; font-weight: bold;"
            )
            c.addWidget(lbl_unpaid)

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # ── FOOTER BUTTONS ────────────────────────────────────
        footer = QWidget()
        footer.setFixedHeight(60)
        footer.setStyleSheet("background: white; border-top: 1px solid #E0E8F5;")
        f = QHBoxLayout(footer)
        f.setContentsMargins(16, 10, 16, 10)
        f.setSpacing(10)

        btn_close = QPushButton("Đóng")
        btn_close.setFixedHeight(38)
        btn_close.setStyleSheet("""
            QPushButton {
                background: #ECEFF1; color: #546E7A;
                border: none; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #CFD8DC; }
        """)
        btn_close.clicked.connect(self.reject)

        btn_print = QPushButton("🖨  In hóa đơn")
        btn_print.setFixedHeight(38)
        color = "#607D8B" if self.mode == "temp" else "#2E7D32"
        btn_print.setStyleSheet(f"""
            QPushButton {{
                background: {color}; color: white;
                border: none; border-radius: 8px; font-weight: bold;
            }}
            QPushButton:hover {{ opacity: 0.85; }}
        """)
        btn_print.clicked.connect(self._on_print)

        f.addWidget(btn_close, 1)
        f.addWidget(btn_print, 2)
        layout.addWidget(footer)

    def _sep(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #E0E8F5;")
        return sep

    def _on_print(self):
        """In ra máy in thực tế hoặc lưu PDF"""
        from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
        from PyQt6.QtGui import QTextDocument

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec():
            doc = QTextDocument()
            doc.setHtml(self._generate_html())
            doc.print(printer)

    def _generate_html(self) -> str:
        """Tạo nội dung HTML để in"""
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        title = "PHIẾU TẠM TÍNH" if self.mode == "temp" else "HÓA ĐƠN THANH TOÁN"

        rows = ""
        for item in self.order.items:
            name = item.product_name
            if item.size:
                name += f" ({item.size})"
            rows += f"""
                <tr>
                    <td>{name}</td>
                    <td align='center'>{item.quantity}</td>
                    <td align='right'>{item.unit_price:,}</td>
                    <td align='right'><b>{item.total_price:,}</b></td>
                </tr>
            """
            if item.toppings:
                tp = ", ".join(t.topping_name for t in item.toppings)
                rows += f"<tr><td colspan='4' style='color:gray;font-size:11px'>  + {tp}</td></tr>"

        subtotal = self.order.subtotal
        final = self.payment.total_amount if (
            self.mode == "final" and self.payment
        ) else subtotal

        discount_row = ""
        if self.mode == "final" and self.payment and self.payment.discount_amount > 0:
            discount_row = f"""
                <tr>
                    <td colspan='3'>Giảm giá ({int(self.payment.discount_rate*100)}%):</td>
                    <td align='right' style='color:red'>-{self.payment.discount_amount:,}₫</td>
                </tr>
            """

        return f"""
        <html><body style='font-family: Arial; font-size: 13px; width: 300px;'>
            <h2 style='text-align:center; color:#1565C0;'>☕ CAFE POS</h2>
            <p style='text-align:center; color:gray;'>Đà Nẵng, Việt Nam</p>
            <hr/>
            <h3 style='text-align:center;'>{title}</h3>
            <p>Bàn: <b>{self.table.name}</b></p>
            <p>Thời gian: {now}</p>
            <hr/>
            <table width='100%' cellspacing='4'>
                <tr style='background:#f5f5f5;'>
                    <th align='left'>Món</th>
                    <th>SL</th>
                    <th align='right'>Đ.Giá</th>
                    <th align='right'>T.Tiền</th>
                </tr>
                {rows}
                <tr><td colspan='4'><hr/></td></tr>
                <tr>
                    <td colspan='3'>Tạm tính:</td>
                    <td align='right'>{subtotal:,}₫</td>
                </tr>
                {discount_row}
                <tr style='font-size:15px; color:green;'>
                    <td colspan='3'><b>TỔNG THANH TOÁN:</b></td>
                    <td align='right'><b>{final:,}₫</b></td>
                </tr>
            </table>
            <hr/>
            <p style='text-align:center; color:gray;'>Cảm ơn quý khách! Hẹn gặp lại 😊</p>
            {"<p style='text-align:center;color:red;'><b>⚠ CHƯA THANH TOÁN</b></p>" if self.mode == "temp" else ""}
        </body></html>
        """