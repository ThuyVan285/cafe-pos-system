# FILE: ui/dialogs/login_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QWidget, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.db import get_session
from repositories.user_repository import UserRepository


class LoginDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logged_user = None
        self.setWindowTitle("Cafe POS — Đăng nhập")
        self.setFixedSize(420, 520)
        self.setModal(True)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint
        )
        self.setStyleSheet("background: #F0F4FA; border-radius: 16px;")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── HEADER ────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(160)
        header.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #1565C0, stop:1 #0D47A1
            );
            border-radius: 0px;
        """)
        h = QVBoxLayout(header)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.setSpacing(8)

        lbl_icon = QLabel("☕")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 48px;")

        lbl_title = QLabel("Cafe POS")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: white;")

        lbl_sub = QLabel("Hệ thống quản lý quán cà phê")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet("color: rgba(255,255,255,0.75); font-size: 12px;")

        h.addWidget(lbl_icon)
        h.addWidget(lbl_title)
        h.addWidget(lbl_sub)
        layout.addWidget(header)

        # ── FORM ──────────────────────────────────────────────
        form = QWidget()
        form.setStyleSheet("background: white;")
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(32, 28, 32, 28)
        form_layout.setSpacing(16)

        # Username
        lbl_user = QLabel("Tên đăng nhập")
        lbl_user.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #555;"
        )
        self.inp_username = QLineEdit()
        self.inp_username.setPlaceholderText("Nhập username...")
        self.inp_username.setFixedHeight(44)
        self.inp_username.setStyleSheet(self._input_style())
        self.inp_username.returnPressed.connect(
            lambda: self.inp_password.setFocus()
        )

        # Password
        lbl_pass = QLabel("Mật khẩu")
        lbl_pass.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #555;"
        )
        self.inp_password = QLineEdit()
        self.inp_password.setPlaceholderText("Nhập mật khẩu...")
        self.inp_password.setFixedHeight(44)
        self.inp_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_password.setStyleSheet(self._input_style())
        self.inp_password.returnPressed.connect(self._on_login)

        # Show password
        chk_show = QCheckBox("Hiện mật khẩu")
        chk_show.setStyleSheet("""
            QCheckBox { font-size: 12px; color: #888; }
            QCheckBox::indicator { width: 15px; height: 15px; }
        """)
        chk_show.toggled.connect(
            lambda checked: self.inp_password.setEchoMode(
                QLineEdit.EchoMode.Normal if checked
                else QLineEdit.EchoMode.Password
            )
        )

        # Error label
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_error.setStyleSheet("""
            color: #E53935;
            font-size: 12px;
            font-weight: bold;
            background: #FFEBEE;
            border-radius: 6px;
            padding: 6px;
        """)
        self.lbl_error.setVisible(False)

        # Login button
        self.btn_login = QPushButton("🔑  Đăng nhập")
        self.btn_login.setFixedHeight(46)
        self.btn_login.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background: #1565C0;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background: #1976D2; }
            QPushButton:pressed { background: #0D47A1; }
        """)
        self.btn_login.clicked.connect(self._on_login)

        form_layout.addWidget(lbl_user)
        form_layout.addWidget(self.inp_username)
        form_layout.addWidget(lbl_pass)
        form_layout.addWidget(self.inp_password)
        form_layout.addWidget(chk_show)
        form_layout.addWidget(self.lbl_error)
        form_layout.addSpacing(4)
        form_layout.addWidget(self.btn_login)

        layout.addWidget(form, 1)

        # ── FOOTER ────────────────────────────────────────────
        footer = QLabel("© 2025 Cafe POS System")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setFixedHeight(36)
        footer.setStyleSheet("color: #AAB4C0; font-size: 11px; background: white;")
        layout.addWidget(footer)

    @staticmethod
    def _input_style() -> str:
        return """
            QLineEdit {
                background: #F5F8FF;
                border: 1.5px solid #DDEAF8;
                border-radius: 10px;
                padding: 0 14px;
                font-size: 14px;
                color: #1E2D3D;
            }
            QLineEdit:focus {
                border: 1.5px solid #1565C0;
                background: white;
            }
        """

    def _on_login(self):
        username = self.inp_username.text().strip()
        password = self.inp_password.text().strip()

        if not username or not password:
            self._show_error("Vui lòng nhập đầy đủ thông tin!")
            return

        session = get_session()
        try:
            repo = UserRepository(session)
            user = repo.get_by_username(username)

            if not user or not user.verify_password(password):
                self._show_error("Tên đăng nhập hoặc mật khẩu không đúng!")
                self.inp_password.clear()
                self.inp_password.setFocus()
                return

            if not user.is_active:
                self._show_error("Tài khoản đã bị khóa!")
                return

            self.logged_user = user
            self.accept()

        except Exception as e:
            self._show_error(f"Lỗi hệ thống: {str(e)}")
        finally:
            session.close()

    def _show_error(self, msg: str):
        self.lbl_error.setText(f"⚠  {msg}")
        self.lbl_error.setVisible(True)