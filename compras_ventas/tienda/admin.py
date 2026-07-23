from django.contrib import admin

from .models import Compra, Producto, Venta


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio_venta", "stock", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre", "descripcion")

    @admin.display(description="Stock")
    def stock(self, obj):
        return obj.stock


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ("producto", "cantidad", "precio_unitario", "total", "proveedor", "fecha")
    list_filter = ("fecha", "proveedor")
    search_fields = ("producto__nombre", "proveedor")
    autocomplete_fields = ("producto",)

    @admin.display(description="Total")
    def total(self, obj):
        return obj.total


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("producto", "cantidad", "precio_unitario", "total", "cliente", "fecha")
    list_filter = ("fecha", "cliente")
    search_fields = ("producto__nombre", "cliente")
    autocomplete_fields = ("producto",)

    @admin.display(description="Total")
    def total(self, obj):
        return obj.total
