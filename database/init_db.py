# FILE: database/init_db.py
import hashlib

from database.db import Base, engine, get_session

# ✅ PHẢI import TẤT CẢ models trước khi gọi create_all
# để SQLAlchemy nhận diện đủ các mapper
import models.user        # noqa: F401
import models.table       # noqa: F401
import models.category    # noqa: F401
import models.product     # noqa: F401
import models.order       # noqa: F401
import models.order_item  # noqa: F401
import models.payment     # noqa: F401

from models.user import User, Role
from models.table import CafeTable, TableType, TableStatus
from models.category import Category
from models.product import Product, ProductSize, Topping, ProductTopping


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_database():
    Base.metadata.create_all(bind=engine)

    session = get_session()

    try:
        # ── USERS ─────────────────────────────────────────────
        if session.query(User).count() == 0:
            session.add_all([
                User(
                    username="admin",
                    password_hash=hash_password("admin123"),
                    full_name="Administrator",
                    role=Role.ADMIN,
                    is_active=True,
                ),
                User(
                    username="manager",
                    password_hash=hash_password("manager123"),
                    full_name="Manager",
                    role=Role.MANAGER,
                    is_active=True,
                ),
                User(
                    username="staff",
                    password_hash=hash_password("staff123"),
                    full_name="Staff",
                    role=Role.STAFF,
                    is_active=True,
                ),
            ])

        # ── TABLES ────────────────────────────────────────────
        if session.query(CafeTable).count() == 0:
            session.add(CafeTable(
                code="TB000",
                name="Take Away",
                table_type=TableType.TAKE_AWAY,
                status=TableStatus.EMPTY,
                capacity=0,
            ))
            for i in range(1, 41):
                session.add(CafeTable(
                    code=f"TB{i:03d}",
                    name=f"Table {i}",
                    table_type=TableType.TABLE,
                    status=TableStatus.EMPTY,
                    capacity=4,
                ))

        # ── CATEGORIES ────────────────────────────────────────
        if session.query(Category).count() == 0:
            coffee = Category(name="Coffee", description="Coffee drinks", icon="☕")
            tea    = Category(name="Tea",    description="Tea drinks",    icon="🍵")
            cake   = Category(name="Cake",   description="Cake & bakery", icon="🍰")
            session.add_all([coffee, tea, cake])
            session.flush()

            # ── PRODUCTS ──────────────────────────────────────
            products = [
                Product(name="Americano",    category_id=coffee.id, base_price=35000, has_size=True,  is_active=True),
                Product(name="Latte",        category_id=coffee.id, base_price=45000, has_size=True,  is_active=True),
                Product(name="Matcha Latte", category_id=tea.id,    base_price=50000, has_size=True,  is_active=True),
                Product(name="Cheese Cake",  category_id=cake.id,   base_price=55000, has_size=False, is_active=True),
            ]
            session.add_all(products)
            session.flush()

            # ── PRODUCT SIZES ─────────────────────────────────
            for product in products:
                if product.has_size:
                    session.add_all([
                        ProductSize(product_id=product.id, size="S", price_delta=-5000),
                        ProductSize(product_id=product.id, size="M", price_delta=0),
                        ProductSize(product_id=product.id, size="L", price_delta=5000),
                    ])

            # ── TOPPINGS ──────────────────────────────────────
            toppings = [
                Topping(name="Pearl",       price=5000),
                Topping(name="Cheese Foam", price=10000),
                Topping(name="Pudding",     price=7000),
            ]
            session.add_all(toppings)
            session.flush()

            # ── PRODUCT TOPPINGS ──────────────────────────────
            for product in products:
                for topping in toppings:
                    session.add(ProductTopping(
                        product_id=product.id,
                        topping_id=topping.id,
                    ))

        session.commit()
        print("=" * 40)
        print("DATABASE INITIALIZED SUCCESS")
        print("=" * 40)
        print("admin   / admin123")
        print("manager / manager123")
        print("staff   / staff123")

    except Exception as e:
        session.rollback()
        print("ERROR:", e)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    init_database()