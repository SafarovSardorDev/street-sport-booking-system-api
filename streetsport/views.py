from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status, viewsets
from .serializers import RegisterSerializer, LoginSerializer, StadiumSerializer, BookingSerializer
from .models import User, Stadium, Booking, Payment
from .permissions import IsAdminOrOwner, IsOwnerOrAdminOrReadOnly
from drf_yasg.utils import swagger_auto_schema

# 🧾 Foydalanuvchini ro'yxatdan o'tkazish view
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "user": serializer.data,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 🔐 Login view (Token olish uchun)
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ⚽ Stadionlar bilan ishlovchi ViewSet (CRUD)
class StadiumViewSet(viewsets.ModelViewSet):
    queryset = Stadium.objects.all()
    serializer_class = StadiumSerializer
    permission_classes = [IsAdminOrOwner]  # Faqat admin va ownerlarga ruxsat

    # ➕ Stadion yaratayotganda avtomatik owner ni qo‘shib qo‘yadi
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # 🔎 Foydalanuvchiga qarab stadionlarni filterlaydi
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # Swagger uchun maxsus
            return Stadium.objects.none()

        user = self.request.user
        if not user.is_authenticated:
            return Stadium.objects.none()  # Swagger yoki anonim foydalanuvchiga bo‘sh queryset qaytariladi

        if user.role == 'admin':
            return Stadium.objects.all()
        return Stadium.objects.filter(active=True)

# 📅 Booking (Bron) viewset
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOrReadOnly]

    # ➕ Booking yaratganda foydalanuvchini avtomatik qo‘shadi
    @swagger_auto_schema(
        operation_description="Create a booking. Must be authenticated."
    )
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # 🔎 Har bir foydalanuvchi o‘ziga tegishli bookinglarni ko‘radi
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Booking.objects.none()

        if user.role == 'admin':
            return Booking.objects.all()
        elif user.role == 'owner':
            return Booking.objects.filter(stadium__owner=user)
        return Booking.objects.filter(user=user)


# ✅ Bookingni "to'langan" deb belgilash uchun API
class MarkAsPaidView(APIView):
    permission_classes = [IsAdminUser | IsOwnerOrAdminOrReadOnly]  # Admin yoki owner

    def patch(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ruxsatni tekshirish
        if not (request.user.is_staff or booking.stadium.owner == request.user):
            return Response({"detail": "You do not have permission to mark this booking as paid."}, status=status.HTTP_403_FORBIDDEN)

        # Statusni yangilash
        booking.is_paid = True
        booking.save()
        return Response({"detail": "Booking marked as paid."}, status=status.HTTP_200_OK)

# 👨‍💼 Stadion uchun manager biriktirish
class AssignManagerView(APIView):
    permission_classes = [IsAdminUser | IsOwnerOrAdminOrReadOnly]  # Admin yoki owner

    def patch(self, request, pk):
        try:
            stadium = Stadium.objects.get(pk=pk)
        except Stadium.DoesNotExist:
            return Response({"detail": "Stadium not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ruxsatni tekshirish
        if not (request.user.is_staff or stadium.owner == request.user):
            return Response({"detail": "You do not have permission to assign a manager to this stadium."}, status=status.HTTP_403_FORBIDDEN)

        # Managerni tayinlash (qisman update)
        serializer = StadiumSerializer(stadium, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
