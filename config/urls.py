from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("products/", include("apps.products.urls", namespace="products")),
    path("inventory/", include("apps.inventory.urls", namespace="inventory")),
    path("reports/", include("apps.reports.urls", namespace="reports")),
    path("", include("apps.inventory.dashboard_urls", namespace="dashboard")),
    path("", RedirectView.as_view(pattern_name="dashboard:index", permanent=False)),
]

