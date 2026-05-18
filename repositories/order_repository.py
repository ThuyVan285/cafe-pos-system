# FILE: repositories/order_repository.py
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from models.order import Order, OrderStatus
from models.order_item import OrderItem, OrderItemTopping


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_active_by_table(self, table_id: int) -> Optional[Order]:
        return (
            self._session.query(Order)
            .options(
                joinedload(Order.items).joinedload(OrderItem.toppings),
                joinedload(Order.items).joinedload(OrderItem.product),
            )
            .filter(Order.table_id == table_id, Order.status == OrderStatus.ACTIVE)
            .first()
        )

    def get_by_id(self, order_id: int) -> Optional[Order]:
        return (
            self._session.query(Order)
            .options(
                joinedload(Order.items).joinedload(OrderItem.toppings),
                joinedload(Order.table),
                joinedload(Order.user),
                joinedload(Order.payment),
            )
            .filter(Order.id == order_id)
            .first()
        )

    def create(self, order: Order) -> Order:
        self._session.add(order)
        self._session.flush()
        return order

    def update_status(self, order_id: int, status: OrderStatus) -> None:
        order = self._session.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = status
            order.updated_at = datetime.utcnow()
            self._session.flush()

    def get_paid_orders_by_date_range(self, start: datetime, end: datetime) -> list[Order]:
        return (
            self._session.query(Order)
            .options(joinedload(Order.payment), joinedload(Order.items))
            .filter(Order.status == OrderStatus.PAID, Order.created_at.between(start, end))
            .all()
        )

    def get_recent_paid_orders(self, limit: int = 30) -> list[Order]:
        return (
            self._session.query(Order)
            .options(joinedload(Order.payment))
            .filter(Order.status == OrderStatus.PAID)
            .order_by(Order.created_at.desc())
            .limit(limit)
            .all()
        )