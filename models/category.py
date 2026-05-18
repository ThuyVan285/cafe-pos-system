# FILE: models/category.py
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="")
    icon: Mapped[str] = mapped_column(String(10), default="")

    products = relationship("Product", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category {self.name}>"