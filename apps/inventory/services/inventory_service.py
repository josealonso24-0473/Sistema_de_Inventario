from django.db import transaction

from apps.products.repositories.base import AbstractProductRepository
from apps.inventory.models import StockMovement
from apps.inventory.observers.base import StockSubject


class InsufficientStockError(Exception):
    """Se lanza cuando se intenta registrar una salida mayor al stock disponible."""


class InventoryService:
    def __init__(self, product_repository: AbstractProductRepository, subject: StockSubject):
        self._product_repo = product_repository
        self._subject = subject

    @transaction.atomic
    def register_movement(
        self,
        *,
        product_id: int,
        movement_type: str,
        quantity: int,
        reason: str,
        user,
    ) -> StockMovement:
        product = self._product_repo.get_by_id(product_id)

        if movement_type == StockMovement.EXIT and quantity > product.stock_quantity:
            raise InsufficientStockError("La salida excede el stock disponible.")

        if movement_type == StockMovement.ENTRY:
            product.stock_quantity += quantity
        elif movement_type == StockMovement.EXIT:
            product.stock_quantity -= quantity
        elif movement_type == StockMovement.ADJUSTMENT:
            product.stock_quantity = quantity

        self._product_repo.save(product)

        movement = StockMovement.objects.create(
            product=product,
            movement_type=movement_type,
            quantity=quantity,
            reason=reason,
            performed_by=user,
        )

        self._subject.notify(product=product, movement=movement)

        return movement

