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

from .forms import NameForm, EmailForm, PasswordChangeForm, AddUserForm, DeleteUserForm, CompanyNameForm
from django.contrib import messages
import stripe

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from project_config.decorators import login_redirect

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
## Settings functions (update profile, change password, add/delete users, update billing, etc.)
##############################################
@csrf_exempt
def stripe_callback(request):
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(
        json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object # contains a stripe.PaymentIntent
        # Then define and call a method to handle the successful payment intent.
        # handle_payment_intent_succeeded(payment_intent)
    elif event.type == 'payment_method.attached':
        payment_method = event.data.object # contains a stripe.PaymentMethod
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
    # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)

@login_redirect
def profile(request):
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
            return redirect('profile')

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

@login_redirect
def company(request):
    ## Set variables
    organization = Organization.objects.get(id=request.user.organization_id)

    context = {
        'company_name': organization.company_name
    }

    ## Check request method
    if request.method =='POST':
        form = CompanyNameForm(request, request.POST)
        if form.is_valid():
            ## Save form
            time.sleep(0.5)
            form.save()

            ## Return
            messages.add_message(request, messages.SUCCESS, 'Your company profile has been updated')
            return redirect('company')

    return render(request, 'company.html', context)

####
@login_redirect
def users(request):
    ## Set variables
    users = []
    for x in User.objects.filter(organization_id=request.user.organization_id).exclude(pk=request.user.pk).order_by('role'):
        users.append(x)

    context = {
        'users': [request.user] + users
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
    previous_page = request.META.get('HTTP_REFERER')

    organization = Organization.objects.get(id=request.user.organization_id)

    session = stripe.billing_portal.Session.create(
        customer=organization.stripe_id,
        return_url=previous_page,
    )

    return redirect(session.url)
    organization = Organization.objects.get(id=request.user.organization_id)

    credit_card = stripe.Customer.list_sources(
        organization.stripe_id,
        object="card",
        limit=1,
    )

    intent = stripe.SetupIntent.create(
        customer=organization.stripe_id
    )

    print(intent.client_secret)

    if len(credit_card['data']) > 0:
        # Parse card details
        card_details = credit_card['data'][0]

        card_brand = card_details['brand']
        exp_month = str(card_details['exp_month'])
        exp_year = str(card_details['exp_year'])
        last_4 = card_details['last4']

        ## Format expiration date
        if len(exp_month) == 1:
            exp_month = '0' + str(exp_month)

        exp_year = exp_year[2:]
        exp_date = f'{exp_month}/{exp_year}'
    else:
        card_brand = ''
        exp_date = ''
        last_4 = ''

    ## Set context
    context = {
        'card': {
            'brand': card_brand,
            'exp_date': exp_date,
            'last_4': last_4
        },
        'client_secret': intent.client_secret
    }

    return render(request, 'billing.html', context)

##############################################
## Auth0 related functions (signup, login, callback, logout)
##############################################
def subscribe(request):
    organization = Organization.objects.get(id=request.user.organization_id)
    subscription_status = organization.subscription_status

    tier1_price_id = 'price_1MU9WZD47P4Qx7WskZSLlXoo'
    tier2_price_id = 'price_1MU9WtD47P4Qx7WsUBhA0PIS'
    tier3_price_id = 'price_1MU9X7D47P4Qx7WsEh6WX57S'

    context = {
        'subscription_status': subscription_status,
        'tiers': {
            'tier1': {
                'price': '$29',
                'url': tier1_price_id
            },
            'tier2': {
                'price': '$79',
                'url': tier2_price_id
            },
            'tier3': {
                'price': '$149',
                'url': tier3_price_id
            }
        }
    }

    return render(request, 'subscribe.html', context)

def checkout(request):
    ## Set variables
    price_id = request.GET.get('price_id')

    ## Get Stripe Customer ID based on Organization
    organization_id = request.user.organization_id
    organization = Organization.objects.get(id=organization_id)
    stripe_id = organization.stripe_id

    ## If Stripe Customer does not exist, then create one
    if not stripe_id:
        metadata = {
            'organization_id': organization_id
        }

        stripe_customer = stripe.Customer.create(
            email=request.user.email,
            metadata=metadata
        )

        stripe_id = stripe_customer['id']

        organization.stripe_id = stripe_id
        organization.save()

    ## Create a Stripe Checkout Session
    try:
        checkout_session = stripe.checkout.Session.create(
            customer=stripe_id,
            success_url='http://127.0.0.1:8000/checkout/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://127.0.0.1:8000/subscribe',
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription'
        )

        return redirect(checkout_session.url)
    except:
        return redirect('subscribe')

def checkout_success(request):
    ## Set variables
    checkout_session_id = request.GET.get('session_id')
    organization = Organization.objects.get(id=request.user.organization_id)

    ## Get Stripe Checkout Session Customer
    session = stripe.checkout.Session.retrieve(
        checkout_session_id,
        expand=['line_items']
    )
    product_id = session['line_items']['data'][0]['price']['product']
    payment_status = session['payment_status']

    ## Update organization subscription
    if product_id == 'prod_NEcm1sUlocuPNG':
        subscription_status = '1' # Good tier
    elif product_id == 'prod_NEcmoYQn6zzwvU':
        subscription_status = '2' # Better tier
    elif product_id == 'prod_NEcmA5JKzU0VnP':
        subscription_status = '3' # Best tier

    ## Update organization
    organization.subscription_status = subscription_status
    organization.save()

    return redirect('dashboard')

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
        # Create new organization & set free trial expiration
        utc_now = arrow.utcnow()
        #trial_expires_at=str(utc_now.shift(days=+14).ceil('day'))
        trial_end=str(utc_now)

        organization_id = str(uuid.uuid4())
        organization = Organization.objects.create(
            id=organization_id,
            trial_end=trial_end
        )
        organization.save()

        # Save Django user
        user.username = email
        user.is_rootuser = True
        user.organization_id = organization_id
        user.auth0_id = auth0_id
        user.save()

    # New users must verify their email before accessing the application
    if is_email_verified and not user.is_active:
        user.is_active = True
        user.save()        

    elif not is_email_verified and not user.is_active:
        return render(request, 'verify-email.html')

    # Login Django user
    django_login(request, user)

    # Set session variables
    request.session['expires_at'] = token['expires_at']
    request.session['is_authorized'] = True

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