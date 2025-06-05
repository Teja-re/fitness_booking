from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import FitnessClass, Booking
from datetime import timedelta

class FitnessClassModelTest(TestCase):
    def setUp(self):
        self.future_class = FitnessClass.objects.create(
            name='YOGA',
            instructor='Intructor 1',
            date_time=timezone.now() + timedelta(days=1),
            total_slots=10
        )
        
        self.past_class = FitnessClass.objects.create(
            name='ZUMBA',
            instructor='Instructor 2',
            date_time=timezone.now() - timedelta(days=1),
            total_slots=5
        )
    
    def test_available_slots_calculation(self):
        """Test available slots calculation."""
        self.assertEqual(self.future_class.available_slots, 10)
        
        # Book some slots
        self.future_class.booked_slots = 3
        self.future_class.save()
        self.assertEqual(self.future_class.available_slots, 7)
    
    def test_is_upcoming_property(self):
        """Test is_upcoming property."""
        self.assertTrue(self.future_class.is_upcoming)
        self.assertFalse(self.past_class.is_upcoming)
    
    def test_can_book_method(self):
        """Test can_book method logic."""
        self.assertTrue(self.future_class.can_book())
        self.assertFalse(self.past_class.can_book())
        
        # Make class full
        self.future_class.booked_slots = 10
        self.future_class.save()
        self.assertFalse(self.future_class.can_book())


class BookingAPITest(APITestCase):
    def setUp(self):
        self.future_class = FitnessClass.objects.create(
            name='YOGA',
            instructor='Instructor 3',
            date_time=timezone.now() + timedelta(days=1),
            total_slots=10
        )
        
        self.full_class = FitnessClass.objects.create(
            name='HIIT',
            instructor='Instructor 4',
            date_time=timezone.now() + timedelta(days=2),
            total_slots=5,
            booked_slots=5
        )
    
    def test_get_classes_success(self):
        url = reverse('get_classes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['count'], 1)  
        self.assertEqual(response.data['classes'][0]['name'], 'YOGA')
    
    def test_create_booking_success(self):
        url = reverse('create_booking')
        data = {
            'class_id': self.future_class.id,
            'client_name': 'John Doe',
            'client_email': 'test@gmail.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('booking_reference', response.data['booking'])
        booking = Booking.objects.get(client_email='john@example.com')
        self.assertEqual(booking.fitness_class, self.future_class)
        self.future_class.refresh_from_db()
        self.assertEqual(self.future_class.booked_slots, 1)
    
    def test_create_booking_full_class(self):
        url = reverse('create_booking')
        data = {
            'class_id': self.full_class.id,
            'client_name': 'Jane Doe',
            'client_email': 'test2@gmail.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_create_duplicate_booking(self):
        Booking.objects.create(
            fitness_class=self.future_class,
            client_name='John Doe',
            client_email='test@gmail.com'
        )
        url = reverse('create_booking')
        data = {
            'class_id': self.future_class.id,
            'client_name': 'John Doe',
            'client_email': 'test@gmail.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already booked', str(response.data))
    
    def test_get_bookings_success(self):
        booking = Booking.objects.create(
            fitness_class=self.future_class,
            client_name='John Doe',
            client_email='john@example.com'
        )
        url = reverse('get_bookings')
        response = self.client.get(url, {'email': 'john@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['bookings'][0]['booking_reference'], booking.booking_reference)
    
    def test_get_bookings_missing_email(self):
        url = reverse('get_bookings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('Email parameter is required', response.data['error'])