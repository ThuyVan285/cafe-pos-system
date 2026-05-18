# FILE: services/order_service.py
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from models.order import Order, OrderStatus
from models.order_item import OrderItem, OrderItemTopping
from models.table import TableStatus
from models.product import Topping
from repositories.order_repository import OrderRepository
from repositories.order_item_repository import OrderItemRepository
from repositories.table_repository import TableRepository
from repositories.product_repository import ProductRepository
from utils.validator import validate_quantity, validate_table_merge


@dataclass
class AddItemRequest:
    product_id: int
    size: str = ""
    quantity: int = 1
    toppings: list[int] = field(default_factory=list)  # list of topping IDs
    note: str = ""


class OrderService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._order_repo = OrderRepository(session)
        self._item_repo = OrderItemRepository(session)
        self._table_repo = TableRepository(session)
        self._product_repo = ProductRepository(session)

    def get_or_create_order(self, table_id: int, user_id: int) -> Order:
        """Fetch active order for table, or create a new one."""
        order = self._order_repo.get_active_by_table(table_id)
        if not order:
            order = Order(table_id=table_id, user_id=user_id, status=OrderStatus.ACTIVE)
            self._order_repo.create(order)
            self._table_repo.update_status(table_id, TableStatus.USING)
            self._session.commit()
        return order

    def get_active_order(self, table_id: int) -> Order | None:
        return self._order_repo.get_active_by_table(table_id)

    def add_item(self, order: Order, request: AddItemRequest) -> OrderItem:
        val = validate_quantity(request.quantity)
        if not val:
            raise ValueError(val.message)

        product = self._product_repo.get_by_id(request.product_id)
        if not product:
            raise ValueError("Product not found.")

        # Calculate unit price from size
        unit_price = product.base_price
        if product.has_size and request.size:
            for ps in product.sizes:
                if ps.size == request.size:
                    unit_price = product.base_price + ps.price_delta
                    break

        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            size=request.size,
            unit_price=unit_price,
            quantity=request.quantity,
            note=request.note,
        )
        self._item_repo.create(item)

        # Add toppings
        for topping_id in request.toppings:
            topping = self._session.get(Topping, topping_id)
            if topping:
                self._item_repo.add_topping(OrderItemTopping(
                    order_item_id=item.id,
                    topping_id=topping.id,
                    topping_name=topping.name,
                    topping_price=topping.price,
                ))

        self._session.commit()
        # Refresh to get toppings loaded
        self._session.refresh(item)
        return item

    def update_item_quantity(self, item_id: int, quantity: int) -> None:
        val = validate_quantity(quantity)
        if not val:
            raise ValueError(val.message)
        self._item_repo.update_quantity(item_id, quantity)
        self._session.commit()

    def remove_item(self, item_id: int) -> None:
        self._item_repo.delete(item_id)
        self._session.commit()

    def move_table(self, order_id: int, target_table_id: int) -> Order:
        """Move an active order from its current table to a target empty table."""
        order = self._order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found.")
        target = self._table_repo.get_by_id(target_table_id)
        if not target or not target.is_available:
            raise ValueError("Target table is not available.")

        old_table_id = order.table_id
        order.table_id = target_table_id
        self._table_repo.update_status(old_table_id, TableStatus.EMPTY)
        self._table_repo.update_status(target_table_id, TableStatus.USING)
        self._session.commit()
        return order

    def merge_tables(self, main_order_id: int, secondary_table_id: int) -> Order:
        """Merge secondary table's order into main order."""
        main_order = self._order_repo.get_by_id(main_order_id)
        if not main_order:
            raise ValueError("Main order not found.")

        secondary_order = self._order_repo.get_active_by_table(secondary_table_id)
        if not secondary_order:
            raise ValueError("Secondary table has no active order.")

        val = validate_table_merge(main_order.table_id, secondary_table_id)
        if not val:
            raise ValueError(val.message)

        # Move all items from secondary to main
        for item in secondary_order.items:
            item.order_id = main_order.id

        # Close secondary order and free its table
        secondary_order.status = OrderStatus.CANCELLED
        self._table_repo.update_status(secondary_table_id, TableStatus.EMPTY)
        self._session.commit()

        # Reload main order
        return self._order_repo.get_by_id(main_order.id)