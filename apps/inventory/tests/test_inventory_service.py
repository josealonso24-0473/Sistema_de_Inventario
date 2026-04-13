"""
Tests for InventoryService.
Uses the real database (Django TestCase) because register_movement
writes StockMovement records via the ORM.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.inventory.models import StockMovement
from apps.inventory.observers.base import StockSubject
from apps.inventory.observers.stock_alert_observer import LowStockAlertObserver
from apps.inventory.services.inventory_service import InsufficientStockError, InventoryService
from apps.products.models import Product
from apps.products.repositories.product_repository import DjangoProductRepository

User = get_user_model()


def make_service(observers=None):
    subject = StockSubject()
    for obs in (observers or []):
        subject.attach(obs)
    return InventoryService(
        product_repository=DjangoProductRepository(),
        subject=subject,
    )


class TestInventoryServiceEntry(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Teclado", sku="TEC-001", unit_price="25.00",
            stock_quantity=10, minimum_stock=5,
        )
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.service = make_service()

    def test_entry_increases_stock(self):
        self.service.register_movement(
            product_id=self.product.pk,
            movement_type=StockMovement.ENTRY,
            quantity=20,
            reason="Compra proveedor",
            user=self.user,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 30)

    def test_entry_creates_movement_record(self):
        self.service.register_movement(
            product_id=self.product.pk,
            movement_type=StockMovement.ENTRY,
            quantity=5,
            reason="Reposición",
            user=self.user,
        )
        movement = StockMovement.objects.get(product=self.product)
        self.assertEqual(movement.movement_type, StockMovement.ENTRY)
        self.assertEqual(movement.quantity, 5)
        self.assertEqual(movement.performed_by, self.user)


class TestInventoryServiceExit(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Mouse", sku="MOU-001", unit_price="15.00",
            stock_quantity=8, minimum_stock=3,
        )
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.service = make_service()

    def test_exit_decreases_stock(self):
        self.service.register_movement(
            product_id=self.product.pk,
            movement_type=StockMovement.EXIT,
            quantity=3,
            reason="Venta",
            user=self.user,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 5)

    def test_exit_raises_when_insufficient_stock(self):
        with self.assertRaises(InsufficientStockError):
            self.service.register_movement(
                product_id=self.product.pk,
                movement_type=StockMovement.EXIT,
                quantity=100,
                reason="Salida excesiva",
                user=self.user,
            )

    def test_insufficient_stock_does_not_modify_db(self):
        try:
            self.service.register_movement(
                product_id=self.product.pk,
                movement_type=StockMovement.EXIT,
                quantity=100,
                reason="Salida excesiva",
                user=self.user,
            )
        except InsufficientStockError:
            pass
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 8)
        self.assertFalse(StockMovement.objects.filter(product=self.product).exists())


class TestInventoryServiceAdjustment(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Monitor", sku="MON-001", unit_price="200.00",
            stock_quantity=15, minimum_stock=5,
        )
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.service = make_service()

    def test_adjustment_sets_absolute_quantity(self):
        self.service.register_movement(
            product_id=self.product.pk,
            movement_type=StockMovement.ADJUSTMENT,
            quantity=42,
            reason="Inventario físico",
            user=self.user,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 42)


class TestInventoryServiceObserverIntegration(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Cable USB", sku="CAB-001", unit_price="5.00",
            stock_quantity=6, minimum_stock=5,
        )
        self.user = User.objects.create_user(username="testuser", password="pass")

    def test_low_stock_observer_triggered_on_exit(self):
        service = make_service(observers=[LowStockAlertObserver()])
        logger_name = "apps.inventory.observers.stock_alert_observer"
        with self.assertLogs(logger_name, level="WARNING") as cm:
            service.register_movement(
                product_id=self.product.pk,
                movement_type=StockMovement.EXIT,
                quantity=2,
                reason="Venta",
                user=self.user,
            )
        self.assertTrue(any("CAB-001" in line for line in cm.output))

    def test_no_alert_when_stock_stays_above_minimum(self):
        service = make_service(observers=[LowStockAlertObserver()])
        logger_name = "apps.inventory.observers.stock_alert_observer"
        with self.assertNoLogs(logger_name, level="WARNING"):
            service.register_movement(
                product_id=self.product.pk,
                movement_type=StockMovement.ENTRY,
                quantity=50,
                reason="Compra",
                user=self.user,
            )
