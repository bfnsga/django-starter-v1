from django.urls import path
from . import views

urlpatterns = [
    path('uploaders', views.uploaders, name='uploaders')
]