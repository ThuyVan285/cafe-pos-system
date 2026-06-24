# FILE: repositories/product_repository.py

from typing import Optional

from sqlalchemy.orm import Session, joinedload

from models.product import (
    Product,
    ProductSize,
    Topping,
    ProductTopping
)

from models.category import Category


class ProductRepository:

    def __init__(self, session: Session) -> None:

        self._session = session

    # GET ALL PRODUCTS
    def get_all(self) -> list[Product]:

        return (
            self._session.query(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.sizes),
                joinedload(Product.product_toppings)
                .joinedload(ProductTopping.topping),
            )
            .order_by(Product.name)
            .all()
        )
    # GET ALL ACTIVE PRODUCTS
    def get_all_active(self) -> list[Product]:

        return (
            self._session.query(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.sizes),
                joinedload(Product.product_toppings)
                .joinedload(ProductTopping.topping),
            )
            .filter(Product.is_active == True)
            .order_by(Product.name)
            .all()
        )

    # GET PRODUCT BY ID
    def get_by_id(self, product_id: int) -> Optional[Product]:

        return (
            self._session.query(Product)
            .options(
                joinedload(Product.sizes),
                joinedload(Product.product_toppings)
                .joinedload(ProductTopping.topping),
            )
            .filter(Product.id == product_id)
            .first()
        )


    # GET PRODUCTS BY CATEGORY

    def get_by_category(
        self,
        category_id: int
    ) -> list[Product]:

        return (
            self._session.query(Product)
            .filter(
                Product.category_id == category_id,
                Product.is_active == True
            )
            .options(
                joinedload(Product.sizes)
            )
            .order_by(Product.name)
            .all()
        )

    # SEARCH PRODUCT

    def search(self, query: str) -> list[Product]:

        return (
            self._session.query(Product)
            .filter(
                Product.name.ilike(f"%{query}%"),
                Product.is_active == True
            )
            .options(
                joinedload(Product.sizes)
            )
            .order_by(Product.name)
            .all()
        )

    # GET ALL CATEGORIES
    def get_all_categories(self) -> list[Category]:

        return (
            self._session.query(Category)
            .order_by(Category.name)
            .all()
        )

    # GET ALL TOPPINGS

    def get_all_toppings(self) -> list[Topping]:

        return (
            self._session.query(Topping)
            .order_by(Topping.name)
            .all()
        )
    # CREATE PRODUCT
    def create(self, product: Product) -> Product:

        self._session.add(product)

        self._session.flush()

        return product

    # UPDATE PRODUCT
    def update(self, product: Product) -> Product:

        self._session.flush()

        return product

    # DELETE PRODUCT (SOFT DELETE)
    def delete(self, product_id: int) -> bool:

        product = self.get_by_id(product_id)

        if product:

            product.is_active = False

            self._session.flush()

            return True

        return False