from PyQt6.QtWidgets import QMainWindow
from ui.screens.pos_screen import PosScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cafe POS")
        self.resize(1400, 900)
        self.setCentralWidget(PosScreen())