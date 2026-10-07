import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Roles(models.TextChoices):
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
        COORDINADOR = "COORDINADOR", "Coordinador"
        OPERADOR = "OPERADOR", "Operador"
        VOLUNTARIO = "VOLUNTARIO", "Voluntario"
        USUARIO = "USUARIO", "Usuario"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    email = models.EmailField(
        unique=True,
        verbose_name="correo electrónico",
    )
    rol = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.USUARIO,
        db_index=True,
    )
    telefono = models.CharField(
        max_length=30,
        blank=True,
    )

    class Meta:
        ordering = ("username",)
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.get_full_name() or self.username
