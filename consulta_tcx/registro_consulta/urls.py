from django.urls import path
from . import views

app_name = "registro_consulta"
urlpatterns = [
    path("", views.index, name = "index"),
    path("agrega_pac", views.agrega_pac, name = "agrega_pac"),
    path("busca_pac", views.busca_pac, name = "busca_pac"),
    path("chart", views.chart, name= "chart"),
    path("chart2", views.chart2, name= "chart")
]