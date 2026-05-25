# FILE: main.py
import sys
from PyQt6.QtWidgets import QApplication
from database.init_db import init_database
from ui.main_window import MainWindow
from ui.dialogs.login_dialog import LoginDialog


def main():
    init_database()
    app = QApplication(sys.argv)

    # ── HIỆN LOGIN ────────────────────────────────────────────
    login = LoginDialog()
    if login.exec() != LoginDialog.DialogCode.Accepted:
        sys.exit(0)  # Đóng app nếu cancel

    user = login.logged_user

    # ── VÀO APP THEO ROLE ─────────────────────────────────────
    window = MainWindow(user)
    window.show()

    sys.exit(app.exec())

    def restart_to_login(widget):
        from PyQt6.QtWidgets import QApplication
        window = widget.window()

        login = LoginDialog()
        if login.exec() == LoginDialog.DialogCode.Accepted:
            user = login.logged_user
            new_window = MainWindow(user)
            new_window.show()
            window.close()
        else:
            window.close()

if __name__ == "__main__":
    main()