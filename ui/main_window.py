# FILE: ui/main_window.py
from PyQt6.QtWidgets import QMainWindow
from models.user import Role


class MainWindow(QMainWindow):

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Cafe POS  —  {user.full_name} ({user.role.value})")
        self.resize(1400, 900)
        self._load_screen()

    def _load_screen(self):
        from models.user import Role

        if self.user.role == Role.STAFF:
            from ui.screens.pos_screen import PosScreen
            screen = PosScreen(self.user)
            self.setCentralWidget(screen)

        elif self.user.role in (Role.ADMIN, Role.MANAGER):
            from ui.screens.dashboard_screen import DashboardScreen
            screen = DashboardScreen(self.user)
            self.setCentralWidget(screen)