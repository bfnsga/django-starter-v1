from django.db import models

# Create your models here.
class Image(models.Model):
    id = models.UUIDField(primary_key=True)
    organization_id = models.UUIDField()
    filename_disk = models.CharField(max_length=128, unique=True)
    filename_download = models.CharField(max_length=128, unique=True)
    type = models.CharField(max_length=128)
    uploaded_by = models.UUIDField()
    uploaded_on = models.CharField(max_length=128)
    modified_by = models.UUIDField()
    modified_on = models.CharField(max_length=128)
    filesize = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()