from django import forms
from django.core.exceptions import ValidationError

from apps.products.models import Product
from .models import StockMovement


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
