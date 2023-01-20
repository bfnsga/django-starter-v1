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
from .models import Organization

from .forms import ProfileForm, PasswordChangeForm, AddUserForm, DeleteUserForm, NameForm, EmailForm
from django.contrib import messages
import stripe

##############################################
## Set User model, initial clients, variables, etc. for use in functions
##############################################
User = get_user_model()
stripe.api_key = settings.STRIPE_API_KEY

####
oauth = OAuth()
oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

##############################################
## Custom wrapper to determine if user is logged and if session is valid
##############################################
def login_redirect(view_func):
    def wrapper(request, *args, **kwargs):

        # Set default redirect page for unauthenticated users
        default_redirect = 'login'

        # Check for session variables            
        if 'is_authorized' in request.session and request.session['is_authorized'] == True:
            # Checks if Auth0 access_token is expired
            expires_at = arrow.get(request.session.get('expires_at'))
            utc_now = arrow.utcnow()

            # Only applies to GET requests, if POST then allow request to go through
            if request.method == 'GET':
                if expires_at > utc_now:
                    return view_func(request, *args, **kwargs)

                # If expired, reauthorize through Auth0 endpoint
                # Redirect to requested page using 'state'
                else:
                    # Clear session
                    django_logout(request)
                    request.session.clear()

                    # Set state session variable for page redirect
                    state_id = str(uuid.uuid4())
                    request.session['state_id'] = {
                        "id": state_id,
                        "view_name": request.resolver_match.view_name
                    }

                    # Send back to login page to re-authenticate
                    return login(request, signup=False, state=state_id)
            else:
                return view_func(request, *args, **kwargs)

        # Redirects to default if user is not authenticated
        return redirect(default_redirect)

    return wrapper

##############################################
## Settings functions (update profile, change password, add/delete users, update billing, etc.)
##############################################
@login_redirect
def dashboard(request):
    # Get user
    user = request.user
    # Process request
    if request.method == 'POST':

        if 'first_name' in request.POST:
            form = NameForm(request, request.POST)
        elif 'email' in request.POST:
            form = EmailForm(request, request.POST)
        elif 'password_1' in request.POST:
            form = PasswordChangeForm(request, request.POST)
        
        if form.is_valid():

            # Save form
            form.save()
            time.sleep(0.5)

            # Return response
            messages.add_message(request, messages.SUCCESS, 'Your profile has been updated')
            return redirect('dashboard')

    else:
        form = {}

    try:
        first_name = user.first_name
    except:
        first_name = ''

    try:
        last_name = user.last_name
    except:
        last_name = ''


    context = {
        'first_name': first_name,
        'last_name': last_name,
        'email': user.email,
        'form': form
    }

    return render(request, 'profile.html', context)

####
@login_redirect
def users(request):
    ## Set variables
    context = {
        'users': User.objects.filter(organization_id=request.user.organization_id),
    }

    # Process request
    if request.method == 'POST':
        if 'email' in request.POST:
            form = AddUserForm(request, request.POST)
        elif 'delete_user_id' in request.POST:
            form = DeleteUserForm(request, request.POST)
        context['form'] = form

        if form.is_valid():
            # Save form
            if 'email' in request.POST:
                auth0_invite_url = form.save()
                ticket = auth0_invite_url['ticket'] + 'type=invite'
                print(ticket)
            else:
                form.save()

            # Return response
            return redirect('users')

    else:
        form = AddUserForm(request)
        context['form'] = form

    return render(request, 'users.html', context)

###
@login_redirect
def billing(request):
    ## Get billing details from Stripe
    organization = Organization.objects.filter(id=request.user.organization_id)
    organization = organization[0]
    stripe_id = organization.stripe_id
    card_id = 'card_1MPD2FD47P4Qx7WsFd4d7iZw'

    card_details = stripe.Customer.retrieve_source(
        stripe_id,
        card_id
    )

    card_brand = card_details['brand']
    exp_month = str(card_details['exp_month'])
    exp_year = str(card_details['exp_year'])
    last_4 = card_details['last4']

    ## Format expiration date
    if len(exp_month) == 1:
        exp_month = '0' + str(exp_month)

    exp_year = exp_year[:-2]

    exp_date = f'{exp_month}/{exp_year}'

    ## Set context
    context = {
        'card': {
            'brand': card_brand,
            'exp_date': exp_date,
            'last_4': last_4
        }
    }

    print(context)

    return render(request, 'billing.html', context)

##############################################
## Auth0 related functions (signup, login, callback, logout)
##############################################
def signup(request):
    return login(request, signup=True)

#####
def login(request, signup=False, state=None):
    # Parse request variables and sets Auth0 parameters
    params = {}

    if request.GET.get('login_hint'):
        params['login_hint'] = request.GET.get('login_hint')
    
    if signup:
        params['screen_hint'] = 'signup'

    if state:
        params['state'] = state

    # Set OAuth params in the client and send request to Auth0
    oauth.auth0.authorize_params = params
    return oauth.auth0.authorize_redirect(request, request.build_absolute_uri(reverse('callback')))

#####
def callback(request):
    # Set variables
    token = oauth.auth0.authorize_access_token(request)
    email = token['userinfo']['email']
    auth0_id = token['userinfo']['sub']
    is_email_verified = token['userinfo']['email_verified']

    # Check if user exists, if not then create a new user
    user, created = User.objects.get_or_create(email=email)
    if created:
        # Create new organization
        organization_id = str(uuid.uuid4())

        # Save Django user
        user.username = email
        user.is_root = True
        user.organization_id = organization_id
        user.auth0_id = auth0_id
        user.save()

        # Create Stripe customer account
        metadata = {
            'organization_id': organization_id
        }

        stripe_customer = stripe.Customer.create(
            description='Programmatic Customer',
            metadata=metadata
        )

        stripe_id = stripe_customer['id']

        # Save organization
        organization = Organization.objects.create(id=organization_id,stripe_id=stripe_id)
        organization.save()

    # Ensure new users verify their email address before they can access the dashboard
    if is_email_verified and not user.is_active:
        user.is_active = True
        user.save()
    elif not is_email_verified and not user.is_active:
        return render(request, 'verify-email.html')

    # Login Django user
    django_login(request, user)

    # Set session variables
    request.session['user_id'] = token['userinfo']['email']
    request.session['expires_at'] = token['expires_at']
    request.session['access_token'] = token['access_token']
    request.session['is_authorized'] = True

    # Redirect
    # Set default redirect page
    redirect_uri = 'dashboard'

    # Get redirect page from session variable, if available
    if 'state_id' in request.session:
        state_param = request.GET.get('state')
        state_id = request.session['state_id']['id']
        if state_param == state_id:
            redirect_uri = request.session['state_id']['view_name']
    
    
    return redirect(request.build_absolute_uri(reverse(redirect_uri)))

#####
def logout(request):

    # Logout Django user & clear session
    django_logout(request)
    request.session.clear()

    # Logout from Auth0
    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse('login')),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )