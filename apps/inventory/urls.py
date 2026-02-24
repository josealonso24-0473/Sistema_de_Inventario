from django.urls import path

from .views import MovementListView, movement_create_view

app_name = "inventory"

urlpatterns = [
    path("movements/", MovementListView.as_view(), name="movements"),
    path("movements/new/", movement_create_view, name="movement_create"),
]

