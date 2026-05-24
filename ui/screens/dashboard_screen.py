# FILE: ui/screens/dashboard_screen.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class DashboardScreen(QWidget):

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setStyleSheet("background: #F0F4FA;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel(f"🏠  Dashboard\nXin chào, {user.full_name}!")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #1565C0;")
        layout.addWidget(lbl)

        lbl_role = QLabel(f"Role: {user.role.value}")
        lbl_role.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_role.setStyleSheet("color: #888; font-size: 14px;")
        layout.addWidget(lbl_role)