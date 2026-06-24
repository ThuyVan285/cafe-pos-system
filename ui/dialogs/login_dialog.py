# FILE: ui/dialogs/login_dialog.py

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QWidget,
    QCheckBox,
    QHBoxLayout,
    QSizePolicy
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.db import get_session
from repositories.user_repository import UserRepository


class LoginDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.logged_user = None

        self.setWindowTitle("Cafe POS")

        # FIX KHUNG
        self.setFixedSize(430, 590)

        # WINDOW BUTTONS
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        self.setStyleSheet("""
            QDialog {
                background: #F4F7FB;
                border-radius: 18px;
            }
        """)

        self.build_ui()

    # UI
    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── HEADER ────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(190)
        header.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #1976D2, stop:1 #1565C0
            );
        """)
        hl = QVBoxLayout(header)
        hl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.setSpacing(4)
        hl.setContentsMargins(20, 16, 20, 16)

        lbl_logo = QLabel("☕")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet("font-size: 48px; background: transparent;")

        lbl_title = QLabel("Cafe POS")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: white; background: transparent;")

        lbl_sub = QLabel("Phần mềm quản lý quán cà phê")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet("color: rgba(255,255,255,0.78); font-size: 12px; background: transparent;")

        badge = QLabel("BÁN HÀNG  •  QUẢN LÝ  •  THỐNG KÊ")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedHeight(30)
        badge.setStyleSheet("""
            background: rgba(255,255,255,0.18);
            color: white; border-radius: 15px;
            padding-left: 16px; padding-right: 16px;
            font-size: 11px; font-weight: bold;
        """)

        hl.addWidget(lbl_logo)
        hl.addWidget(lbl_title)
        hl.addWidget(lbl_sub)
        hl.addSpacing(8)
        hl.addWidget(badge)
        root.addWidget(header)

        # ── BODY ──────────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet("background: white;")
        fl = QVBoxLayout(body)
        fl.setContentsMargins(36, 24, 36, 20)
        fl.setSpacing(0)

        # Tiêu đề form
        lbl_login = QLabel("Đăng nhập hệ thống")
        lbl_login.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_login.setStyleSheet("color: #0F172A;")
        fl.addWidget(lbl_login)

        lbl_desc = QLabel("Vui lòng nhập tài khoản để tiếp tục")
        lbl_desc.setStyleSheet("color: #94A3B8; font-size: 12px;")
        fl.addWidget(lbl_desc)
        fl.addSpacing(20)

        # Username
        lbl_user = QLabel("Tên đăng nhập")
        lbl_user.setStyleSheet("font-size: 12px; font-weight: bold; color: #475569;")
        fl.addWidget(lbl_user)
        fl.addSpacing(6)

        self.inp_username = QLineEdit()
        self.inp_username.setPlaceholderText("Nhập username...")
        self.inp_username.setFixedHeight(46)
        self.inp_username.setStyleSheet(self.input_style())
        self.inp_username.returnPressed.connect(lambda: self.inp_password.setFocus())
        fl.addWidget(self.inp_username)
        fl.addSpacing(14)

        # Password
        lbl_pass = QLabel("Mật khẩu")
        lbl_pass.setStyleSheet("font-size: 12px; font-weight: bold; color: #475569;")
        fl.addWidget(lbl_pass)
        fl.addSpacing(6)

        self.inp_password = QLineEdit()
        self.inp_password.setPlaceholderText("Nhập mật khẩu...")
        self.inp_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_password.setFixedHeight(46)
        self.inp_password.setStyleSheet(self.input_style())
        self.inp_password.returnPressed.connect(self._on_login)
        fl.addWidget(self.inp_password)
        fl.addSpacing(10)

        # Hiện mật khẩu
        chk_show = QCheckBox("Hiện mật khẩu")
        chk_show.setStyleSheet("""
            QCheckBox { font-size: 12px; color: #64748B; }
            QCheckBox::indicator { width: 14px; height: 14px; }
        """)
        chk_show.toggled.connect(
            lambda checked: self.inp_password.setEchoMode(
                QLineEdit.EchoMode.Normal if checked
                else QLineEdit.EchoMode.Password
            )
        )
        fl.addWidget(chk_show)
        fl.addSpacing(14)

        self.error_container = QWidget()
        self.error_container.setFixedHeight(0)  # ẩn = height 0
        self.error_container.setStyleSheet("background: transparent;")
        ec_layout = QVBoxLayout(self.error_container)
        ec_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setStyleSheet("""
            background: #FEF2F2; color: #DC2626;
            border-radius: 10px; padding: 8px;
            font-size: 12px; font-weight: bold;
        """)
        ec_layout.addWidget(self.lbl_error)
        fl.addWidget(self.error_container)

        # Nút đăng nhập
        self.btn_login = QPushButton("Đăng nhập")
        self.btn_login.setFixedHeight(48)
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.btn_login.setStyleSheet("""
            QPushButton {
                background: #3B82F6; color: white;
                border: none; border-radius: 14px;
            }
            QPushButton:hover { background: #2563EB; }
            QPushButton:pressed { background: #1D4ED8; }
        """)
        self.btn_login.clicked.connect(self._on_login)
        fl.addWidget(self.btn_login)
        fl.addSpacing(10)

        # Quên mật khẩu
        self.btn_forgot = QPushButton("Quên mật khẩu?")
        self.btn_forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_forgot.setStyleSheet("""
            QPushButton {
                border: none; background: transparent;
                color: #3B82F6; font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { color: #2563EB; }
        """)
        self.btn_forgot.clicked.connect(self._forgot_password)
        fl.addWidget(self.btn_forgot)

        fl.addStretch()

        # Footer
        footer = QLabel("© 2026 Cafe POS System")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setFixedHeight(24)
        footer.setStyleSheet("color: #94A3B8; font-size: 11px;")
        fl.addWidget(footer)

        root.addWidget(body)
    # STYLE

    def label_style(self):

        return """
            font-size: 12px;
            font-weight: bold;
            color: #475569;
        """

    def input_style(self):

        return """
            QLineEdit {

                background: #F8FAFC;

                border: 1.5px solid #E2E8F0;

                border-radius: 14px;

                padding-left: 14px;
                padding-right: 14px;

                font-size: 14px;

                color: #0F172A;
            }

            QLineEdit:focus {

                background: white;

                border: 1.5px solid #3B82F6;
            }
        """

    # =========================================================
    # LOGIN
    # =========================================================

    def _on_login(self):
        self._clear_error()  # ← thêm dòng này
        username = self.inp_username.text().strip()
        password = self.inp_password.text().strip()

        if not username or not password:

            self.show_error(
                "Vui lòng nhập đầy đủ thông tin!"
            )

            return

        self.btn_login.setText(
            "Đang đăng nhập..."
        )

        self.btn_login.setEnabled(False)

        session = get_session()

        try:

            repo = UserRepository(session)

            user = repo.get_by_username(
                username
            )

            if not user or not user.verify_password(password):

                self.show_error(
                    "Tên đăng nhập hoặc mật khẩu không đúng!"
                )

                self.inp_password.clear()

                self.inp_password.setFocus()

                return

            if not user.is_active:

                self.show_error(
                    "Tài khoản đã bị khóa!"
                )

                return

            self.logged_user = user

            self.accept()

        except Exception as e:

            self.show_error(
                f"Lỗi hệ thống: {str(e)}"
            )

        finally:

            self.btn_login.setText(
                "Đăng nhập"
            )

            self.btn_login.setEnabled(True)

            session.close()
    # ERROR

    def show_error(self, text: str):
        self.lbl_error.setText(f"⚠  {text}")
        self.error_container.setFixedHeight(44)  # hiện ra = có chiều cao

    def _clear_error(self):
        self.lbl_error.setText("")
        self.error_container.setFixedHeight(0)  # ẩn = height 0

    # FORGOT PASSWORD

    def _forgot_password(self):

        username = self.inp_username.text().strip()

        if not username:
            self.show_error(
                "Vui lòng nhập tên đăng nhập trước!"
            )

            return

        session = get_session()

        try:

            repo = UserRepository(session)

            user = repo.get_by_username(username)

            if not user:
                self.show_error(
                    "Không tìm thấy tài khoản!"
                )

                return

            # RESET PASSWORD MẶC ĐỊNH
            import hashlib

            new_password = "123456"

            user.password_hash = hashlib.sha256(
                new_password.encode()
            ).hexdigest()

            session.commit()

            self.lbl_error.setStyleSheet("""
                background: #ECFDF5;
                color: #059669;

                border-radius: 10px;

                padding: 10px;

                font-size: 12px;
                font-weight: bold;
            """)

            self.lbl_error.setText(
                "✓ Mật khẩu đã reset về: 123456"
            )

            self.lbl_error.setVisible(True)

        except Exception as e:

            self.show_error(
                f"Lỗi: {str(e)}"
            )

        finally:

            session.close()