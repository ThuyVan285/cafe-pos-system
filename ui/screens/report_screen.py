from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

from database.db import get_session
from services.statistic_service import StatisticService


class ReportScreen(QWidget):

    def __init__(self):

        super().__init__()

        session = get_session()

        service = StatisticService(session)

        layout = QVBoxLayout()

        revenue = service.get_today_revenue()

        prediction = service.moving_average_prediction()

        layout.addWidget(
            QLabel(f"Today's Revenue: {revenue:,}₫")
        )

        layout.addWidget(
            QLabel(f"AI Prediction: {prediction:,.0f}₫")
        )

        self.setLayout(layout)