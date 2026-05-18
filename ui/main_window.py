from PyQt6.QtWidgets import (
    QMainWindow,
    QTabWidget
)

from ui.screens.pos_screen import PosScreen
from ui.screens.report_screen import ReportScreen


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Cafe POS")

        self.resize(1400, 900)

        tabs = QTabWidget()

        tabs.addTab(PosScreen(), "POS")
        tabs.addTab(ReportScreen(), "Reports")

        self.setCentralWidget(tabs)