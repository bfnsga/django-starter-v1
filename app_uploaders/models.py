from django.db import models
import uuid

# Create your models here.
class Uploader(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization_id = models.UUIDField()
    name = models.CharField(max_length=128, blank=True, null=True)
    phone_e164 = models.CharField(max_length=128)
    language = models.CharField(max_length=128)
    created_on = models.DateField(auto_now_add=True)