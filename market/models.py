import requests
from threading import Thread

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


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
        SAAS = 'saas', 'SaaS'
        ECOMMERCE = 'ecommerce', 'E-Commerce'
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
    # ----------------------------------------------------
    # Maxsus loyiha turlari (Bot, Mobil Ilova) uchun havolalar
    # ----------------------------------------------------
    bot_username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Bot Username"
    )
    play_store_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="Play Store Havolasi"
    )
    app_store_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="App Store Havolasi"
    )
    is_premium = models.BooleanField(
        default=False,
        verbose_name="Premium e'lon"
    )
    is_sold = models.BooleanField(
        default=False,
        verbose_name="Sotildi"
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


class Message(models.Model):
    """
    Foydalanuvchilar o'rtasidagi ichki xabarlar (Chat) tizimi.
    Xabarlar ma'lum bir Startup haqida bo'lishi mumkin.
    """
    sender = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        verbose_name="Yuboruvchi"
    )
    receiver = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='received_messages',
        verbose_name="Qabul qiluvchi"
    )
    startup = models.ForeignKey(
        Startup, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='messages',
        verbose_name="Tegishli Startup"
    )
    content = models.TextField(verbose_name="Xabar matni")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan vaqt")

    class Meta:
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
