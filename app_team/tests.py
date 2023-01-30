from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.test import Client
from app_media.models import Image
from app_settings.models import Organization
from .models import TeamMember
from .forms import AddTeamMemberForm

import uuid
import arrow


User = get_user_model()
client = Client()

class TeamViewTestCase(TestCase):
    def setUp(self):
        organization_id = uuid.uuid4()
        # Create test user and organization
        user = User.objects.create_user(username='testuser', email='testuser@test.com', password='')
        user.organization_id = organization_id
        user.is_active = True
        user.save()
        self.user = user

        # Create test organization
        organization = Organization.objects.create(
            id=organization_id,
            trial_end=str(arrow.utcnow().shift(days=+1)),
            subscription_status='subscribed'
        )

        # Create test team member and image
        team_member = TeamMember.objects.create(
            name='Test Team Member',
            phone_e164='+12345678901',
            language='English',
            organization_id=user.organization_id
        )
        Image.objects.create(
            id=str(uuid.uuid4()),
            organization_id=user.organization_id,
            filename_disk = 'testing.jpg',
            filename_download = 'testing-download.jpg',
            type = 'image/jpeg',
            uploaded_by = team_member.pk,
            uploaded_on = '2022-01-01',
            modified_by = team_member.pk,
            modified_on = '2022-01-01',
            filesize = 5000,
            width = 5000,
            height = 5000
        )

    def test_team_view(self):
        # Call the view
        response = client.get('/team')

        self.assertEqual(response.status_code, 302)

        # Log the user in and set session variables
        client.login(username=self.user, password='')
        session = client.session
        session['is_authorized'] = True
        session['expires_at'] = str(arrow.utcnow().shift(days=+1))
        session.save()

        # Call the view
        response = client.get('/team')

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['team_members']), 1)
        self.assertEqual(response.context['team_members'][0].phone_display, '(234) 567-8901')
        self.assertEqual(response.context['team_members'][0].last_uploaded_on, '2022-01-01')
        self.assertIsInstance(response.context['form'], AddTeamMemberForm)

        # Check the view after a post request
        response = client.post('/team', {'name': 'Test Team Member 2', 'phone': '(234) 567-8902', 'language': 'Spanish'})

        # Check the response after a post request
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(TeamMember.objects.all()), 2)
        self.assertEqual(TeamMember.objects.last().phone_e164, '+12345678902')
        self.assertEqual(TeamMember.objects.last().language, 'Spanish')

        ##################
        team_member_id = TeamMember.objects.filter(phone_e164='+12345678902')[0]
        team_member_id = team_member_id.id

        # Check the view after a post request
        response = client.post('/team', {'delete_team_member_id': team_member_id})

        # Check the response after a post request
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(TeamMember.objects.all()), 1)
        self.assertEqual(TeamMember.objects.last().phone_e164, '+12345678901')
