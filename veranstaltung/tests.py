from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import UserProfile, Warenkorb, Ticket, Event, EventLocation, Category
import datetime
from django.utils import timezone
# Create your tests here.

class TestUserProfile(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(email='testuser@test.com', password='1234')
        self.time = timezone.now()
        self.userprofile = UserProfile.objects.create(
            nickname='Bill',
            birthday=self.time,
            user=self.user
        )

    def test_count_waren_korb_items(self):
        self.assertEqual('Bill', self.userprofile.nickname)
        self.assertEqual(self.time, self.userprofile.birthday)


class TestEvent(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(email='testuser@test.com', password='1234')
        self.time = timezone.now()

        self.userprofile = UserProfile.objects.create(
            nickname='Bill',
            birthday=self.time,
            user=self.user
        )

        self.event_location = EventLocation.objects.create(
            userID=self.userprofile,
            location='Amsterdam Street',
            standort='Test Allee 5',
            seatingCapacity=3000,
            detail='Test Detail'
        )

        self.category = Category.objects.create(
            title='Testdummy',
            description='This is a test'
        )

        self.event = Event.objects.create(
            name="TestEvent",
            datum=self.time,
            ticketAvailability=False,
            price=20.00,
            artist='Nine Centimeter Nails',
            userID=self.userprofile,
            locationID=self.event_location,
            categoryID=self.category
        )


    def test_name(self):
        self.assertEqual(self.event.name, 'TestEvent')

class TestEventLocation(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(email='testuser@test.com', password='1234')
        self.time = timezone.now()

        self.userprofile = UserProfile.objects.create(
            nickname='Bill',
            birthday=self.time,
            user=self.user
        )

        self.event_location = EventLocation.objects.create(
            userID=self.userprofile,
            location='Amsterdam Street',
            standort='Test Allee 5',
            seatingCapacity=3000,
            detail='Test Detail'
        )

    def test_standort(self):
        self.assertEqual('Amsterdam Street', self.event_location.location)

class TestCategory(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            title='Testdummy',
            description='This is a test'
        )

    def test_title(self):
        self.assertEqual('Testdummy', self.category.title)
        self.assertNotEqual(self.category.description, self.category.title)

class TestTicket(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(email='testuser@test.com', password='1234')
        self.time = timezone.now()

        self.userprofile = UserProfile.objects.create(
            nickname='Bill',
            birthday=self.time,
            user=self.user
        )

        self.event_location = EventLocation.objects.create(
            userID=self.userprofile,
            location='Amsterdam Street',
            standort='Test Allee 5',
            seatingCapacity=3000,
            detail='Test Detail'
        )

        self.category = Category.objects.create(
            title='Testdummy',
            description='This is a test'
        )

        self.event = Event.objects.create(
            name="TestEvent",
            datum=self.time,
            ticketAvailability=False,
            price=20.00,
            artist='Nine Centimeter Nails',
            userID=self.userprofile,
            locationID=self.event_location,
            categoryID=self.category
        )

        self.ticket = Ticket.objects.create(
            userID= self.userprofile,
            eventID=self.event,
            eventLocationID=self.event_location,
            price=self.event.price,
            quantity=1
        )

    def test_seats(self):
        self.assertEqual(3000, self.event_location.seatingCapacity)