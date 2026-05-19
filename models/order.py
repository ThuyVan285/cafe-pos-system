# FILE: models/order.py
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base


class OrderStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    table_id: Mapped[int] = mapped_column(
        ForeignKey("cafe_tables.id"), nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.ACTIVE
    )

    discount_amount: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    table = relationship("CafeTable", back_populates="orders")

    # ✅ QUAN TRỌNG: dùng string "User", KHÔNG import class User trực tiếp
    user = relationship("User", back_populates="orders")

    payment = relationship(
        "Payment",
        back_populates="order",
        uselist=False,
    )

    # ── Properties ───────────────────────────────────────────────────────
    @property
    def subtotal(self) -> int:
        return sum(item.total_price for item in self.items)

    @property
    def total(self) -> int:
        return max(0, self.subtotal - self.discount_amount)

    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items)

    def __repr__(self):
        return f"<Order #{self.id} {self.status}>"