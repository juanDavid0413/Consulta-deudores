from django.urls import path
from .views import upload_bd2

app_name = 'uploads'

urlpatterns = [
    path('bd2/', upload_bd2, name='upload_bd2'),
]
