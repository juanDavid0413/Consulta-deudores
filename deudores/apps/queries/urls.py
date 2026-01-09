from django.urls import path
from .views import consulta_deudor_view
urlpatterns = [
    path("", consulta_deudor_view, name="consulta_deudor"),
]
