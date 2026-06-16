# FILE: controllers/order_controller.py

from services.order_service import OrderService, AddItemRequest


class OrderController:

    def __init__(self, order_service: OrderService):
        self._service = order_service          # ← lưu là _service

    def create_or_get_order(self, table_id: int, user_id: int):
        return self._service.get_or_create_order(table_id, user_id)

    def add_product(self, order, product_id, size="", toppings=None):
        # ✅ Sửa: dùng self._service thay vì self.order_service
        return self._service.add_item(
            order, product_id,
            size=size,
            toppings=toppings or []
        )

    def remove_item(self, item_id: int):
        self._service.remove_item(item_id)