from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import ListView, TemplateView

from apps.inventory.forms import get_stock_movement_form
from apps.inventory.models import StockMovement
from apps.inventory.observers.base import StockSubject
from apps.inventory.observers.stock_alert_observer import LowStockAlertObserver
from apps.inventory.services.inventory_service import InventoryService, InsufficientStockError
from apps.products.services.product_service import ProductService
from config.data_source import get_product_repository
from config.mock_data import get_mock_movements


@method_decorator(login_required, name="dispatch")
class MovementListView(ListView):
    model = StockMovement
    template_name = "inventory/movement_list.html"
    context_object_name = "movements"
    paginate_by = 20

    def get_queryset(self):
        if getattr(settings, "USE_MOCK_DATA", False):
            return get_mock_movements()
        return StockMovement.objects.select_related("product", "performed_by").all()


@login_required
def movement_create_view(request):
    form = get_stock_movement_form(request.POST or None)

    if request.method == "POST" and form.is_valid():
        if getattr(settings, "USE_MOCK_DATA", False):
            messages.success(request, "Modo visualización: el movimiento no se guarda.")
            return redirect("inventory:movements")
        repo = get_product_repository()
        subject = StockSubject()
        subject.attach(LowStockAlertObserver())
        service = InventoryService(repo, subject)
        product_id = form.cleaned_data["product"]
        if hasattr(product_id, "id"):
            product_id = product_id.id
        try:
            service.register_movement(
                product_id=product_id,
                movement_type=form.cleaned_data["movement_type"],
                quantity=form.cleaned_data["quantity"],
                reason=form.cleaned_data.get("reason") or "",
                user=request.user,
            )
        except InsufficientStockError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, "Movimiento registrado correctamente.")
            return redirect("inventory:movements")

    return render(
        request,
        "inventory/movement_form.html",
        {"form": form},
    )


@method_decorator(login_required, name="dispatch")
class DashboardView(TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        repo = get_product_repository()
        product_service = ProductService(repo)
        low_stock_products = product_service.get_low_stock_products()
        if getattr(settings, "USE_MOCK_DATA", False):
            recent_movements = get_mock_movements()[:10]
        else:
            recent_movements = StockMovement.objects.select_related("product").all()[:10]
        context.update(
            {
                "low_stock_products": low_stock_products,
                "recent_movements": recent_movements,
            }
        )
        return context

