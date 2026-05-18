from sqlalchemy.orm import Session

from models.payment import Payment, PaymentMethod
from models.order import OrderStatus
from models.table import TableStatus

from repositories.order_repository import OrderRepository
from repositories.table_repository import TableRepository

from config.settings import APP_CONFIG


class PaymentService:

    def __init__(self, session: Session):

        self._session = session

        self._order_repo = OrderRepository(session)
        self._table_repo = TableRepository(session)

    def process_payment(
        self,
        order_id: int,
        method: PaymentMethod,
        apply_discount: bool = False
    ) -> Payment:

        order = self._order_repo.get_by_id(order_id)

        if not order:
            raise ValueError("Order not found")

        subtotal = order.subtotal

        discount_rate = 0.0
        discount_amount = 0

        if apply_discount:
            discount_rate = APP_CONFIG.staff_discount_rate
            discount_amount = int(subtotal * discount_rate)

        final_amount = subtotal - discount_amount

        payment = Payment(
            order_id=order.id,
            method=method,
            subtotal=subtotal,
            discount_rate=discount_rate,
            discount_amount=discount_amount,
            total_amount=final_amount,
            amount_received=final_amount,
            change_amount=0,
        )

        self._session.add(payment)

        order.status = OrderStatus.PAID

        self._table_repo.update_status(
            order.table_id,
            TableStatus.EMPTY
        )

        self._session.commit()

        return payment