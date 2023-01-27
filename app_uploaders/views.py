from django.shortcuts import render, redirect
from app_images.models import Image
from .models import Uploader
from .forms import AddUploaderForm, DeleteUploaderForm
import time

def phone_format(phone_e164):
    phone_display = phone_e164.replace("+1", "")
    phone_display = phone_display[:6] + "-" + phone_display[6:]
    phone_display = phone_display[:3] + ") " + phone_display[3:]
    phone_display = "(" + phone_display

    return phone_display

# Create your views here.
def uploaders(request):
    ## Set variables
    uploaders = Uploader.objects.filter(organization_id=request.user.organization_id).order_by('created_on')

    for x in uploaders:
        x.phone_display = phone_format(x.phone_e164)
        
        try:
            last_uploaded_on = Image.objects.filter(uploaded_by=x.id).order_by('-uploaded_on')[0]
            ## Add in date handling
        except:
            x.last_uploaded_on = '---' 

    context = {
        'uploaders': uploaders
    }

    if request.method == 'POST':
        if 'phone' in request.POST:
            form = AddUploaderForm(request, request.POST)
        elif 'delete_uploader_id' in request.POST:
            form = DeleteUploaderForm(request, request.POST)
        context['form'] = form

        if form.is_valid():
            # Save form
            time.sleep(0.5)
            form.save()

            # Return response
            return redirect('uploaders')

    else:
        form = AddUploaderForm(request)
        context['form'] = form

    return render(request, 'uploaders.html', context)