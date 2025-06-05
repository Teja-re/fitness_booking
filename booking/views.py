from django.shortcuts import render

# Create your views here.
from rest_framework import status,viewsets
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import FitnessClass, Booking
from .serializers import (
    FitnessClassSerializer, 
    BookingCreateSerializer, 
    BookingSerializer
)
from django.db.models import F
from rest_framework.decorators import action
import logging
logger = logging.getLogger(__name__)


class FitnessClassViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FitnessClass.objects.all()
    serializer_class = FitnessClassSerializer

    def list(self, request, *args, **kwargs):
        try:
            user_timezone = request.GET.get('timezone')
            class_type = request.GET.get('class_type', '').upper()

            queryset = FitnessClass.objects.filter(
                date_time__gt=timezone.now()
            ).exclude(
                booked_slots__gte=F('total_slots')
            )

            if class_type and class_type in dict(FitnessClass.CLASS_TYPES):
                queryset = queryset.filter(name=class_type)

            serializer = self.get_serializer(queryset, many=True, context={'timezone': user_timezone})
            logger.info(f"Retrieved {len(serializer.data)} classes for timezone: {user_timezone}")

            return Response({
                'success': True,
                'count': len(serializer.data),
                'timezone': user_timezone,
                'classes': serializer.data
            })
        except Exception as e:
            logger.error(f"Error retrieving classes: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve classes',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookingViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def create_booking(self, request):
        try:
            serializer = BookingCreateSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid booking data: {serializer.errors}")
                return Response({
                    'success': False,
                    'error': 'Validation failed',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            validated_data = serializer.validated_data

            with transaction.atomic():
                fitness_class = FitnessClass.objects.select_for_update().get(
                    id=validated_data['class_id']
                )
                if not fitness_class.can_book():
                    return Response({
                        'success': False,
                        'error': 'Booking failed',
                        'message': 'Class is no longer available for booking'
                    }, status=status.HTTP_409_CONFLICT)

                booking = Booking.objects.create(
                    fitness_class=fitness_class,
                    client_name=validated_data['client_name'],
                    client_email=validated_data['client_email']
                )

                fitness_class.book_slot()

                booking_serializer = BookingSerializer(
                    booking,
                    context={'timezone': request.GET.get('timezone', 'Asia/Kolkata')}
                )

                logger.info(f"Booking created: {booking.booking_reference} for {booking.client_email}")
                return Response({
                    'success': True,
                    'message': 'Booking confirmed successfully',
                    'booking': booking_serializer.data
                }, status=status.HTTP_201_CREATED)

        except FitnessClass.DoesNotExist:
            logger.error(f"Class not found: {request.data.get('class_id')}")
            return Response({
                'success': False,
                'error': 'Class not found'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            return Response({
                'success': False,
                'error': 'Booking failed',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def get_bookings(self, request):
        try:
            client_email = request.GET.get('email')
            user_timezone = request.GET.get('timezone', 'Asia/Kolkata')
            booking_status = request.GET.get('status', '').upper()

            if not client_email:
                return Response({
                    'success': False,
                    'error': 'Email parameter is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            queryset = Booking.objects.filter(client_email=client_email)
            if booking_status and booking_status in dict(Booking.STATUS_CHOICES):
                queryset = queryset.filter(status=booking_status)

            serializer = BookingSerializer(
                queryset,
                many=True,
                context={'timezone': user_timezone}
            )

            logger.info(f"Retrieved {len(serializer.data)} bookings for {client_email}")
            return Response({
                'success': True,
                'count': len(serializer.data),
                'email': client_email,
                'timezone': user_timezone,
                'bookings': serializer.data
            })
        except Exception as e:
            logger.error(f"Error retrieving bookings: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve bookings',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)