from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, EmailValidator
from django.utils import timezone
import pytz


class FitnessClass(models.Model):
    CLASS_TYPES = [
        ('YOGA', 'Yoga'),
        ('ZUMBA', 'Zumba'),
        ('HIIT', 'HIIT'),
        ('GYM', 'Gym'),
        ('CARDIO', 'Cardio'),
    ]
    name = models.CharField(max_length=100, choices=CLASS_TYPES,null=True,blank=True)
    instructor = models.CharField(max_length=100,null=True,blank=True)
    date_time = models.DateTimeField(null=True,blank=True)
    total_slots = models.PositiveIntegerField(blank=True,null=True)
    booked_slots = models.PositiveIntegerField(null=True,blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Fitness Class'
        verbose_name_plural = 'Fitness Classes'
    
    @property
    def available_slots(self):
        return max(0, self.total_slots - self.booked_slots)
    
    @property
    def is_full(self):
        return self.available_slots <= 0
    
    @property
    def is_upcoming(self):
        return self.date_time > timezone.now()
    
    def can_book(self, slots_needed=1):
        return (
            self.is_upcoming and 
            not self.is_full and 
            self.available_slots >= slots_needed
        )
    
    def book_slot(self):
        if not self.can_book():
            raise ValueError("Cannot book")
        
        self.booked_slots += 1
        self.save(update_fields=['booked_slots', 'updated_at'])





class Booking(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('WAITLIST', 'Waitlist'),
    ]
    
    fitness_class = models.ForeignKey(
        FitnessClass, 
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField(validators=[EmailValidator()])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED',)
    booking_reference = models.CharField(max_length=20, unique=True, null=True,blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"{self.client_name} - {self.fitness_class} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Generate booking reference if not provided."""
        if not self.booking_reference:
            import uuid
            self.booking_reference = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)