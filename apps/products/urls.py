from django.urls import path

from .views import ProductListView, product_create_view, product_update_view

app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view(), name="list"),
    path("new/", product_create_view, name="create"),
    path("<int:pk>/edit/", product_update_view, name="update"),
]

