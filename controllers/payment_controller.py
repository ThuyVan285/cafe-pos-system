from services.payment_service import PaymentService
from models.payment import PaymentMethod


class PaymentController:

    def __init__(self, payment_service: PaymentService):
        self._service = payment_service

    def pay(
        self,
        order_id: int,
        method: str,
        discount=False
    ):

        payment_method = PaymentMethod(method)

        return self._service.process_payment(
            order_id,
            payment_method,
            discount
        )