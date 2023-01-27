from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
import uuid
import arrow
import time
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as django_login

from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
import json

from django.contrib import messages

from django.http import HttpResponse

from app_settings.decorators import login_redirect

from app_images.models import Image

##############################################
## Set User model
##############################################
User = get_user_model()

##############################################
## Settings functions (update profile, change password, add/delete users, update billing, etc.)
##############################################
@login_redirect
def dashboard(request):
    images = Image.objects.all()
    context = {
        'organization_id': 'a63f471c-004b-446a-8be3-e61c88f18ddf',
        'images': images
    }
    return render(request, 'dashboard.html', context)