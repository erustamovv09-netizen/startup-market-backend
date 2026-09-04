from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Maxsus foydalanuvchi modeli.
    Django'ning standart AbstractUser modelini kengaytiradi.
    Qo'shimcha maydonlar: telefon raqami va Telegram foydalanuvchi nomi.
    """
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefon raqami"
    )
    telegram_username = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Telegram foydalanuvchi nomi"
    )

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"

    def __str__(self):
        return self.username


class Startup(models.Model):
    """
    Sotuvdagi IT loyiha / startup modeli.
    Har bir startup bitta egaga tegishli (CustomUser).
    """

    class ProjectType(models.TextChoices):
        WEBSITE = 'website', 'Veb-sayt'
        TELEGRAM_BOT = 'telegram_bot', 'Telegram Bot'
        MOBILE_APP = 'mobile_app', 'Mobil Ilova'
        OTHER = 'other', 'Boshqa'

    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='startups',
        verbose_name="Egasi"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Loyiha nomi"
    )
    description = models.TextField(
        verbose_name="Tavsif"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Narxi (USD)"
    )
    tech_stack = models.CharField(
        max_length=255,
        verbose_name="Texnologiyalar to'plami",
        help_text="Masalan: Django, React, PostgreSQL"
    )
    project_type = models.CharField(
        max_length=20,
        choices=ProjectType.choices,
        default=ProjectType.OTHER,
        verbose_name="Loyiha turi"
    )
    demo_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="Demo havolasi"
    )
    github_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="GitHub havolasi"
    )
    is_premium = models.BooleanField(
        default=False,
        verbose_name="Premium e'lon"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan sana"
    )

    class Meta:
        verbose_name = "Startup"
        verbose_name_plural = "Startuplar"
        ordering = ['-is_premium', '-created_at']  # Premium e'lonlar birinchi chiqadi

    def __str__(self):
        return f"{self.title} — {self.owner.username} ({self.get_project_type_display()})"
