from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "rol",
        "is_active",
        "is_staff",
    )
    list_filter = (
        "rol",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "VíaRescate VE",
            {
                "fields": (
                    "rol",
                    "telefono",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "VíaRescate VE",
            {
                "fields": (
                    "email",
                    "rol",
                    "telefono",
                )
            },
        ),
    )
