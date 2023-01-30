from django.shortcuts import render, redirect
from app_media.models import Image
from .models import TeamMember
from .forms import AddTeamMemberForm, DeleteTeamMemberForm
import time
from project_config.decorators import login_redirect

###########################################
## FUNCTIONS
###########################################
def phone_format(phone_e164):
    phone_display = phone_e164.replace("+1", "")
    phone_display = phone_display[:6] + "-" + phone_display[6:]
    phone_display = phone_display[:3] + ") " + phone_display[3:]
    phone_display = "(" + phone_display

    return phone_display

###########################################
## VIEWS
###########################################
@login_redirect
def team(request):
    ## Set variables
    team_members = TeamMember.objects.filter(organization_id=request.user.organization_id).order_by('created_on')

    for x in team_members:
        x.phone_display = phone_format(x.phone_e164)
        
        try:
            last_uploaded_on = Image.objects.filter(uploaded_by=x.id).order_by('-uploaded_on')[0]
            ## Add in date handling
        except:
            x.last_uploaded_on = '---' 

    context = {
        'team_members': team_members
    }

    if request.method == 'POST':
        if 'phone' in request.POST:
            form = AddTeamMemberForm(request, request.POST)
        elif 'delete_team_member_id' in request.POST:
            form = DeleteTeamMemberForm(request, request.POST)
        context['form'] = form

        if form.is_valid():
            # Save form
            time.sleep(0.5)
            form.save()

            # Return response
            return redirect('team')

    else:
        form = AddTeamMemberForm(request)
        context['form'] = form

    return render(request, 'team.html', context)