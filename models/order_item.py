# FILE: models/order_item.py
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)  # snapshot
    size: Mapped[str] = mapped_column(String(5), default="")  # S, M, L or empty
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False)  # base + size delta
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    note: Mapped[str] = mapped_column(String(255), default="")

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    toppings = relationship("OrderItemTopping", back_populates="order_item", cascade="all, delete-orphan")

    @property
    def topping_total(self) -> int:
        return sum(t.topping_price for t in self.toppings)

    @property
    def line_total(self) -> int:
        return (self.unit_price + self.topping_total) * self.quantity

    def __repr__(self) -> str:
        return f"<OrderItem {self.product_name} x{self.quantity}>"


class OrderItemTopping(Base):
    __tablename__ = "order_item_toppings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_item_id: Mapped[int] = mapped_column(ForeignKey("order_items.id"), nullable=False)
    topping_id: Mapped[int] = mapped_column(ForeignKey("toppings.id"), nullable=False)
    topping_name: Mapped[str] = mapped_column(String(80), nullable=False)  # snapshot
    topping_price: Mapped[int] = mapped_column(Integer, default=0)

    order_item = relationship("OrderItem", back_populates="toppings")