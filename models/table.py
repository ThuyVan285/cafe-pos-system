# FILE: models/table.py
import enum
from sqlalchemy import String, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db import Base


class TableType(str, enum.Enum):
    TABLE = "TABLE"
    TAKE_AWAY = "TAKE_AWAY"
    DELIVERY = "DELIVERY"


class TableStatus(str, enum.Enum):
    EMPTY = "EMPTY"
    USING = "USING"


class CafeTable(Base):
    __tablename__ = "cafe_tables"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    table_type: Mapped[TableType] = mapped_column(SAEnum(TableType), default=TableType.TABLE)
    status: Mapped[TableStatus] = mapped_column(SAEnum(TableStatus), default=TableStatus.EMPTY)
    capacity: Mapped[int] = mapped_column(Integer, default=4)

    orders = relationship("Order", back_populates="table")

    @property
    def is_available(self) -> bool:
        return self.status == TableStatus.EMPTY

    def __repr__(self) -> str:
        return f"<CafeTable {self.code} ({self.status})>"