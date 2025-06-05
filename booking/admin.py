from django.contrib import admin

# Register your models here.
from .models import FitnessClass, Booking

@admin.register(FitnessClass)
class FitnessClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'instructor', 'date_time', 'available_slots', 'total_slots', 'is_upcoming']
    list_filter = ['name', 'instructor', 'date_time']
    search_fields = ['name', 'instructor']
    ordering = ['date_time']
    
    def available_slots(self, obj):
        return obj.available_slots
    available_slots.short_description = 'Available'
    
    def is_upcoming(self, obj):
        return obj.is_upcoming
    is_upcoming.boolean = True
    is_upcoming.short_description = 'Upcoming'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'client_name', 'client_email', 'fitness_class', 'status', 'created_at']
    list_filter = ['status', 'fitness_class__name', 'created_at']
    search_fields = ['client_name', 'client_email', 'booking_reference']
    ordering = ['-created_at']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at']
