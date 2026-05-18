# FILE: models/payment.py
import enum
from datetime import datetime
from sqlalchemy import Integer, Float, String, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db import Base


class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    BANKING = "BANKING"
    CARD = "CARD"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), unique=True, nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(SAEnum(PaymentMethod), nullable=False)
    subtotal: Mapped[int] = mapped_column(Integer, nullable=False)
    discount_rate: Mapped[float] = mapped_column(Float, default=0.0)
    discount_amount: Mapped[int] = mapped_column(Integer, default=0)
    total_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_received: Mapped[int] = mapped_column(Integer, default=0)
    change_amount: Mapped[int] = mapped_column(Integer, default=0)
    note: Mapped[str] = mapped_column(String(255), default="")
    paid_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="payment")

    def __repr__(self) -> str:
        return f"<Payment #{self.id} {self.method} {self.total_amount}>"