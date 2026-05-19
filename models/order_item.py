# FILE: models/order_item.py
from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.db import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False
    )

    product_name: Mapped[str] = mapped_column(
        String(100)
    )

    size: Mapped[str] = mapped_column(
        String(10),
        default=""
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    unit_price: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    note: Mapped[str] = mapped_column(
        String(255),
        default=""
    )

    order = relationship(
        "Order",
        back_populates="items"
    )

    toppings = relationship(
        "OrderItemTopping",
        back_populates="order_item",
        cascade="all, delete-orphan"
    )

    @property
    def topping_total(self) -> int:
        return sum(t.topping_price for t in self.toppings)

    @property
    def single_price(self) -> int:
        return self.unit_price + self.topping_total

    @property
    def total_price(self) -> int:
        return self.single_price * self.quantity

    def __repr__(self):
        return f"<OrderItem {self.product_name}>"



class OrderItemTopping(Base):
    __tablename__ = "order_item_toppings"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    order_item_id: Mapped[int] = mapped_column(
        ForeignKey("order_items.id"),
        nullable=False
    )

    topping_id: Mapped[int] = mapped_column(
        ForeignKey("toppings.id"),
        nullable=False
    )

    topping_name: Mapped[str] = mapped_column(
        String(100)
    )

    topping_price: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    order_item = relationship(
        "OrderItem",
        back_populates="toppings"
    )