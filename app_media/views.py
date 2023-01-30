from project_config.decorators import login_redirect
from django.shortcuts import render
from django.contrib.auth import get_user_model
from .models import Image
from django.contrib import messages

##############################################
## MODELS, CLIENTS, & VARIABLES
##############################################
User = get_user_model()

##############################################
## VIEWS
##############################################
@login_redirect
def media(request):
    images = Image.objects.all()
    context = {
        'organization_id': 'a63f471c-004b-446a-8be3-e61c88f18ddf',
        'images': images
    }
    return render(request, 'media.html', context)