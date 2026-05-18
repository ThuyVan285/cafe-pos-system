from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.order import Order, OrderStatus


class StatisticService:

    def __init__(self, session: Session):
        self._session = session

    def get_today_revenue(self) -> int:

        today = datetime.now().date()

        orders = (
            self._session.query(Order)
            .filter(Order.status == OrderStatus.PAID)
            .all()
        )

        total = 0

        for order in orders:

            if order.created_at.date() == today:
                total += order.payment.total_amount

        return total

    def moving_average_prediction(self, days: int = 3) -> float:

        orders = (
            self._session.query(Order)
            .filter(Order.status == OrderStatus.PAID)
            .order_by(Order.created_at.desc())
            .all()
        )

        revenues = []

        grouped = {}

        for order in orders:

            date = order.created_at.date()

            if date not in grouped:
                grouped[date] = 0

            grouped[date] += order.payment.total_amount

        for value in grouped.values():
            revenues.append(value)

        revenues = revenues[:days]

        if not revenues:
            return 0

        return sum(revenues) / len(revenues)