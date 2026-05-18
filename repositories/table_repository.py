# FILE: repositories/table_repository.py
from typing import Optional
from sqlalchemy.orm import Session
from models.table import CafeTable, TableStatus, TableType


class TableRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_all(self) -> list[CafeTable]:
        return self._session.query(CafeTable).order_by(CafeTable.code).all()

    def get_by_id(self, table_id: int) -> Optional[CafeTable]:
        return self._session.query(CafeTable).filter(CafeTable.id == table_id).first()

    def get_by_code(self, code: str) -> Optional[CafeTable]:
        return self._session.query(CafeTable).filter(CafeTable.code == code).first()

    def get_empty_tables(self) -> list[CafeTable]:
        return (
            self._session.query(CafeTable)
            .filter(CafeTable.status == TableStatus.EMPTY)
            .order_by(CafeTable.code)
            .all()
        )

    def get_dine_in_tables(self) -> list[CafeTable]:
        return (
            self._session.query(CafeTable)
            .filter(CafeTable.table_type.in_([TableType.TABLE, TableType.TAKE_AWAY]))
            .order_by(CafeTable.code)
            .all()
        )

    def update_status(self, table_id: int, status: TableStatus) -> None:
        table = self.get_by_id(table_id)
        if table:
            table.status = status
            self._session.flush()