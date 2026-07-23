from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum


class Producto(models.Model):
    nombre = models.CharField("Nombre", max_length=120, unique=True)
    descripcion = models.CharField("Descripción", max_length=255, blank=True)
    precio_venta = models.DecimalField(
        "Precio de venta", max_digits=10, decimal_places=2, default=0
    )
    activo = models.BooleanField("Activo", default=True)
    creado = models.DateTimeField("Creado", auto_now_add=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    @property
    def total_comprado(self):
        return self.compras.aggregate(t=Sum("cantidad"))["t"] or 0

    @property
    def total_vendido(self):
        return self.ventas.aggregate(t=Sum("cantidad"))["t"] or 0

    @property
    def stock(self):
        """Stock disponible = todo lo comprado menos todo lo vendido."""
        return self.total_comprado - self.total_vendido


class Compra(models.Model):
    """Entrada de mercancía: aumenta el stock."""

    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="compras"
    )
    cantidad = models.PositiveIntegerField("Cantidad")
    precio_unitario = models.DecimalField(
        "Precio unitario", max_digits=10, decimal_places=2
    )
    proveedor = models.CharField("Proveedor", max_length=120, blank=True)
    fecha = models.DateTimeField("Fecha", auto_now_add=True)

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Compra {self.cantidad} × {self.producto}"

    @property
    def total(self):
        return self.cantidad * self.precio_unitario


class Venta(models.Model):
    """Salida de mercancía: descuenta el stock."""

    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="ventas"
    )
    cantidad = models.PositiveIntegerField("Cantidad")
    precio_unitario = models.DecimalField(
        "Precio unitario", max_digits=10, decimal_places=2
    )
    cliente = models.CharField("Cliente", max_length=120, blank=True)
    fecha = models.DateTimeField("Fecha", auto_now_add=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Venta {self.cantidad} × {self.producto}"

    @property
    def total(self):
        return self.cantidad * self.precio_unitario

    def clean(self):
        """Impide vender más de lo que hay en stock."""
        if self.producto_id and self.cantidad:
            disponible = self.producto.stock
            # Si es una edición, no cuentes la cantidad previa de esta venta.
            if self.pk:
                anterior = Venta.objects.get(pk=self.pk)
                disponible += anterior.cantidad
            if self.cantidad > disponible:
                raise ValidationError(
                    {
                        "cantidad": (
                            f"Stock insuficiente. Disponible: {disponible}, "
                            f"solicitado: {self.cantidad}."
                        )
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
