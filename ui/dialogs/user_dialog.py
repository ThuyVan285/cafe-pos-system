# FILE: ui/dialogs/user_dialog.py
import hashlib
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QComboBox,
    QWidget, QHBoxLayout, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from models.user import User, Role


class UserDialog(QDialog):

    def __init__(self, session, user=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.user = user
        self.setWindowTitle("Thêm người dùng" if not user else "Sửa người dùng")
        self.setFixedWidth(380)
        self.setModal(True)
        self.setStyleSheet("background: #F5F8FF;")
        self._build()
        if user:
            self._fill(user)

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(52)
        header.setStyleSheet("background: #1565C0;")
        h = QHBoxLayout(header)
        h.setContentsMargins(16, 0, 16, 0)
        title = QLabel("👤  " + ("Thêm" if not self.user else "Sửa") + " người dùng")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        h.addWidget(title)
        layout.addWidget(header)

        # Form
        form_widget = QWidget()
        form_widget.setStyleSheet("background: white;")
        form = QFormLayout(form_widget)
        form.setContentsMargins(20, 16, 20, 16)
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        style = """
            QLineEdit {
                background: #F5F8FF; border: 1.5px solid #DDEAF8;
                border-radius: 8px; padding: 0 12px;
                height: 36px; font-size: 13px;
            }
            QLineEdit:focus { border: 1.5px solid #1565C0; }
        """

        self.inp_fullname = QLineEdit()
        self.inp_fullname.setStyleSheet(style)
        self.inp_username = QLineEdit()
        self.inp_username.setStyleSheet(style)
        self.inp_password = QLineEdit()
        self.inp_password.setStyleSheet(style)
        self.inp_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_password.setPlaceholderText(
            "Để trống nếu không đổi" if self.user else "Nhập mật khẩu..."
        )

        self.cmb_role = QComboBox()
        self.cmb_role.addItems(["STAFF", "MANAGER", "ADMIN"])
        self.cmb_role.setFixedHeight(36)
        self.cmb_role.setStyleSheet("""
            QComboBox {
                background: #F5F8FF; border: 1.5px solid #DDEAF8;
                border-radius: 8px; padding: 0 12px; font-size: 13px;
            }
        """)

        form.addRow("Họ tên:", self.inp_fullname)
        form.addRow("Username:", self.inp_username)
        form.addRow("Mật khẩu:", self.inp_password)
        form.addRow("Vai trò:", self.cmb_role)

        layout.addWidget(form_widget, 1)

        # Footer
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
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("💾  Lưu")
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

    def _fill(self, user):
        self.inp_fullname.setText(user.full_name)
        self.inp_username.setText(user.username)
        idx = self.cmb_role.findText(user.role.value)
        if idx >= 0:
            self.cmb_role.setCurrentIndex(idx)

    def _on_save(self):
        fullname = self.inp_fullname.text().strip()
        username = self.inp_username.text().strip()
        password = self.inp_password.text().strip()
        role_str = self.cmb_role.currentText()

        if not fullname or not username:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        try:
            if self.user:
                self.user.full_name = fullname
                self.user.username = username
                self.user.role = Role(role_str)
                if password:
                    self.user.password_hash = hashlib.sha256(
                        password.encode()
                    ).hexdigest()
            else:
                if not password:
                    QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu!")
                    return
                user = User(
                    username=username,
                    password_hash=hashlib.sha256(password.encode()).hexdigest(),
                    full_name=fullname,
                    role=Role(role_str),
                    is_active=True,
                )
                self.session.add(user)

            self.session.commit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))