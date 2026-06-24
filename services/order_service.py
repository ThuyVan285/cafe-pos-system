# FILE: services/order_service.py
from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from models.order import Order, OrderStatus
from models.order_item import OrderItem, OrderItemTopping
from models.table import TableStatus
from models.product import Product, Topping

from repositories.order_repository import OrderRepository
from repositories.order_item_repository import OrderItemRepository
from repositories.product_repository import ProductRepository
from repositories.table_repository import TableRepository



@dataclass
class AddItemRequest:
    product_id: int
    quantity: int = 1
    size: str = ""
    toppings: list[int] = field(default_factory=list)
    note: str = ""


class OrderService:

    def __init__(self, session: Session):
        self.session = session
        self.order_repo = OrderRepository(session)
        self.item_repo = OrderItemRepository(session)
        self.product_repo = ProductRepository(session)
        self.table_repo = TableRepository(session)

    def get_or_create_order(self, table_id: int, user_id: int) -> Order:
        order = self.order_repo.get_active_by_table(table_id)
        if order:
            return order

        order = Order(
            table_id=table_id,
            user_id=user_id,
            status=OrderStatus.ACTIVE,
        )
        self.order_repo.create(order)
        self.session.commit()
        return order

    def get_active_order(self, table_id: int):
        return self.order_repo.get_active_by_table(table_id)

    def add_item(self, order, product_id, size="", toppings=None):
        toppings = toppings or []

        product = self.session.get(Product, product_id)

        unit_price = product.base_price

        if size:
            size_obj = next((s for s in product.sizes if s.size == size), None)
            if size_obj:
                unit_price += size_obj.price_delta

        topping_total = sum(t.price for t in toppings)
        unit_price += topping_total

        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            size=size,
            quantity=1,
            unit_price=unit_price,
            note="",
        )
        self.session.add(item)
        self.session.flush()

        for topping in toppings:
            ot = OrderItemTopping(
                order_item_id=item.id,
                topping_id=topping.id,
                topping_name=topping.name,
                topping_price=topping.price,
            )
            self.session.add(ot)

        self.table_repo.update_status(order.table_id, TableStatus.USING)
        self.session.commit()
        return item

    def update_item_quantity(self, item_id: int, quantity: int):
        item = self.item_repo.get_by_id(item_id)
        if not item:
            raise ValueError("Item not found")
        item.quantity = quantity
        self.session.commit()

    def remove_item(self, item_id: int):
        item = self.item_repo.get_by_id(item_id)
        if not item:
            raise ValueError("Item not found")
        self.session.delete(item)
        self.session.commit()
        order = self.order_repo.get_by_id(item.order_id)
        if order and len(order.items) == 0:
            self.table_repo.update_status(order.table_id, TableStatus.EMPTY)

        self.session.commit()

    def move_table(self, order_id: int, target_table_id: int):
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        target_table = self.table_repo.get_by_id(target_table_id)
        if not target_table:
            raise ValueError("Target table not found")
        if target_table.status != TableStatus.EMPTY:
            raise ValueError("Target table is being used")

        old_table_id = order.table_id
        order.table_id = target_table_id
        self.table_repo.update_status(old_table_id, TableStatus.EMPTY)
        self.table_repo.update_status(target_table_id, TableStatus.USING)
        self.session.commit()

    def merge_tables(self, main_order_id: int, secondary_table_id: int) -> Order:
        main_order = self.order_repo.get_by_id(main_order_id)
        if not main_order:
            raise ValueError("Main order not found")

        second_order = self.order_repo.get_active_by_table(secondary_table_id)
        if not second_order:
            raise ValueError("Secondary table has no active order")
        if main_order.table_id == secondary_table_id:
            raise ValueError("Cannot merge same table")

        for item in second_order.items:
            item.order_id = main_order.id

        second_order.status = OrderStatus.CANCELLED
        self.table_repo.update_status(secondary_table_id, TableStatus.EMPTY)
        self.session.commit()
        self.session.refresh(main_order)
        return main_order

    def _calculate_price(self, product, size: str) -> int:
        price = product.base_price
        if product.has_size and size:
            selected = next(
                (s for s in product.sizes if s.size == size), None
            )
            if selected:
                price += selected.price_delta
        return price

    def _attach_toppings(self, item: OrderItem, topping_ids: list[int]):
        for topping_id in topping_ids:
            topping = self.session.get(Topping, topping_id)
            if not topping:
                continue
            self.session.add(OrderItemTopping(
                order_item_id=item.id,
                topping_id=topping.id,
                topping_name=topping.name,
                topping_price=topping.price,
            ))