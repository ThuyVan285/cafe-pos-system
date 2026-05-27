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

    def get_week_revenue(self) -> int:
        from datetime import datetime, timedelta
        start = datetime.now() - timedelta(days=7)
        orders = (
            self._session.query(Order)
            .filter(
                Order.status == OrderStatus.PAID,
                Order.created_at >= start
            )
            .all()
        )
        return sum(o.payment.total_amount for o in orders if o.payment)

    def get_month_revenue(self) -> int:
        from datetime import datetime
        now = datetime.now()
        start = datetime(now.year, now.month, 1)
        orders = (
            self._session.query(Order)
            .filter(
                Order.status == OrderStatus.PAID,
                Order.created_at >= start
            )
            .all()
        )
        return sum(o.payment.total_amount for o in orders if o.payment)

    def get_top_products(self, limit: int = 10) -> list:
        from models.order_item import OrderItem
        from sqlalchemy import func
        results = (
            self._session.query(
                OrderItem.product_name,
                func.sum(OrderItem.quantity).label("total_qty"),
                func.sum(
                    OrderItem.unit_price * OrderItem.quantity
                ).label("total_revenue")
            )
            .group_by(OrderItem.product_name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
            .all()
        )
        return [
            (r.product_name, r.total_qty, r.total_revenue)
            for r in results
        ]

    def get_revenue_by_hour(self):
        from models.order import Order, OrderStatus
        from models.payment import Payment
        from datetime import datetime
        from sqlalchemy import func

        today = datetime.now().date()
        results = (
            self._session.query(
                func.hour(Order.created_at).label('hour'),
                func.sum(Payment.total_amount).label('revenue')
            )
            .join(Payment, Payment.order_id == Order.id)
            .filter(
                Order.status == OrderStatus.PAID,
                func.date(Order.created_at) == today
            )
            .group_by(func.hour(Order.created_at))
            .order_by('hour')
            .all()
        )
        return [(int(r.hour), int(r.revenue or 0)) for r in results]

    def get_revenue_by_day(self, days: int = 7):
        from models.order import Order, OrderStatus
        from models.payment import Payment
        from datetime import datetime, timedelta
        from sqlalchemy import func

        result = []
        today = datetime.now().date()
        for i in range(days - 1, -1, -1):
            d = today - timedelta(days=i)
            rev = (
                    self._session.query(func.sum(Payment.total_amount))
                    .join(Order, Payment.order_id == Order.id)
                    .filter(
                        Order.status == OrderStatus.PAID,
                        func.date(Order.created_at) == d
                    )
                    .scalar() or 0
            )
            result.append((d.strftime('%d/%m'), int(rev)))
        return result

    def get_revenue_by_weekday(self):
        from models.order import Order, OrderStatus
        from models.payment import Payment
        from sqlalchemy import func

        day_names = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
        results = (
            self._session.query(
                func.dayofweek(Order.created_at).label('dow'),
                func.sum(Payment.total_amount).label('revenue')
            )
            .join(Payment, Payment.order_id == Order.id)
            .filter(Order.status == OrderStatus.PAID)
            .group_by(func.dayofweek(Order.created_at))
            .all()
        )

        dow_map = {2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 1: 6}
        values = [0] * 7
        for r in results:
            idx = dow_map.get(int(r.dow), -1)
            if idx >= 0:
                values[idx] = int(r.revenue or 0)
        return list(zip(day_names, values))

    def get_today_revenue(self) -> int:
        from models.order import Order, OrderStatus
        from models.payment import Payment
        from datetime import datetime
        from sqlalchemy import func

        today = datetime.now().date()
        result = (
                self._session.query(func.sum(Payment.total_amount))
                .join(Order, Payment.order_id == Order.id)
                .filter(
                    Order.status == OrderStatus.PAID,
                    func.date(Order.created_at) == today
                )
                .scalar() or 0
        )
        return int(result)

    def get_week_revenue(self) -> int:
        from models.order import Order, OrderStatus
        from models.payment import Payment
        from datetime import datetime, timedelta
        from sqlalchemy import func

        start = datetime.now() - timedelta(days=7)
        result = (
                self._session.query(func.sum(Payment.total_amount))
                .join(Order, Payment.order_id == Order.id)
                .filter(
                    Order.status == OrderStatus.PAID,
                    Order.created_at >= start
                )
                .scalar() or 0
        )
        return int(result)

    def get_month_revenue(self) -> int:
        from models.order import Order, OrderStatus
        from models.payment import Payment
        from datetime import datetime
        from sqlalchemy import func

        now = datetime.now()
        start = datetime(now.year, now.month, 1)
        result = (
                self._session.query(func.sum(Payment.total_amount))
                .join(Order, Payment.order_id == Order.id)
                .filter(
                    Order.status == OrderStatus.PAID,
                    Order.created_at >= start
                )
                .scalar() or 0
        )
        return int(result)

    def get_customers_by_hour(self):
        from models.order import Order, OrderStatus
        from sqlalchemy import func

        results = (
            self._session.query(
                func.hour(Order.created_at).label('hour'),
                func.count(Order.id).label('count')
            )
            .filter(Order.status == OrderStatus.PAID)
            .group_by(func.hour(Order.created_at))
            .order_by('hour')
            .all()
        )
        return [(int(r.hour), r.count) for r in results]

    def get_customers_by_day(self, days: int = 7) -> list:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        results = (
            self._session.query(
                func.date(Order.created_at).label('date'),
                func.count(Order.id).label('count')
            )
            .filter(
                Order.status == OrderStatus.PAID,
                Order.created_at >= datetime.now() - timedelta(days=days)
            )
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at))
            .all()
        )
        return [(str(r.date), int(r.count)) for r in results]

    def get_customers_by_weekday(self) -> list:
        from sqlalchemy import func
        results = (
            self._session.query(
                func.dayofweek(Order.created_at).label('dow'),
                func.count(Order.id).label('count')
            )
            .filter(Order.status == OrderStatus.PAID)
            .group_by(func.dayofweek(Order.created_at))
            .order_by(func.dayofweek(Order.created_at))
            .all()
        )
        days_map = {1: "CN", 2: "T2", 3: "T3", 4: "T4", 5: "T5", 6: "T6", 7: "T7"}
        return [(days_map.get(int(r.dow), str(r.dow)), int(r.count)) for r in results]

    def get_revenue_by_category(self) -> list:
        """Doanh thu theo từng danh mục — dùng cho pie chart"""
        from models.order_item import OrderItem
        from models.product import Product
        from models.category import Category
        from sqlalchemy import func
        results = (
            self._session.query(
                Category.name,
                func.sum(
                    OrderItem.unit_price * OrderItem.quantity
                ).label('revenue')
            )
            .join(Product, Product.id == OrderItem.product_id)
            .join(Category, Category.id == Product.category_id)
            .group_by(Category.name)
            .order_by(func.sum(
                OrderItem.unit_price * OrderItem.quantity
            ).desc())
            .all()
        )
        return [(r.name, int(r.revenue or 0)) for r in results]