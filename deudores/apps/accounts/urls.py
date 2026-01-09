from django.urls import path
from .views import login_view, logout_view, dashboard, create_user
from . import views

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('users/create/', create_user, name='create_user'),
]
