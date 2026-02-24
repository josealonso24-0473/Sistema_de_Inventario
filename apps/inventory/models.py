from django.conf import settings
from django.db import models

from apps.products.models import Product


class StockMovement(models.Model):
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    ADJUSTMENT = "ADJUSTMENT"

    MOVEMENT_TYPE_CHOICES = [
        (ENTRY, "Entrada"),
        (EXIT, "Salida"),
        (ADJUSTMENT, "Ajuste"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_movements",
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPE_CHOICES,
    )
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.movement_type} - {self.product} ({self.quantity})"

