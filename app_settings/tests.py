from unittest import TestCase
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from unittest.mock import Mock
from .views import login
from django.urls import reverse

# Custom User model
User = get_user_model()