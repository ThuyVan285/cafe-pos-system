# FILE: models/product.py
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    base_price: Mapped[int] = mapped_column(Integer, nullable=False)  # VND
    has_size: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str] = mapped_column(String(255), default="")
    image_path: Mapped[str] = mapped_column(String(255), default="")

    category = relationship("Category", back_populates="products")
    sizes = relationship("ProductSize", back_populates="product", cascade="all, delete-orphan")
    product_toppings = relationship("ProductTopping", back_populates="product", cascade="all, delete-orphan")

    @property
    def available_toppings(self):
        return [pt.topping for pt in self.product_toppings]

    def __repr__(self) -> str:
        return f"<Product {self.name} @ {self.base_price}>"


class ProductSize(Base):
    __tablename__ = "product_sizes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    size: Mapped[str] = mapped_column(String(5), nullable=False)  # S, M, L
    price_delta: Mapped[int] = mapped_column(Integer, default=0)  # relative to base

    product = relationship("Product", back_populates="sizes")


class Topping(Base):
    __tablename__ = "toppings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    price: Mapped[int] = mapped_column(Integer, default=0)

    product_toppings = relationship("ProductTopping", back_populates="topping")

    def __repr__(self) -> str:
        return f"<Topping {self.name}>"


class ProductTopping(Base):
    __tablename__ = "product_toppings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    topping_id: Mapped[int] = mapped_column(ForeignKey("toppings.id"), nullable=False)

    product = relationship("Product", back_populates="product_toppings")
    topping = relationship("Topping", back_populates="product_toppings")