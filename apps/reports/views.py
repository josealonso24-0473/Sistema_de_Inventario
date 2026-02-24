import csv
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponse
from django.shortcuts import render

from apps.inventory.models import StockMovement
from apps.products.models import Product


@login_required
def movement_report_view(request):
    movements = StockMovement.objects.select_related("product", "performed_by")

    # Filtros simples por fecha, tipo y producto
    movement_type = request.GET.get("movement_type")
    product_id = request.GET.get("product")

    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    if product_id:
        movements = movements.filter(product_id=product_id)

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

    products = Product.objects.filter(is_active=True)
    return render(
        request,
        "reports/movement_report.html",
        {
            "movements": movements,
            "products": products,
        },
    )


@login_required
def low_stock_report_view(request):
    products = Product.objects.filter(
        is_active=True, stock_quantity__lte=models.F("minimum_stock")
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

    return render(
        request,
        "reports/low_stock_report.html",
        {
            "products": products,
        },
    )

