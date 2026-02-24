import logging

from .base import StockObserver

logger = logging.getLogger(__name__)


class LowStockAlertObserver(StockObserver):
    def update(self, *, product, movement) -> None:
        if product.stock_quantity <= product.minimum_stock:
            logger.warning(
                "ALERTA DE STOCK BAJO | SKU=%s | stock=%s | mínimo=%s",
                product.sku,
                product.stock_quantity,
                product.minimum_stock,
            )

