from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from django.conf import settings

from apps.products.forms import ProductForm
from apps.products.models import Product
from apps.products.services.product_service import ProductService
from config.data_source import get_product_repository


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
    if getattr(settings, "USE_MOCK_DATA", False):
        messages.info(request, "Modo visualización: no se pueden crear productos.")
        return redirect("products:list")
    form = ProductForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        repo = get_product_repository()
        service = ProductService(repo)
        service.create_product(**form.cleaned_data)
        messages.success(request, "Producto creado correctamente.")
        return redirect("products:list")
    return render(request, "products/product_form.html", {"form": form, "title": "Nuevo producto"})


@login_required
def product_update_view(request, pk):
    if getattr(settings, "USE_MOCK_DATA", False):
        messages.info(request, "Modo visualización: no se pueden editar productos.")
        return redirect("products:list")
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == "POST" and form.is_valid():
        repo = get_product_repository()
        service = ProductService(repo)
        service.update_product(product, **form.cleaned_data)
        messages.success(request, "Producto actualizado correctamente.")
        return redirect("products:list")
    return render(request, "products/product_form.html", {"form": form, "title": "Editar producto", "product": product})

