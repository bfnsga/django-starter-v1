import arrow
from django.contrib.auth import logout as django_logout
import uuid
from django.shortcuts import redirect
from .models import Organization

##############################################
## Custom wrapper to determine if user is logged and if session is valid
##############################################
def login_redirect(view_func):
    def wrapper(request, *args, **kwargs):

        # Set default redirect page for unauthenticated users
        default_redirect = 'login'

        # Check for session variables
        if 'is_authorized' in request.session and request.session['is_authorized'] == True:
            # Check if organization is in their free trial
            organization = Organization.objects.get(id=request.user.organization_id)
            if organization.subscription_status == 'trial':
                # Check if free trial has expired
                trial_end = arrow.get(organization.trial_end)
                utc_now = arrow.utcnow()

                # If free trial has expired, redirect to subscription page
                if utc_now > trial_end:
                    return redirect('subscribe')

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
                    return redirect('login')
            else:
                return view_func(request, *args, **kwargs)

        # Redirects to default if user is not authenticated
        return redirect(default_redirect)

    return wrapper