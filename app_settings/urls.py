from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('signup', views.signup, name='signup'),
    path('callback', views.callback, name='callback'),
    path('stripe_callback', views.stripe_callback, name='stripe_callback'),
    path('settings/profile', views.profile, name='profile'),
    path('settings/company', views.company, name='company'),
    path('settings/users', views.users, name='users'),
    path('settings/billing', views.billing, name='billing'),
    path('subscribe', views.subscribe, name='subscribe'),
    path('checkout', views.checkout, name='checkout'),
    path('checkout/success', views.checkout_success, name='checkout_success')
]