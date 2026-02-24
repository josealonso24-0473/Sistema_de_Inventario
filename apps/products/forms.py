from django import forms

from .models import Product, Category, Supplier


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "category",
            "supplier",
            "unit_price",
            "stock_quantity",
            "minimum_stock",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "sku": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "supplier": forms.Select(attrs={"class": "form-select"}),
            "unit_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "stock_quantity": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "minimum_stock": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all().order_by("name")
        self.fields["category"].required = False
        self.fields["supplier"].queryset = Supplier.objects.all().order_by("name")
        self.fields["supplier"].required = False
