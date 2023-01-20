from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('signup', views.signup, name='signup'),
    path('callback', views.callback, name='callback'),
    path('settings/profile', views.dashboard, name='dashboard'),
    path('settings/users', views.users, name='users'),
    path('settings/billing', views.billing, name='billing'),
]