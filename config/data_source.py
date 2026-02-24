"""
Devuelve el repositorio de productos y los movimientos según USE_MOCK_DATA.
Usar en vistas para no acoplar a BD ni mock.
"""
from django.conf import settings

from apps.products.repositories.mock_repository import MockProductRepository
from apps.products.repositories.product_repository import DjangoProductRepository


def get_product_repository():
    if getattr(settings, "USE_MOCK_DATA", False):
        return MockProductRepository()
    return DjangoProductRepository()
