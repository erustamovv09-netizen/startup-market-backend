from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Startup


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    CustomUser modeli uchun kuchaytirilgan admin panel.

    - list_display: ro'yxatda ko'rinadigan ustunlar
    - search_fields: username va email bo'yicha tezkor qidiruv
    - Qo'shimcha maydonlar (phone_number, telegram_username) tahrirlash
      sahifasida alohida bo'limda ko'rsatiladi.
    """
    list_display = ('username', 'email', 'date_joined', 'last_login', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    ordering = ('-date_joined',)

    # Standart fieldsets-ga qo'shimcha maydonlarni qo'shamiz
    fieldsets = UserAdmin.fieldsets + (
        ("Qo'shimcha ma'lumotlar", {
            "fields": ("phone_number", "telegram_username"),
        }),
    )


@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    """
    Startup modeli uchun kuchaytirilgan admin panel.

    - list_display: asosiy ustunlar
    - list_filter: project_type va created_at bo'yicha yon panel filtri
    - search_fields: nom va egasining @username bo'yicha qidiruv
    - list_editable: is_premium ni ro'yxatdan to'g'ridan-to'g'ri o'zgartirish
    """
    list_display = ('title', 'owner', 'price', 'project_type', 'is_premium', 'created_at')
    list_filter = ('project_type', 'created_at')
    search_fields = ('title', 'owner__username')
    list_editable = ('is_premium',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    autocomplete_fields = ('owner',)  # owner qidiruvi uchun autocomplete
