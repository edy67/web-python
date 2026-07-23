from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.shortcuts import render

from .models import Compra, Producto, Venta

_MONEY = DecimalField(max_digits=14, decimal_places=2)


def _importe(qs):
    """Suma cantidad * precio_unitario de un queryset de movimientos."""
    total = qs.aggregate(
        t=Sum(
            ExpressionWrapper(F("cantidad") * F("precio_unitario"), output_field=_MONEY)
        )
    )["t"]
    return total or 0


def dashboard(request):
    productos = list(Producto.objects.all())
    total_compras = _importe(Compra.objects.all())
    total_ventas = _importe(Venta.objects.all())

    contexto = {
        "productos": productos,
        "num_productos": len(productos),
        "total_compras": total_compras,
        "total_ventas": total_ventas,
        "ganancia": total_ventas - total_compras,
        "ultimas_compras": Compra.objects.select_related("producto")[:8],
        "ultimas_ventas": Venta.objects.select_related("producto")[:8],
        "bajo_stock": [p for p in productos if p.stock <= 5],
    }
    return render(request, "tienda/dashboard.html", contexto)
