from django.contrib.auth.models import AbstractUser
from django.db import models

# Custom foydalanuvchi modeli. AbstractUser'dan meros olib, unga qo‘shimcha 'role' maydoni qo‘shilgan.
class User(AbstractUser):
    # Foydalanuvchi rollari uchun tanlovlar.
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'        # Saytga to‘liq kirish huquqiga ega bo‘lgan administrator
        OWNER = 'owner', 'Owner'        # Stadion egasi
        MANAGER = 'manager', 'Manager'  # Stadion boshqaruvchisi
        USER = 'user', 'User'           # Oddiy foydalanuvchi

    # Har bir foydalanuvchiga role biriktiriladi.
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)

    def __str__(self):
        # Foydalanuvchini ko‘rsatishda foydalanuvchi nomi va roli ko‘rsatiladi
        return f"{self.username} ({self.role})"

# Stadion modelini ifodalaydi
class Stadium(models.Model):
    name = models.CharField(max_length=100)  # Stadion nomi
    location = models.CharField(max_length=255)  # Stadion joylashuvi
    description = models.TextField(blank=True)  # Qo‘shimcha tavsif
    image = models.ImageField(upload_to='stadiums/', blank=True, null=True)  # Stadion rasmi
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)  # Soatlik narx
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_stadiums')  # Stadion egasi
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_stadiums')  # Boshqaruvchi (ixtiyoriy)

    def __str__(self):
        return self.name

# Bron qilish modelini ifodalaydi
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Kim bron qilgan
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE)  # Qaysi stadion bron qilingan
    date = models.DateField()  # Qaysi sanaga bron qilingan
    created_at = models.TimeField(auto_now_add=True)  # Qachon yaratilgan
    updated_at = models.TimeField(auto_now=True)  # Qachon yangilangan

    # To‘lov usuli tanlovlari
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card'),  # Kartadan to‘lov
        ('cash', 'Cash'),  # Naqd to‘lov
    ]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)  # Tanlangan to‘lov usuli
    is_paid = models.BooleanField(default=False)  # To‘lov qilingan-qilinmaganligi

    def __str__(self):
        return f"{self.user.username} - {self.stadium.name} ({self.date})"

# To‘lov modelini ifodalaydi
class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)  # Qaysi bron uchun to‘lov qilindi
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # To‘lov summasi
    method = models.CharField(max_length=10, choices=Booking.PAYMENT_METHOD_CHOICES)  # To‘lov usuli
    status = models.CharField(max_length=20, choices=[('paid', 'Paid'), ('failed', 'Failed')])  # To‘lov holati
    created_at = models.DateTimeField(auto_now_add=True)  # To‘lov yaratilgan vaqti

    def __str__(self):
        return f"Payment for {self.booking}"
