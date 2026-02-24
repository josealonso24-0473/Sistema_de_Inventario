from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from django.conf import settings

from apps.products.forms import ProductForm, get_product_form
from apps.products.models import Product
from apps.products.services.product_service import ProductService
from config.data_source import get_product_repository
from config.mock_data import (
    create_mock_product,
    get_mock_product_by_id,
    update_mock_product,
)


@method_decorator(login_required, name="dispatch")
class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        repo = get_product_repository()
        service = ProductService(repo)
        category_id = self.request.GET.get("category")
        low_stock_only = self.request.GET.get("low_stock") == "1"
        return service.list_products(
            category_id=int(category_id) if category_id else None,
            low_stock_only=low_stock_only,
        )


@login_required
def product_create_view(request):
    form = get_product_form(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if getattr(settings, "USE_MOCK_DATA", False):
            create_mock_product(
                name=form.cleaned_data["name"],
                sku=form.cleaned_data["sku"],
                category_id=form.cleaned_data.get("category"),
                supplier_id=form.cleaned_data.get("supplier"),
                unit_price=form.cleaned_data["unit_price"],
                stock_quantity=form.cleaned_data["stock_quantity"],
                minimum_stock=form.cleaned_data["minimum_stock"],
                is_active=form.cleaned_data["is_active"],
            )
            messages.success(
                request,
                "Producto creado correctamente (modo mock, no se guarda en BD).",
            )
            return redirect("products:list")
        repo = get_product_repository()
        service = ProductService(repo)
        service.create_product(**form.cleaned_data)
        messages.success(request, "Producto creado correctamente.")
        return redirect("products:list")
    return render(request, "products/product_form.html", {"form": form, "title": "Nuevo producto"})


@login_required
def product_update_view(request, pk):
    if getattr(settings, "USE_MOCK_DATA", False):
        product = get_mock_product_by_id(pk)
        if product is None:
            messages.error(request, "Producto no encontrado en datos mock.")
            return redirect("products:list")
        form = get_product_form(request.POST or None, instance=product)
        if request.method == "POST" and form.is_valid():
            update_mock_product(
                pk,
                name=form.cleaned_data["name"],
                sku=form.cleaned_data["sku"],
                category_id=form.cleaned_data.get("category"),
                supplier_id=form.cleaned_data.get("supplier"),
                unit_price=form.cleaned_data["unit_price"],
                stock_quantity=form.cleaned_data["stock_quantity"],
                minimum_stock=form.cleaned_data["minimum_stock"],
                is_active=form.cleaned_data["is_active"],
            )
            messages.success(
                request,
                "Producto actualizado correctamente (modo mock, no se guarda en BD).",
            )
            return redirect("products:list")
        return render(
            request,
            "products/product_form.html",
            {"form": form, "title": "Editar producto", "product": product},
        )

    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == "POST" and form.is_valid():
        repo = get_product_repository()
        service = ProductService(repo)
        service.update_product(product, **form.cleaned_data)
        messages.success(request, "Producto actualizado correctamente.")
        return redirect("products:list")
    return render(request, "products/product_form.html", {"form": form, "title": "Editar producto", "product": product})

