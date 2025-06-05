from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import FitnessClassViewSet, BookingViewSet

router = DefaultRouter()
router.register(r'classes', FitnessClassViewSet, basename='classes')

booking_list = BookingViewSet.as_view({
    'post': 'create_booking',
    'get': 'get_bookings'
})

urlpatterns = [
    path('', include(router.urls)),
    path('bookings/', booking_list, name='booking-actions'),
]