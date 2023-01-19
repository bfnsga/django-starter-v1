from django import forms
from django.contrib.auth import get_user_model
from django.conf import settings
from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
import boto3

###########################################
## Set functions and models
###########################################
User = get_user_model()

def verify_password(email, password):
    try:
        get_token = GetToken(settings.AUTH0_DOMAIN)
        token = get_token.login(client_id=settings.AUTH0_CLIENT_ID, client_secret=settings.AUTH0_CLIENT_SECRET, username=email, password=password, realm='Username-Password-Authentication', scope='email', audience=f'https://{settings.AUTH0_DOMAIN}/api/v2/')
    except:
        return False

    return True

def update_auth0_user(auth0_id,email):
    # Get Auth0 Management API token
    get_token = GetToken(settings.AUTH0_DOMAIN)
    token = get_token.client_credentials(settings.AUTH0_CLIENT_ID,settings.AUTH0_CLIENT_SECRET, f'https://{settings.AUTH0_DOMAIN}/api/v2/')
    mgmt_api_token = token['access_token']

    # Update user email & name via Management API
    auth0 = Auth0(settings.AUTH0_DOMAIN, mgmt_api_token)
    auth0.users.update(auth0_id,{'email': email, 'name': email})

    return True        

###########################################
## Forms
###########################################
class NameForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def save(self):
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        current_user = self.request.user

        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.save()

        return current_user

class EmailForm(forms.Form):
    email = forms.EmailField()

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        current_user = self.request.user

        if current_user.email == email:
            raise forms.ValidationError('This is your current email')
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'{email} is already in use')

        return email

    def save(self):
        email = self.cleaned_data['email']
        current_user = self.request.user

        if current_user.email != email:
            update_auth0_user(current_user.auth0_id, email)

        current_user.email = email
        current_user.save()

        return current_user

class ProfileForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']
        current_user = self.request.user

        if not verify_password(current_user.email, password):
            raise forms.ValidationError('Incorrect password')

        return password

    def clean_email(self):
        email = self.cleaned_data['email']
        current_user = self.request.user

        if current_user.email == email:
            raise forms.ValidationError('This is your current email')
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'{email} is already in use')

        return email

    def save(self):
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        email = self.cleaned_data['email']
        current_user = self.request.user

        if current_user.email != email:
            update_auth0_user(current_user.auth0_id, email)

        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.email = email
        current_user.save()

        return current_user

class PasswordChangeForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    password_1 = forms.CharField(widget=forms.PasswordInput())
    password_2 = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']
        current_user = self.request.user

        if not verify_password(current_user.email, password):
            raise forms.ValidationError('Incorrect password')

        return password

    def clean_password_1(self):
        password_1 = self.cleaned_data['password_1']
        return password_1

    def clean_password_2(self):
        password_2 = self.cleaned_data['password_2']
        return password_2

    def clean(self):
        cleaned_data = super().clean()
        password_1 = cleaned_data.get('password_1')
        password_2 = cleaned_data.get('password_2')

        if password_1 and password_2 and password_1 != password_2:
            raise forms.ValidationError({'password_1': 'Passwords do not match'})

        return cleaned_data

    def save(self, commit=True):
        # Set variables
        current_user = self.request.user
        auth0_id = current_user.auth0_id
        new_password = self.cleaned_data['password_1']

        # Get Auth0 Management API token
        get_token = GetToken(settings.AUTH0_DOMAIN)
        token = get_token.client_credentials(settings.AUTH0_CLIENT_ID,settings.AUTH0_CLIENT_SECRET, f'https://{settings.AUTH0_DOMAIN}/api/v2/')
        mgmt_api_token = token['access_token']

        # Update password
        auth0 = Auth0(settings.AUTH0_DOMAIN, mgmt_api_token)
        auth0.users.update(auth0_id,{'password': new_password})

        return current_user

class AddUserForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        current_user = self.request.user

        if current_user.email == email:
            raise forms.ValidationError(f'You are already logged in as {email}')
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'{email} is already in use')

        return email

    def save(self):
        current_user = self.request.user

        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        email = self.cleaned_data['email']

        ########################
        ## Create User in Auth0

        # Get Auth0 Management API token
        get_token = GetToken(settings.AUTH0_DOMAIN)
        token = get_token.client_credentials(settings.AUTH0_CLIENT_ID,settings.AUTH0_CLIENT_SECRET, f'https://{settings.AUTH0_DOMAIN}/api/v2/')
        mgmt_api_token = token['access_token']

        # Update user email & name via Management API
        auth0 = Auth0(settings.AUTH0_DOMAIN, mgmt_api_token)
        new_user = auth0.users.create({'email': email, 'verify_email': False, 'password': 'Hello123!', 'connection': 'Username-Password-Authentication'})
        
        new_user_id = new_user['user_id']

        ########################
        ## Create User in Django
        user = User.objects.create(username=email,email=email)
        user.organization_id = current_user.organization_id
        user.auth0_id = new_user_id
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        ########################
        ## Create 'Password change ticket'
        ticket = auth0.tickets.create_pswd_change({'result_url': f'http://127.0.0.1:3000/login?login_hint={email}', 'user_id': new_user_id, 'mark_email_as_verified': True})
        
        ########################
        ## Send SES email with link
        

        ########################
        ## Return
        return ticket

class DeleteUserForm(forms.Form):
    delete_user_id = forms.CharField()

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean_delete_user_id(self):
        ## Set variables
        current_user = self.request.user
        delete_user_id = self.cleaned_data['delete_user_id']

        try:
            delete_user = User.objects.get(pk=delete_user_id)
            delete_user_organization_id = delete_user.organization_id
        except:
            raise forms.ValidationError('User does not exist')

        ## Ensure user isn't trying to delete self
        if current_user.pk == delete_user_id:
            raise forms.ValidationError('To delete your account, please visit your Account page')

        ## Ensure current user has permission to delete user
        if not current_user.is_root or current_user.organization_id != delete_user_organization_id:
            raise forms.ValidationError('You do not have permission to delete this account')

        ## Check that user exists in Auth0

        return delete_user_id

    def save(self):
        # Set variables
        delete_user_id = self.cleaned_data['delete_user_id']
        delete_user = User.objects.get(pk=delete_user_id)
        delete_user_auth0_id = delete_user.auth0_id

        # Get Auth0 Management API token
        get_token = GetToken(settings.AUTH0_DOMAIN)
        token = get_token.client_credentials(settings.AUTH0_CLIENT_ID,settings.AUTH0_CLIENT_SECRET, f'https://{settings.AUTH0_DOMAIN}/api/v2/')
        mgmt_api_token = token['access_token']

        # Delete user from Auth0 via Management API
        auth0 = Auth0(settings.AUTH0_DOMAIN, mgmt_api_token)
        auth0.users.delete(delete_user_auth0_id)

        # Delete User from Django database
        delete_user.delete()

        return True

        
