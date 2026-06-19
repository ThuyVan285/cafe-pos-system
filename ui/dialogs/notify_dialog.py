# FILE: ui/dialogs/notify_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import qtawesome as qta

class NotifyDialog(QDialog):

    def __init__(self, order, table, parent=None):
        super().__init__(parent)
        self.order = order
        self.table = table

        self.setWindowTitle("Thông báo pha chế")
        self.setFixedWidth(400)
        self.setModal(True)
        self.setStyleSheet("background: #F5F8FF;")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── HEADER ────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet("background: #1565C0;")
        h = QHBoxLayout(header)
        h.setContentsMargins(16, 0, 16, 0)

        icon = QLabel()
        icon.setPixmap(qta.icon('fa5s.bell', color='white').pixmap(22, 22))

        title = QLabel(f"Thông báo pha chế  —  {self.table.name}")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
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
        body_layout.setSpacing(0)

        # Tiêu đề cột
        col_hdr = QWidget()
        col_hdr.setFixedHeight(30)
        col_hdr.setStyleSheet("""
            background: #EEF4FC;
            border-radius: 6px;
        """)
        ch = QHBoxLayout(col_hdr)
        ch.setContentsMargins(10, 0, 10, 0)

        for text, stretch in [("Món", 1), ("Size", 0), ("SL", 0)]:
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #888; font-size: 12px; font-weight: bold;")
            if not stretch:
                lbl.setFixedWidth(50)
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ch.addWidget(lbl, stretch)

        body_layout.addWidget(col_hdr)
        body_layout.addSpacing(8)

        # Danh sách món
        for idx, item in enumerate(self.order.items, 1):
            row = QWidget()
            row.setStyleSheet(f"""
                background: {'#F8FAFF' if idx % 2 == 0 else 'white'};
                border-radius: 6px;
            """)
            row.setFixedHeight(38)

            r = QHBoxLayout(row)
            r.setContentsMargins(10, 0, 10, 0)

            # Số thứ tự + tên
            lbl_name = QLabel(f"{idx}.  {item.product_name}")
            lbl_name.setStyleSheet(
                "color: #1E2D3D; font-size: 13px; font-weight: bold;"
            )

            # Size
            size_text = item.size if item.size else "—"
            lbl_size = QLabel(size_text)
            lbl_size.setFixedWidth(50)
            lbl_size.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_size.setStyleSheet("color: #555; font-size: 13px;")

            # Số lượng
            lbl_qty = QLabel(f"x{item.quantity}")
            lbl_qty.setFixedWidth(50)
            lbl_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_qty.setStyleSheet("""
                color: white;
                background: #1565C0;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
                padding: 2px 6px;
            """)

            r.addWidget(lbl_name, 1)
            r.addWidget(lbl_size)
            r.addWidget(lbl_qty)
            body_layout.addWidget(row)

        # Topping nếu có
        has_topping = any(item.toppings for item in self.order.items)
        if has_topping:
            body_layout.addSpacing(8)
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("color: #E0E8F5;")
            body_layout.addWidget(sep)
            body_layout.addSpacing(4)

            lbl_top_title = QLabel("Topping:")
            lbl_top_title.setStyleSheet(
                "color: #888; font-size: 12px; font-weight: bold;"
            )
            body_layout.addWidget(lbl_top_title)

            for item in self.order.items:
                if item.toppings:
                    topping_names = ", ".join(
                        t.topping_name for t in item.toppings
                    )
                    lbl_tp = QLabel(f"  • {item.product_name}: {topping_names}")
                    lbl_tp.setStyleSheet("color: #555; font-size: 12px;")
                    body_layout.addWidget(lbl_tp)

        layout.addWidget(body, 1)

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
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background: #CFD8DC; }
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_send = QPushButton("  Gửi thông báo")
        self.btn_send.setIcon(qta.icon('fa5s.bell', color='white'))
        self.btn_send.setStyleSheet("""
            QPushButton {
                background: #1565C0; color: white;
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        self.btn_send.clicked.connect(self._on_send)

        f.addWidget(btn_cancel, 1)
        f.addWidget(self.btn_send, 2)
        layout.addWidget(footer)

    def _on_send(self):
        self.btn_send.setText("  Đã gửi pha chế!")
        self.btn_send.setIcon(qta.icon('fa5s.check-circle', color='white'))
        self.btn_send.setStyleSheet("""
            QPushButton {
                background: #2E7D32; color: white;
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: bold;
            }
        """)
        self.btn_send.setEnabled(False)
        # Tự đóng sau 1.5 giây
        QTimer.singleShot(1500, self.accept)



