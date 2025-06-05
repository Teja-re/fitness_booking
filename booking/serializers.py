from rest_framework import serializers
from django.utils import timezone
from .models import FitnessClass, Booking
import pytz



class FitnessClassSerializer(serializers.ModelSerializer):
    available_slots = serializers.ReadOnlyField()
    class_type = serializers.CharField(source='get_name_display', read_only=True)
    local_datetime = serializers.SerializerMethodField()
    
    class Meta:
        model = FitnessClass
        fields = '__all__'
        read_only_fields = ['booked_slots']
    
    def get_local_datetime(self, obj):
        """Convert datetime to user's timezone if provided in context."""
        user_timezone = self.context.get('timezone', 'Asia/Kolkata')
        try:
            tz = pytz.timezone(user_timezone)
            local_dt = obj.date_time.astimezone(tz)
            return local_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
        except pytz.exceptions.UnknownTimeZoneError:
            return obj.date_time.strftime('%Y-%m-%d %H:%M:%S UTC')


class BookingCreateSerializer(serializers.Serializer):
    class_id = serializers.IntegerField()
    client_name = serializers.CharField(max_length=100, min_length=2)
    client_email = serializers.EmailField()
    
    def validate_class_id(self, value):
        try:
            fitness_class = FitnessClass.objects.get(id=value)
        except FitnessClass.DoesNotExist:
            raise serializers.ValidationError("Fitness class not found.")
        
        if not fitness_class.is_upcoming:
            raise serializers.ValidationError("Cannot book past classes.")
        
        if fitness_class.is_full:
            raise serializers.ValidationError("Class is fully booked.")
        
        return value
    
    def validate_client_name(self, value):
        if not value.replace(' ', '').isalpha():
            raise serializers.ValidationError("Name should contain only alphabetic characters.")
        return value.title()
    
    def validate(self, attrs):
        try:
            fitness_class = FitnessClass.objects.get(id=attrs['class_id'])
            existing_booking = Booking.objects.filter(
                fitness_class=fitness_class,
                client_email=attrs['client_email'],
                status='CONFIRMED'
            ).exists()
            
            if existing_booking:
                raise serializers.ValidationError({
                    'client_email': 'You have already booked this class.'
                })
        except FitnessClass.DoesNotExist:
            pass  
        return attrs


class BookingSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='fitness_class.get_name_display', read_only=True)
    class_datetime = serializers.DateTimeField(source='fitness_class.date_time', read_only=True)
    instructor = serializers.CharField(source='fitness_class.instructor', read_only=True)
    local_datetime = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = '__all__'
    
    def get_local_datetime(self, obj):
        """Convert class datetime to user's timezone."""
        user_timezone = self.context.get('timezone', 'Asia/Kolkata')
        try:
            tz = pytz.timezone(user_timezone)
            local_dt = obj.fitness_class.date_time.astimezone(tz)
            return local_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
        except pytz.exceptions.UnknownTimeZoneError:
            return obj.fitness_class.date_time.strftime('%Y-%m-%d %H:%M:%S UTC')