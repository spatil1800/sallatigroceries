import uuid

import pytz
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import FileExtensionValidator
from django.db import models
from rest_framework.authtoken.models import Token

from sallati_groceries.accounts.managers import UserManager
from sallati_groceries.common.custom_storages import PublicMediaStorage
from sallati_groceries.common.model_utils import TimeStampedModel


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )

    name = models.CharField(max_length=150)
    email = models.EmailField(blank=False, unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    timezone = models.CharField(
        max_length=32,
        choices=tuple(zip(pytz.all_timezones, pytz.all_timezones)),
        default="UTC",
    )
    avatar = models.ImageField(
        blank=True,
        storage=PublicMediaStorage(folder="/icons/"),
        validators=[FileExtensionValidator(["png", "jpeg", "jpg"])],
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
