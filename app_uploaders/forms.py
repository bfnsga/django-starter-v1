from django import forms
from .models import Uploader

###########################################
## Functions
###########################################
def phone_e164_format(phone_display):
    phone_e164 = phone_display.replace('(','')
    phone_e164 = phone_e164.replace(')','')
    phone_e164 = phone_e164.replace('-','')
    phone_e164 = phone_e164.replace(' ','')
    phone_e164 = '+1' + phone_e164

    return phone_e164

###########################################
## Forms
###########################################
class AddUploaderForm(forms.Form):
    name = forms.CharField()
    phone = forms.CharField()
    language = forms.CharField()

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean_phone(self):
        ## Set variables
        phone = self.cleaned_data['phone']
        phone_e164 = phone_e164_format(phone)
        current_user = self.request.user

        ## Check that phone number does not already exist
        if Uploader.objects.filter(organization_id=current_user.organization_id,phone_e164=phone_e164).exists():
            raise forms.ValidationError(f'{phone} is in use')

        ## Twilio Lookup

        ## Return
        return phone

    def save(self):
        ## Set variables
        name = self.cleaned_data['name']
        phone = self.cleaned_data['phone']
        language = self.cleaned_data['language']
        current_user = self.request.user

        ## Create new uploader
        uploader = Uploader.objects.create(organization_id=current_user.organization_id)
        uploader.name = name
        uploader.phone_e164 = phone_e164_format(phone)
        uploader.language = language
        uploader.save()

        ## Return
        return uploader

class DeleteUploaderForm(forms.Form):
    delete_uploader_id = forms.CharField()

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def save(self):
        ## Set variables
        delete_uploader_id = self.cleaned_data['delete_uploader_id']
        delete_uploader = Uploader.objects.get(pk=delete_uploader_id)

        ## Delete Uploader from database
        delete_uploader.delete()

        ## Return
        return True