from django.urls import path

from . import views

app_name = "operaciones"

urlpatterns = [
    path("", views.centro_operativo, name="centro"),
]
