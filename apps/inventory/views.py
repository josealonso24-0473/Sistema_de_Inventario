from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import ListView, TemplateView

from apps.inventory.forms import StockMovementForm
from apps.inventory.models import StockMovement
from apps.inventory.observers.base import StockSubject
from apps.inventory.observers.stock_alert_observer import LowStockAlertObserver
from apps.inventory.services.inventory_service import InventoryService, InsufficientStockError
from apps.products.repositories.product_repository import DjangoProductRepository
from apps.products.services.product_service import ProductService


@method_decorator(login_required, name="dispatch")
class MovementListView(ListView):
    model = StockMovement
    template_name = "inventory/movement_list.html"
    context_object_name = "movements"


@login_required
def movement_create_view(request):
    form = StockMovementForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        repo = DjangoProductRepository()
        subject = StockSubject()
        subject.attach(LowStockAlertObserver())
        service = InventoryService(repo, subject)

        try:
            service.register_movement(
                product_id=form.cleaned_data["product"].id,
                movement_type=form.cleaned_data["movement_type"],
                quantity=form.cleaned_data["quantity"],
                reason=form.cleaned_data.get("reason") or "",
                user=request.user,
            )
        except InsufficientStockError as exc:
            form.add_error(None, str(exc))
        else:
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
        repo = DjangoProductRepository()
        product_service = ProductService(repo)
        low_stock_products = product_service.get_low_stock_products()
        recent_movements = StockMovement.objects.select_related("product").all()[:10]

        context.update(
            {
                "low_stock_products": low_stock_products,
                "recent_movements": recent_movements,
            }
        )
        return context

