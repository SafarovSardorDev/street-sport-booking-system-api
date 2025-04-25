from django.urls import path
from .views import RegisterView, LoginView
from rest_framework.routers import DefaultRouter
from .views import StadiumViewSet, BookingViewSet, MarkAsPaidView, AssignManagerView 

router = DefaultRouter()
router.register(r'stadiums', StadiumViewSet, basename='stadium')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('bookings/<int:pk>/mark_as_paid/', MarkAsPaidView.as_view(), name='mark_as_paid'),
    path('stadiums/<int:pk>/assign_manager/', AssignManagerView.as_view(), name='assign_manager'),
]

urlpatterns += router.urls
