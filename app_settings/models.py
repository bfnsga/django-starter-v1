from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractUser):
    ## Custom fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    username = models.CharField(max_length=128, unique=True)
    email = models.EmailField(unique=True)
    auth0_id = models.CharField(max_length=128, blank=True, null=True)
    organization_id = models.UUIDField(blank=True, null=True)
    is_rootuser = models.BooleanField(default=False)

    ## Django defaults
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

class Organization(models.Model):
    id = models.UUIDField(primary_key=True)
    stripe_id = models.CharField(max_length=96, blank=True, null=True, default=None)
    subscription_status = models.CharField(max_length=96, default='trial')
    trial_end = models.CharField(max_length=96, blank=True, null=True, default=None)
    is_lapsed = models.BooleanField(default=False)