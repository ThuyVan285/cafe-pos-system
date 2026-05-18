from database.db import get_session
from services.order_service import OrderService, AddItemRequest


def test_create_order():

    session = get_session()

    service = OrderService(session)

    order = service.get_or_create_order(
        table_id=1,
        user_id=1
    )

    assert order is not None


def test_add_item():

    session = get_session()

    service = OrderService(session)

    order = service.get_or_create_order(
        table_id=1,
        user_id=1
    )

    item = service.add_item(
        order,
        AddItemRequest(
            product_id=1,
            quantity=1
        )
    )

    assert item is not None