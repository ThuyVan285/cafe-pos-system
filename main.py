# FILE: main.py
import sys
from PyQt6.QtWidgets import QApplication
from database.init_db import init_database
from ui.main_window import MainWindow
from ui.dialogs.login_dialog import LoginDialog

_current_window = None


def restart_to_login(widget):
    global _current_window

    old_window = widget.window()

    login = LoginDialog()
    if login.exec() == LoginDialog.DialogCode.Accepted:
        user = login.logged_user
        _current_window = MainWindow(user)
        _current_window.show()

    old_window.close()


def main():
    global _current_window

    init_database()
    app = QApplication(sys.argv)

    login = LoginDialog()
    if login.exec() != LoginDialog.DialogCode.Accepted:
        sys.exit(0)

    user = login.logged_user
    _current_window = MainWindow(user)
    _current_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()