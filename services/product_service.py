# FILE: services/product_service.py
from sqlalchemy.orm import Session
from models.product import Product, ProductSize, Topping
from models.category import Category
from repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, session: Session) -> None:
        self._repo = ProductRepository(session)
        self._session = session

    def get_all_products(self) -> list[Product]:
        return self._repo.get_all_active()

    def get_products_by_category(self, category_id: int) -> list[Product]:
        return self._repo.get_by_category(category_id)

    def search_products(self, query: str) -> list[Product]:
        return self._repo.search(query)

    def get_categories(self) -> list[Category]:
        return self._repo.get_all_categories()

    def get_toppings(self) -> list[Topping]:
        return self._repo.get_all_toppings()

    def get_product_by_id(self, product_id: int) -> Product | None:
        return self._repo.get_by_id(product_id)

    def calculate_item_price(self, product: Product, size: str) -> int:
        if not product.has_size or not size:
            return product.base_price
        for ps in product.sizes:
            if ps.size == size:
                return product.base_price + ps.price_delta
        return product.base_price