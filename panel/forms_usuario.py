"""Formularios de gestión de usuarios con validación completa."""
from django import forms

from core import messages as msg
from core.validators import (
    normalizar_telefono_ve,
    validar_email,
    validar_nombre_persona,
    validar_password_fuerte,
    validar_username,
)
from usuarios.models import Usuario

from .user_hierarchy import roles_que_puede_asignar


class UsuarioCrearForm(forms.ModelForm):
    """Formulario de creación con contraseña inicial y validación completa."""

    password1 = forms.CharField(
        label="Contraseña inicial",
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            "data-validator": "password_fuerte",
            "minlength": "12",
            "maxlength": "128",
            "aria-describedby": "id_password1_help",
        }),
        help_text=(
            "Mínimo 12 caracteres, con mayúscula, minúscula, número "
            "y símbolo. No puede contener tu usuario ni correo."
        ),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            "data-validator": "password_confirmar",
            "minlength": "12",
            "maxlength": "128",
        }),
    )

    class Meta:
        model = Usuario
        fields = [
            "username", "email", "first_name", "last_name",
            "rol", "telefono", "is_active", "is_staff",
        ]
        widgets = {
            "username": forms.TextInput(attrs={
                "placeholder": "Ej: jperez",
                "minlength": "3",
                "maxlength": "150",
                "pattern": "[a-zA-Z0-9_.-]{3,150}",
                "data-validator": "username",
                "autocomplete": "username",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "usuario@ejemplo.com",
                "maxlength": "254",
                "data-validator": "email",
                "autocomplete": "email",
            }),
            "first_name": forms.TextInput(attrs={
                "placeholder": "Ej: Juan",
                "minlength": "2",
                "maxlength": "150",
                "data-validator": "nombre_persona",
                "autocomplete": "given-name",
            }),
            "last_name": forms.TextInput(attrs={
                "placeholder": "Ej: Pérez",
                "minlength": "2",
                "maxlength": "150",
                "data-validator": "nombre_persona",
                "autocomplete": "family-name",
            }),
            "telefono": forms.TextInput(attrs={
                "placeholder": "+584121234567",
                "data-validator": "telefono",
                "inputmode": "tel",
                "autocomplete": "tel",
                "pattern": "\\+58(4\\d{9}|2\\d{9})",
            }),
        }

    def __init__(self, *args, gestor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.gestor = gestor

        if gestor:
            roles_validos = [r[0] for r in roles_que_puede_asignar(gestor)]
            self.fields["rol"].choices = [
                (v, l) for v, l in Usuario.Roles.choices if v in roles_validos
            ]
            if not gestor.is_superuser:
                self.fields.pop("is_staff", None)

    def clean_username(self):
        valor = validar_username(self.cleaned_data["username"])
        if Usuario.objects.filter(username__iexact=valor).exists():
            raise forms.ValidationError(
                "Ya existe un usuario con ese nombre de usuario."
            )
        return valor

    def clean_email(self):
        valor = validar_email(self.cleaned_data["email"])
        if Usuario.objects.filter(email__iexact=valor).exists():
            raise forms.ValidationError(msg.EMAIL_DUPLICADO)
        return valor

    def clean_first_name(self):
        valor = self.cleaned_data.get("first_name", "").strip()
        if not valor:
            return ""
        return validar_nombre_persona(valor, contexto="nombre")

    def clean_last_name(self):
        valor = self.cleaned_data.get("last_name", "").strip()
        if not valor:
            return ""
        return validar_nombre_persona(valor, contexto="apellido")

    def clean_telefono(self):
        valor = self.cleaned_data.get("telefono", "").strip()
        if not valor:
            return ""
        return normalizar_telefono_ve(valor)

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        if not p1:
            return cleaned

        if p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
            return cleaned

        # Validar contraseña (incluye lista negra y coincidencia con user/email)
        try:
            validar_password_fuerte(
                p1,
                username=cleaned.get("username"),
                email=cleaned.get("email"),
            )
        except forms.ValidationError as e:
            self.add_error("password1", e)

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UsuarioEditarForm(forms.ModelForm):
    """Editar sin tocar contraseña. Todos los campos validados."""

    class Meta:
        model = Usuario
        fields = [
            "email", "first_name", "last_name",
            "rol", "telefono", "is_active", "is_staff",
        ]
        widgets = {
            "email": forms.EmailInput(attrs={
                "maxlength": "254",
                "data-validator": "email",
                "autocomplete": "email",
            }),
            "first_name": forms.TextInput(attrs={
                "minlength": "2",
                "maxlength": "150",
                "data-validator": "nombre_persona",
            }),
            "last_name": forms.TextInput(attrs={
                "minlength": "2",
                "maxlength": "150",
                "data-validator": "nombre_persona",
            }),
            "telefono": forms.TextInput(attrs={
                "placeholder": "+584121234567",
                "data-validator": "telefono",
                "inputmode": "tel",
                "pattern": "\\+58(4\\d{9}|2\\d{9})",
            }),
        }

    def __init__(self, *args, gestor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.gestor = gestor
        if gestor:
            roles_validos = [r[0] for r in roles_que_puede_asignar(gestor)]
            self.fields["rol"].choices = [
                (v, l) for v, l in Usuario.Roles.choices if v in roles_validos
            ]
            if not gestor.is_superuser:
                self.fields.pop("is_staff", None)

    def clean_email(self):
        valor = validar_email(self.cleaned_data["email"])
        qs = Usuario.objects.filter(email__iexact=valor)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(msg.EMAIL_DUPLICADO)
        return valor

    def clean_first_name(self):
        valor = self.cleaned_data.get("first_name", "").strip()
        if not valor:
            return ""
        return validar_nombre_persona(valor, contexto="nombre")

    def clean_last_name(self):
        valor = self.cleaned_data.get("last_name", "").strip()
        if not valor:
            return ""
        return validar_nombre_persona(valor, contexto="apellido")

    def clean_telefono(self):
        valor = self.cleaned_data.get("telefono", "").strip()
        if not valor:
            return ""
        return normalizar_telefono_ve(valor)
