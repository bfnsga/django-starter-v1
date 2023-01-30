from django import forms
from .models import TeamMember
from app_settings.models import Organization
from django.conf import settings

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

###########################################
## MODELS, CLIENTS & VARIABLES
###########################################
twilio_account_sid = settings.TWILIO_ACCOUNT_SID
twilio_auth_token = settings.TWILIO_AUTH_TOKEN
twilio_client = Client(twilio_account_sid, twilio_auth_token)

###########################################
## FUNCTIONS
###########################################
def phone_format(phone_display):
    phone_e164 = phone_display.replace('(','')
    phone_e164 = phone_e164.replace(')','')
    phone_e164 = phone_e164.replace('-','')
    phone_e164 = phone_e164.replace(' ','')
    phone_e164 = '+1' + phone_e164

    return phone_e164

###########################################
## FORMS
###########################################
class AddTeamMemberForm(forms.Form):
    name = forms.CharField()
    phone = forms.CharField()
    language = forms.CharField()

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean_phone(self):
        ########
        phone = self.cleaned_data['phone']
        phone_e164 = phone_format(phone)

        current_user = self.request.user
        organization_id = current_user.organization_id


        ########
        if TeamMember.objects.filter(organization_id=organization_id,phone_e164=phone_e164).exists():
            raise forms.ValidationError(f'{phone} is in use')

        ########
        if settings.MY_ENVIRONMENT == 'PROD':
            try:
                phone_lookup = twilio_client.lookups.v2.phone_numbers(phone_e164).fetch()
            except TwilioRestException as err:
                print(err)

            if not phone_lookup.valid:
                raise forms.ValidationError('Invalid phone number')

            if phone_lookup.country_code != 'US':
                raise forms.ValidationError('Must be a US phone number')

        ########
        return phone

    def save(self):
        ########
        name = self.cleaned_data['name']
        phone = self.cleaned_data['phone']
        language = self.cleaned_data['language']

        current_user = self.request.user
        organization_id = current_user.organization_id
        organization = Organization.objects.get(pk=organization_id)

        ########
        team_member = TeamMember.objects.create(
            organization_id = organization_id,
            name = name,
            phone_e164 = phone_format(phone),
            language = language
        )
        team_member.save()

        ########
        if settings.MY_ENVIRONMENT == 'PROD':
            try:
                twilio_client.messages.create(
                    body=f"You've been added to {organization.company_name}! Please save this phone number.",
                    from_='+17033729548',
                    to=phone_format(phone)
                )
            except TwilioRestException as err:
                print(err)

        ########
        return True

###########################################
class DeleteTeamMemberForm(forms.Form):
    delete_team_member_id = forms.CharField()

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def save(self):
        ########
        delete_team_member_id = self.cleaned_data['delete_team_member_id']
        delete_team_member = TeamMember.objects.get(pk=delete_team_member_id)

        ########
        delete_team_member.delete()

        ########
        return True