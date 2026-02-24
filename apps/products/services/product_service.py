from typing import Iterable, Optional

from apps.products.models import Product
from apps.products.repositories.base import AbstractProductRepository


class ProductService:
    def __init__(self, repository: AbstractProductRepository) -> None:
        self._repository = repository

    def list_products(
        self,
        *,
        category_id: Optional[int] = None,
        low_stock_only: bool = False,
    ) -> Iterable[Product]:
        qs = self._repository.get_all()
        if category_id:
            qs = qs.filter(category_id=category_id)
        if low_stock_only:
            from django.db.models import F

            qs = qs.filter(stock_quantity__lte=F("minimum_stock"))
        return qs

    def create_product(self, **data) -> Product:
        product = Product(**data)
        return self._repository.save(product)

    def update_product(self, product: Product, **data) -> Product:
        for field, value in data.items():
            setattr(product, field, value)
        return self._repository.save(product)

    def deactivate_product(self, product: Product) -> Product:
        product.is_active = False
        return self._repository.save(product)

    def get_low_stock_products(self) -> Iterable[Product]:
        return self._repository.get_low_stock()

