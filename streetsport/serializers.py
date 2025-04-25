from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Stadium, Booking, Payment
from django.utils import timezone


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', User.Role.USER)
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Username or password is incorrect")


class StadiumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stadium
        fields = '__all__'
        read_only_fields = ['owner']


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user', 'is_paid']

    def validate(self, data):
        stadium = data['stadium']
        date = data['date']
        start_time = data['start_time']
        end_time = data['end_time']

        if start_time >= end_time:
            raise serializers.ValidationError("Boshlanish vaqti tugash vaqtidan oldin bo‘lishi kerak")

        # mavjud bronlar bilan to‘qnashuvni tekshiramiz
        existing = Booking.objects.filter(
            stadium=stadium,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        # update holati uchun hozirgi instance'ni chiqaramiz
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise serializers.ValidationError("Bu vaqt oralig‘ida bu stadion allaqachon bron qilingan")

        return data

        # To'lovni faqat admin/manager tomonidan o'zgartirish uchun alohida validatsiya qilish
    def update(self, instance, validated_data):
        if 'is_paid' in validated_data:
            if not self.context['request'].user.is_staff:  # admin yoki stadium owner
                raise serializers.ValidationError("Sizda to'lov statusini almashtirish ruxsati yo'q!")
        return super().update(instance, validated_data)


class StadiumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stadium
        fields = '__all__'

    def update(self, instance, validated_data):
        # Faqat stadion egasi yoki admin managerni o'zgartira olishiga ruxsat beramiz
        if 'manager' in validated_data:
            user = self.context['request'].user
            if not user.is_staff and user != instance.owner:
                raise serializers.ValidationError("Only the stadium owner or admin can assign a manager.")
        return super().update(instance, validated_data)


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['user', 'stadium', 'date', 'is_paid', 'created_at']

    def create(self, validated_data):
        return Booking.objects.create(**validated_data)

