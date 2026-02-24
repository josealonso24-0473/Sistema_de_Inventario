from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from apps.products.models import Product
from .models import StockMovement


def get_stock_movement_form(data=None):
    """Devuelve el formulario adecuado según USE_MOCK_DATA (mock no usa ORM)."""
    if getattr(settings, "USE_MOCK_DATA", False):
        return StockMovementFormMock(data)
    return StockMovementForm(data)


class StockMovementFormMock(forms.Form):
    """Formulario de movimiento con productos desde mock (solo visualización)."""

    product = forms.TypedChoiceField(
        choices=[],
        coerce=int,
        empty_value=None,
        label="Producto",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    movement_type = forms.ChoiceField(
        choices=StockMovement.MOVEMENT_TYPE_CHOICES,
        label="Tipo de movimiento",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    quantity = forms.IntegerField(
        min_value=1,
        label="Cantidad",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
    )
    reason = forms.CharField(
        required=False,
        max_length=255,
        label="Motivo (opcional)",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def __init__(self, data=None, **kwargs):
        super().__init__(data, **kwargs)
        from config.mock_data import get_mock_products

        products = get_mock_products(active_only=True)
        self.fields["product"].choices = [("", "Seleccione un producto")] + [
            (p.id, f"{p.sku} - {p.name}") for p in products
        ]

    def clean(self):
        cleaned_data = super().clean()
        from config.mock_data import get_mock_product_by_id

        product_id = cleaned_data.get("product")
        movement_type = cleaned_data.get("movement_type")
        quantity = cleaned_data.get("quantity")
        if product_id and movement_type == StockMovement.EXIT and quantity is not None:
            product = get_mock_product_by_id(product_id)
            if product and quantity > product.stock_quantity:
                raise ValidationError(
                    f"La salida excede el stock disponible. Stock actual: {product.stock_quantity}."
                )
        return cleaned_data


class StockMovementForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True).order_by("name"),
        label="Producto",
        empty_label="Seleccione un producto",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    movement_type = forms.ChoiceField(
        choices=StockMovement.MOVEMENT_TYPE_CHOICES,
        label="Tipo de movimiento",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    quantity = forms.IntegerField(
        min_value=1,
        label="Cantidad",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
    )
    reason = forms.CharField(
        required=False,
        max_length=255,
        label="Motivo (opcional)",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        movement_type = cleaned_data.get("movement_type")
        quantity = cleaned_data.get("quantity")

        if product and movement_type == StockMovement.EXIT and quantity is not None:
            if quantity > product.stock_quantity:
                raise ValidationError(
                    f"La salida excede el stock disponible. Stock actual: {product.stock_quantity}."
                )

        return cleaned_data
