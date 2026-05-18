# FILE: repositories/order_item_repository.py
from typing import Optional
from sqlalchemy.orm import Session
from models.order_item import OrderItem, OrderItemTopping


class OrderItemRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, item: OrderItem) -> OrderItem:
        self._session.add(item)
        self._session.flush()
        return item

    def get_by_id(self, item_id: int) -> Optional[OrderItem]:
        return self._session.query(OrderItem).filter(OrderItem.id == item_id).first()

    def update_quantity(self, item_id: int, quantity: int) -> None:
        item = self.get_by_id(item_id)
        if item:
            item.quantity = quantity
            self._session.flush()

    def delete(self, item_id: int) -> bool:
        item = self.get_by_id(item_id)
        if item:
            self._session.delete(item)
            self._session.flush()
            return True
        return False

    def add_topping(self, topping: OrderItemTopping) -> OrderItemTopping:
        self._session.add(topping)
        self._session.flush()
        return topping