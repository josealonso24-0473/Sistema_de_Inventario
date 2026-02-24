from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from apps.products.models import Product
from apps.products.repositories.product_repository import DjangoProductRepository
from apps.products.services.product_service import ProductService


@method_decorator(login_required, name="dispatch")
class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        repo = DjangoProductRepository()
        service = ProductService(repo)
        category_id = self.request.GET.get("category")
        low_stock_only = self.request.GET.get("low_stock") == "1"
        return service.list_products(
            category_id=category_id if category_id else None,
            low_stock_only=low_stock_only,
        )


@login_required
def product_list_simple(request):
    # Vista alternativa mínima de listado
    products = Product.objects.filter(is_active=True)
    return render(request, "products/product_list.html", {"products": products})

