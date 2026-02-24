from django.contrib import admin
from .models import StockMovement


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "movement_type",
        "quantity",
        "reason",
        "performed_by",
        "created_at",
    )
    list_filter = ("movement_type", "created_at")
    search_fields = ("product__name", "product__sku", "reason")
    raw_id_fields = ("product", "performed_by")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
