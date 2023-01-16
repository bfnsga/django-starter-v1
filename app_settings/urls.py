from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('settings/profile', views.dashboard, name='dashboard'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('signup', views.signup, name='signup'),
    path('callback', views.callback, name='callback'),
    path('settings/password', views.password_change, name='password_change'),
    path('users', views.users, name='users'),
    path('users/add', views.add_user, name='add-user'),
    path('users/delete', views.delete_user, name='delete_user'),
    path('billing', views.billing, name='billing')
]