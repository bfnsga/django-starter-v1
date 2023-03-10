from project_config.decorators import login_redirect
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib import messages

##############################################
## MODELS, CLIENTS & VARIABLES
##############################################
User = get_user_model()

##############################################
## VIEWS
##############################################
@login_redirect
def dashboard(request):
    return render(request, 'dashboard.html')