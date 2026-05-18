from services.product_service import ProductService


class ProductController:

    def __init__(self, product_service: ProductService):
        self._service = product_service

    def get_products(self):
        return self._service.get_all_products()

    def search_products(self, keyword: str):
        return self._service.search_products(keyword)

    def get_categories(self):
        return self._service.get_categories()