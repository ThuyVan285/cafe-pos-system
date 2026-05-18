# FILE: config/settings.py
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "cafe_pos"
    charset: str = "utf8mb4"

    @property
    def url(self) -> str:
        return (
            f"mysql+pymysql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}?charset={self.charset}"
        )


@dataclass
class AppConfig:
    name: str = "Cafe POS"
    version: str = "1.0.0"
    window_width: int = 1400
    window_height: int = 860
    currency_symbol: str = "₫"
    tax_rate: float = 0.0
    staff_discount_rate: float = 0.20


DB_CONFIG = DatabaseConfig()
APP_CONFIG = AppConfig()