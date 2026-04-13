"""
Unit tests for the Observer pattern (StockSubject + LowStockAlertObserver).
No database required.
"""
from types import SimpleNamespace
from django.test import SimpleTestCase

from apps.inventory.observers.base import StockObserver, StockSubject
from apps.inventory.observers.stock_alert_observer import LowStockAlertObserver


class RecordingObserver(StockObserver):
    def __init__(self):
        self.calls = []

    def update(self, *, product, movement):
        self.calls.append((product, movement))


class TestStockSubject(SimpleTestCase):
    def setUp(self):
        self.subject = StockSubject()
        self.observer = RecordingObserver()

    def test_attach_and_notify(self):
        self.subject.attach(self.observer)
        product = SimpleNamespace(sku="X-001", stock_quantity=5, minimum_stock=5)
        movement = SimpleNamespace(movement_type="EXIT", quantity=1)
        self.subject.notify(product=product, movement=movement)
        self.assertEqual(len(self.observer.calls), 1)
        self.assertIs(self.observer.calls[0][0], product)

    def test_detach_stops_notifications(self):
        self.subject.attach(self.observer)
        self.subject.detach(self.observer)
        self.subject.notify(
            product=SimpleNamespace(sku="X", stock_quantity=1, minimum_stock=5),
            movement=SimpleNamespace(),
        )
        self.assertEqual(len(self.observer.calls), 0)

    def test_multiple_observers_all_notified(self):
        obs2 = RecordingObserver()
        self.subject.attach(self.observer)
        self.subject.attach(obs2)
        self.subject.notify(
            product=SimpleNamespace(sku="X", stock_quantity=1, minimum_stock=5),
            movement=SimpleNamespace(),
        )
        self.assertEqual(len(self.observer.calls), 1)
        self.assertEqual(len(obs2.calls), 1)


class TestLowStockAlertObserver(SimpleTestCase):
    def setUp(self):
        self.observer = LowStockAlertObserver()

    def test_logs_warning_when_stock_at_minimum(self):
        product = SimpleNamespace(sku="WARN-001", stock_quantity=5, minimum_stock=5)
        with self.assertLogs("apps.inventory.observers.stock_alert_observer", level="WARNING") as cm:
            self.observer.update(product=product, movement=SimpleNamespace())
        self.assertTrue(any("WARN-001" in line for line in cm.output))

    def test_logs_warning_when_stock_below_minimum(self):
        product = SimpleNamespace(sku="WARN-002", stock_quantity=2, minimum_stock=10)
        with self.assertLogs("apps.inventory.observers.stock_alert_observer", level="WARNING") as cm:
            self.observer.update(product=product, movement=SimpleNamespace())
        self.assertTrue(any("WARN-002" in line for line in cm.output))

    def test_no_warning_when_stock_above_minimum(self):
        product = SimpleNamespace(sku="OK-001", stock_quantity=20, minimum_stock=5)
        with self.assertNoLogs("apps.inventory.observers.stock_alert_observer", level="WARNING"):
            self.observer.update(product=product, movement=SimpleNamespace())
