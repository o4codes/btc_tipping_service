import uuid
from django.db import models
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, phone, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, phone, password, **extra_fields)

    def create_superuser(self, email, phone, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    sec_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    bitnob_id = models.CharField(max_length=100, unique=True, blank=False, null=False)
    email = models.EmailField(verbose_name="email address", unique=True)
    phone_regex = RegexValidator(
        regex=r"^\d{9,13}$", message="max of 13 digits allowed."
    )
    country_code = models.CharField(max_length=4, default="+234")
    phone = models.CharField(
        validators=[phone_regex], max_length=17, blank=False, null=False
    )
    satoshis = models.BigIntegerField(null=False, blank=False, default=1000)
    first_name = models.CharField(verbose_name="first name", max_length=30, blank=False)
    last_name = models.CharField(verbose_name="last name", max_length=30, blank=False)
    is_active = models.BooleanField(verbose_name="active", default=False)
    is_staff = models.BooleanField(verbose_name="staff", default=False)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone"]

    def __str__(self):
        """Returns email as string representation of the User object"""
        return self.email

    def get_full_name(self):
        """Returns the first_name plus the last_name, with a space in between."""
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Sends an email to this User."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
        
    def deduct_satoshis(self, amount):
        self.satoshis -= amount
        self.save()
        return self.satoshis
    
    def add_satoshis(self, amount):
        self.satoshis += amount
        self.save()
        return self.satoshis
