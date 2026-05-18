# FILE: models/order.py
import enum
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime, Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db import Base


class OrderStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("cafe_tables.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.ACTIVE)
    note: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    table = relationship("CafeTable", back_populates="orders")
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False)

    @property
    def subtotal(self) -> int:
        return sum(item.line_total for item in self.items)

    def __repr__(self) -> str:
        return f"<Order #{self.id} [{self.status}]>"