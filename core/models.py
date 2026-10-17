from django.db import models


class Estado(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100, unique=True)

    # Coordenadas del centroide / capital del estado
    # Usadas para inicializar el pin del mapa cuando el usuario selecciona
    # este estado. Si son null, el mapa cae al default nacional.
    centroide_lat = models.FloatField(
        null=True, blank=True,
        help_text="Latitud del centroide o capital del estado.",
    )
    centroide_lng = models.FloatField(
        null=True, blank=True,
        help_text="Longitud del centroide o capital del estado.",
    )

    class Meta:
        ordering = ("nombre",)
        verbose_name = "Estado"
        verbose_name_plural = "Estados"

    def __str__(self):
        return self.nombre


class Municipio(models.Model):
    estado = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        related_name="municipios",
    )
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=120)

    centroide_lat = models.FloatField(null=True, blank=True)
    centroide_lng = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ("estado__nombre", "nombre")
        constraints = [
            models.UniqueConstraint(
                fields=("estado", "nombre"),
                name="uq_municipio_estado_nombre",
            ),
        ]
        verbose_name = "Municipio"
        verbose_name_plural = "Municipios"

    def __str__(self):
        return f"{self.nombre}, {self.estado.nombre}"


class Parroquia(models.Model):
    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.PROTECT,
        related_name="parroquias",
    )
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=120)

    centroide_lat = models.FloatField(null=True, blank=True)
    centroide_lng = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ("municipio__estado__nombre", "municipio__nombre", "nombre")
        constraints = [
            models.UniqueConstraint(
                fields=("municipio", "nombre"),
                name="uq_parroquia_municipio_nombre",
            ),
        ]
        verbose_name = "Parroquia"
        verbose_name_plural = "Parroquias"

    def __str__(self):
        return f"{self.nombre}, {self.municipio.nombre}"
