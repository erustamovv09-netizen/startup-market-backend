from rest_framework import serializers

from .models import CustomUser, Startup


class OwnerSerializer(serializers.ModelSerializer):
    """
    Startup egasi haqida minimal ma'lumot beruvchi o'qish uchun serializer.
    Faqat kerakli public maydonlar chiqariladi — parol va boshqa maxfiy
    ma'lumotlar hech qachon ko'rinmaydi.
    """
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email')


class UserSerializer(serializers.ModelSerializer):
    """
    Tizimga kirgan foydalanuvchining o'z profilini ko'rish va
    tahrirlash uchun serializer (`GET /api/profile/`, `PATCH /api/profile/`).

    - Parol bu yerda ko'rinmaydi va o'zgartirilmaydi (buning uchun
      alohida endpoint kerak bo'ladi).
    - `email` ixtiyoriy — bo'sh qoldirish mumkin.
    """
    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'first_name',     # Ko'rsatiladigan ism (Display Name)
            'email',
            'phone_number',
            'telegram_username',
            'is_staff',       # Admin panel kirish huquqi
            'is_superuser',   # To'liq superadmin huquqi
            'is_active',      # Faol yoki bloklangan
            'date_joined',    # Ro'yxatdan o'tgan sanasi
        )
        # Bular faqat o'qish uchun — API orqali o'zgartirib bo'lmaydi
        read_only_fields = ('id', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
            'first_name': {'required': False},
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Yangi foydalanuvchi ro'yxatdan o'tkazish uchun serializer.

    - `password` maydoni faqat yozish uchun (`write_only=True`) —
      hech qachon API javobida ko'rinmaydi.
    - `create()` metodi Django'ning `set_password()` funksiyasini ishlatadi,
      bu parolni xavfsiz tarzda bcrypt/PBKDF2 bilan hashlaydi.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Kamida 8 ta belgi bo'lishi shart."
    )

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'email', 'password', 'phone_number', 'telegram_username')
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'phone_number': {'required': False},
            'telegram_username': {'required': False},
        }

    def create(self, validated_data):
        """
        Oddiy `.create()` o'rniga bu metod ishlatiladi chunki parolni
        `set_password()` orqali hashlash kerak. To'g'ridan-to'g'ri
        `password` matnini saqlash xavfli!
        """
        # Parolni validated_data dan ajratib olamiz
        password = validated_data.pop('password')
        # Foydalanuvchini parolsiz yaratamiz
        user = CustomUser(**validated_data)
        # Parolni xavfsiz hashlab o'rnatamiz
        user.set_password(password)
        user.save()
        return user



class StartupSerializer(serializers.ModelSerializer):
    """
    Startup modeli uchun to'liq serializer.

    - `owner_info`  — faqat o'qish uchun: eganing id, username, email ni ko'rsatadi.
    - `owner`       — yozish uchun: yangi startup yaratishda owner ID qabul qiladi.
    - `project_type_display` — insoniy o'qiladigan loyiha turi (masalan: "Telegram Bot").
    """

    # Eganing to'liq ma'lumotlarini o'qish uchun (nested)
    owner_info = OwnerSerializer(source='owner', read_only=True)

    # Insoniy ko'rinadigan loyiha turi matni
    project_type_display = serializers.CharField(
        source='get_project_type_display',
        read_only=True
    )

    class Meta:
        model = Startup
        fields = (
            'id',
            'owner',           # Yozish uchun (PK)
            'owner_info',      # O'qish uchun (nested)
            'title',
            'description',
            'price',
            'tech_stack',
            'project_type',
            'project_type_display',
            'demo_link',
            'github_link',
            'is_premium',
            'created_at',
        )
        read_only_fields = ('id', 'created_at', 'owner_info', 'project_type_display')
        extra_kwargs = {
            # owner maydoni yozishda ixtiyoriy — view'da avtomatik o'rnatiladi
            'owner': {'required': False},
        }
