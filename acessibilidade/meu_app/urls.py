# meu_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('resultado', views.resultado, name='resultados'),
    path('download/<str:filename>', views.download_file, name='download_file'),
]
