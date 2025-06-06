from datetime import timedelta
from django.utils import timezone
from booking.models import FitnessClass

now = timezone.now()

FitnessClass.objects.create(
    name="YOGA",
    date_time=now + timedelta(days=1, hours=2),
    total_slots=10,
    booked_slots=0
)

FitnessClass.objects.create(
    name="CARDIO",
    date_time=now + timedelta(days=2, hours=3),
    total_slots=15,
    booked_slots=5
)

FitnessClass.objects.create(
    name="GYM",
    date_time=now + timedelta(days=3),
    total_slots=8,
    booked_slots=8 
)

print("Class created successfully")