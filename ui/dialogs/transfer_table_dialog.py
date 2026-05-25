from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QScrollArea,
    QGridLayout,
    QHBoxLayout
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class TransferTableDialog(QDialog):

    def __init__(self, tables, current_table, parent=None,
                 title=None, subtitle=None, btn_color="#1565C0"):

        super().__init__(parent)

        self.empty_tables = tables
        self.current_table = current_table
        self.selected_table = None

        self._title = title or f"Chuyển từ {current_table.name}"
        self._subtitle = subtitle or "Chỉ hiển thị các bàn đang trống"
        self._btn_color = btn_color

        self.setWindowTitle(self._title)

        self.resize(620, 420)

        self.setStyleSheet("""
            QDialog {
                background: #EEF4FC;
            }
        """)

        self.build_ui()

    # =====================================================
    # UI
    # =====================================================
    def build_ui(self):

        root = QVBoxLayout(self)

        root.setContentsMargins(16, 16, 16, 16)

        root.setSpacing(12)

        # TITLE
        lbl_title = QLabel(self._title)

        lbl_title.setFont(
            QFont("Segoe UI", 15, QFont.Weight.Bold)
        )

        lbl_title.setStyleSheet("""
            color: #1565C0;
        """)

        root.addWidget(lbl_title)

        # SUBTITLE
        lbl_sub = QLabel(self._subtitle)

        lbl_sub.setStyleSheet("""
            color: #607D8B;
            font-size: 12px;
        """)

        root.addWidget(lbl_sub)

        # SCROLL
        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }

            QScrollBar:vertical {
                background: #DDE8F8;
                width: 6px;
                border-radius: 3px;
            }

            QScrollBar::handle:vertical {
                background: #90B4D8;
                border-radius: 3px;
            }
        """)

        container = QWidget()

        grid = QGridLayout(container)

        grid.setSpacing(12)

        grid.setAlignment(
            Qt.AlignmentFlag.AlignTop |
            Qt.AlignmentFlag.AlignLeft
        )

        COLS = 4

        for idx, table in enumerate(self.empty_tables):

            card = self.make_table_card(table)

            row = idx // COLS
            col = idx % COLS

            grid.addWidget(card, row, col)

        scroll.setWidget(container)

        root.addWidget(scroll, 1)

        # FOOTER
        footer = QHBoxLayout()

        footer.addStretch()

        btn_close = QPushButton("Đóng")

        btn_close.setFixedSize(110, 38)

        btn_close.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        btn_close.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #D0DCEB;
                border-radius: 8px;

                font-size: 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #F5F8FD;
            }
        """)

        btn_close.clicked.connect(self.reject)

        footer.addWidget(btn_close)

        root.addLayout(footer)

    # =====================================================
    # TABLE CARD
    # =====================================================
    def make_table_card(self, table):

        btn = QPushButton()

        btn.setFixedSize(130, 90)

        btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        btn.setText(
            f"🏠\n{table.name}"
        )

        btn.setStyleSheet(f"""
            QPushButton {{
                background: white;

                border: 2px solid #BBDEFB;
                border-radius: 14px;

                color: #1E2D3D;

                font-size: 13px;
                font-weight: bold;

                padding: 8px;
            }}

            QPushButton:hover {{
                background: #E3F2FD;

                border: 2px solid {self._btn_color};

                color: {self._btn_color};
            }}
        """)

        btn.clicked.connect(
            lambda: self.select_table(table)
        )

        return btn

    # =====================================================
    # SELECT
    # =====================================================
    def select_table(self, table):

        self.selected_table = table

        self.accept()