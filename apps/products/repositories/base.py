from abc import ABC, abstractmethod
from typing import Iterable

from apps.products.models import Product


class AbstractProductRepository(ABC):
    @abstractmethod
    def get_all(self) -> Iterable[Product]:
        ...

    @abstractmethod
    def get_by_id(self, product_id: int) -> Product:
        ...

    @abstractmethod
    def get_by_sku(self, sku: str) -> Product:
        ...

    @abstractmethod
    def get_low_stock(self) -> Iterable[Product]:
        ...

    @abstractmethod
    def save(self, product: Product) -> Product:
        ...

    @abstractmethod
    def delete(self, product: Product) -> None:
        ...

