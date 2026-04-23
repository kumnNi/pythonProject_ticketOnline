from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin


#Create your models here.
#https://github.com/akjasim/cb_dj_custom_user_model/
class CustomerUserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):

    username = None
    email = models.EmailField(unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = CustomerUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    nickname = models.CharField(max_length=100)
    birthday = models.DateTimeField(auto_now=False, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nickname}"

    class Meta:
        ordering = ['nickname']

    def count_waren_korb_items(self):
        count = 0
        if self.user.is_authenticated:
            waren_korb_items = Warenkorb.objects.filter(myuser=self)
            count = sum(item.quantity for item in waren_korb_items)

        return count

    def count_ticket(self):
        num = 0
        if self.user.is_authenticated:
            ticket_items = Ticket.objects.filter(userID=self)
            num = sum(item.quantity for item in ticket_items)

        return num

    def delete(self, *args, **kwargs):
        print("Deleting UserProfile:", self)
        self.user.delete()
        super().delete(*args, **kwargs)
        print("After deletion - UserProfile exists:", UserProfile.objects.filter(pk=self.pk).exists())


class EventLocation(models.Model):
    location = models.CharField( max_length = 255)
    standort = models.CharField( max_length = 255)
    seatingCapacity = models.IntegerField()
    detail = models.CharField(max_length=255)
    userID = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.location}"

    class Meta:
        ordering = ['location']


class Category(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ['title']


class Event(models.Model):
    name = models.CharField( max_length=255)
    datum = models.DateTimeField(auto_now=False)
    ticketAvailability = models.BooleanField(auto_created=False)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    artist = models.CharField(max_length=255)
    locationID = models.ForeignKey(EventLocation, on_delete=models.CASCADE)
    userID = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    categoryID = models.ForeignKey(Category, on_delete=models.CASCADE)
    video_source = models.CharField(null=True, blank=True, max_length=255)
    img_source = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['datum']


class Warenkorb(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    myuser = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    eventID = models.ForeignKey(Event, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    sessionID = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.eventID}"

    def total_price(self):
        return self.quantity * int(self.eventID.price)

    def get_number_of_items(self):
        #total_quantity = sum(self.quantity)
        #waren_korps_items = Warenkorp.objects.filter(quantity=total_quantity)
        #print(waren_korps_items)
        return Warenkorb.objects.filter(myuser=self.myuser).count()

    @staticmethod
    def get_or_create_for_anonymous_user(session_key, event_id):
        warenkorb, created = Warenkorb.objects.get_or_create(session_key=session_key, anonymous_user=session_key)
        if created:
            warenkorb.eventID_id = event_id
            warenkorb.save()
        return warenkorb


class Ticket(models.Model):
    userID = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    eventID = models.ForeignKey(Event, on_delete=models.CASCADE)
    eventLocationID = models.ForeignKey(EventLocation, on_delete=models.PROTECT)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    quantity = models.IntegerField(default=1)
    #warenKorb = models.ForeignKey(Warenkorb, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.eventID}"

    class Meta:
        ordering = ['eventID']





