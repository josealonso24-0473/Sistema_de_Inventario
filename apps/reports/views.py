import csv
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render

from apps.inventory.models import StockMovement
from apps.products.models import Product

PAGE_SIZE = 20


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _get_movements_queryset(request):
    if getattr(settings, "USE_MOCK_DATA", False):
        from config.mock_data import get_mock_movements

        movements = get_mock_movements()
        movement_type = request.GET.get("movement_type")
        product_id = request.GET.get("product")
        date_from = _parse_date(request.GET.get("date_from"))
        date_to = _parse_date(request.GET.get("date_to"))
        if movement_type:
            movements = [m for m in movements if m.movement_type == movement_type]
        if product_id:
            pid = int(product_id)
            movements = [m for m in movements if getattr(m.product, "id", m.product_id) == pid]
        if date_from:
            movements = [m for m in movements if m.created_at.date() >= date_from]
        if date_to:
            movements = [m for m in movements if m.created_at.date() <= date_to]
        return movements
    movements = StockMovement.objects.select_related("product", "performed_by")
    movement_type = request.GET.get("movement_type")
    product_id = request.GET.get("product")
    date_from = _parse_date(request.GET.get("date_from"))
    date_to = _parse_date(request.GET.get("date_to"))
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    if product_id:
        movements = movements.filter(product_id=product_id)
    if date_from:
        movements = movements.filter(created_at__date__gte=date_from)
    if date_to:
        movements = movements.filter(created_at__date__lte=date_to)
    return movements


@login_required
def movement_report_view(request):
    movements = _get_movements_queryset(request)

    if request.GET.get("export") == "csv":
        response = HttpResponse(content_type="text/csv")
        filename = f"movements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "ID",
                "Producto",
                "Tipo",
                "Cantidad",
                "Motivo",
                "Usuario",
                "Fecha",
            ]
        )
        for m in movements:
            writer.writerow(
                [
                    m.id,
                    m.product.sku,
                    m.movement_type,
                    m.quantity,
                    m.reason or "",
                    m.performed_by.username if m.performed_by else "",
                    m.created_at.isoformat(),
                ]
            )
        return response

    paginator = Paginator(movements, PAGE_SIZE)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    if getattr(settings, "USE_MOCK_DATA", False):
        from config.mock_data import get_mock_products

        products = get_mock_products(active_only=True)
    else:
        products = Product.objects.filter(is_active=True)
    return render(
        request,
        "reports/movement_report.html",
        {
            "movements": page_obj,
            "page_obj": page_obj,
            "products": products,
        },
    )


@login_required
def low_stock_report_view(request):
    if getattr(settings, "USE_MOCK_DATA", False):
        from config.mock_data import get_mock_low_stock_products

        products = get_mock_low_stock_products()
    else:
        products = Product.objects.filter(
            is_active=True, stock_quantity__lte=F("minimum_stock")
        )
    if request.GET.get("export") == "csv":
        response = HttpResponse(content_type="text/csv")
        filename = f"low_stock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "SKU",
                "Nombre",
                "Stock",
                "Stock mínimo",
            ]
        )
        for p in products:
            writer.writerow(
                [
                    p.sku,
                    p.name,
                    p.stock_quantity,
                    p.minimum_stock,
                ]
            )
        return response

    paginator = Paginator(products, PAGE_SIZE)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "reports/low_stock_report.html",
        {
            "products": page_obj,
            "page_obj": page_obj,
        },
    )

