from django.urls import path

from .views import low_stock_report_view, movement_report_view

app_name = "reports"

urlpatterns = [
    path("movements/", movement_report_view, name="movement_report"),
    path("low-stock/", low_stock_report_view, name="low_stock_report"),
]

