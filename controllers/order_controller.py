from services.order_service import OrderService, AddItemRequest


class OrderController:

    def __init__(self, order_service: OrderService):
        self._service = order_service

    def create_or_get_order(self, table_id: int, user_id: int):
        return self._service.get_or_create_order(table_id, user_id)

    def add_product(
        self,
        order,
        product_id,
        size="",
        quantity=1,
        toppings=None
    ):

        toppings = toppings or []

        request = AddItemRequest(
            product_id=product_id,
            size=size,
            quantity=quantity,
            toppings=toppings
        )

        return self._service.add_item(order, request)

    def remove_item(self, item_id: int):
        self._service.remove_item(item_id)