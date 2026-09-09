import requests
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()

from .models import Startup, CustomUser, Message
from .serializers import (
    StartupSerializer, 
    UserRegistrationSerializer, 
    UserSerializer,
    MessageSerializer
)


def send_telegram_notification(startup_title, startup_price, owner_username):
    """
    Yangi startup yaratilganda admin Telegram'ga xabar yuboradi.
    Tarmoq xatoligi yuz bersa, server ishini to'xtatmaslik uchun
    xatoni tutib, faqat konsolga chiqarib qo'yadi.
    """
    bot_token = "8977368056:AAECjvzo9X3bL639i21pN-QcRrf_Ou-hueg"
    chat_id = "8273165378"
    text = (
        f"🚀 Saytga yangi e'lon joylandi!\n\n"
        f"📌 Loyiha nomi: {startup_title}\n"
        f"💰 Narxi: ${startup_price}\n"
        f"👤 Joyladi: @{owner_username}\n\n"
        f"Iltimos, admin panelga kirib tekshiring."
    )
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        requests.post(url, data={'chat_id': chat_id, 'text': text})
    except Exception as e:
        print("Telegram bot xatoligi:", e)


class UserRegistrationView(generics.CreateAPIView):
    """
    POST /api/register/  — yangi foydalanuvchi ro'yxatdan o'tkazish.

    Muvaffaqiyatli ro'yxatdan o'tgandan so'ng yangi foydalanuvchi
    ma'lumotlari (id, username, email) qaytariladi.
    Parol hech qachon javobda ko'rinmaydi (write_only).
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/profile/  — o'z profil ma'lumotlarini ko'rish.
    PUT   /api/profile/  — profilni to'liq yangilash.
    PATCH /api/profile/  — profilni qisman yangilash (tavsiya etiladi).

    Faqat tizimga kirgan foydalanuvchiga ruxsat beriladi (IsAuthenticated).
    `get_object()` doim `request.user`-ni qaytaradi — ya'ni har bir
    foydalanuvchi faqat o'z profilini ko'ra va tahrir qila oladi.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # PK yoki lookup field kerak emas — har doim token egasi qaytariladi
        return self.request.user


class AdminUserListView(generics.ListAPIView):
    """
    GET /api/admin/users/ — barcha foydalanuvchilar ro'yxatini qaytaradi.
    
    Faqat staff va superuser ruxsatiga ega bo'lgan foydalanuvchilar uchun.
    Eng oxirgi qo'shilgan foydalanuvchilar birinchi bo'lib chiqadi.
    """
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminStartupDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/admin/startups/<pk>/delete/
    
    Faqat adminlarga ruxsat berilgan bo'lib, istalgan startupni 
    bazadan butunlay o'chirib tashlash imkonini beradi.
    """
    queryset = Startup.objects.all()
    permission_classes = [permissions.IsAdminUser]


class AdminStartupUpdateView(generics.RetrieveUpdateAPIView):
    """
    PUT/PATCH /api/admin/startups/<pk>/edit/

    Admin istalgan startupni istalgan vaqtda tahrirlashi mumkin.
    15 daqiqalik vaqt chekovi bu yerda qo'llanilmaydi.
    Faqat admin/staff foydalana oladi (IsAdminUser).
    """
    serializer_class = StartupSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Startup.objects.all()


class ToggleStartupPremiumView(APIView):
    """
    POST /api/admin/startups/<pk>/toggle-premium/
    
    Startup'ning premium (is_premium) holatini o'zgartiradi.
    Faqat admin/staff foydalana oladi.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        startup = get_object_or_404(Startup, pk=pk)
        
        startup.is_premium = not startup.is_premium
        startup.save()
        return Response({"is_premium": startup.is_premium})


class ToggleUserStatusView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        return Response({"id": user.id, "is_active": user.is_active})


class MyStartupListView(generics.ListAPIView):
    """
    GET /api/my-startups/
    
    Faqat joriy tizimga kirgan foydalanuvchiga tegishli startuplarni qaytaradi.
    """
    serializer_class = StartupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Startup.objects.filter(owner=self.request.user)


class UserStartupDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/my-startups/<pk>/delete/
    
    Foydalanuvchi o'ziga tegishli bo'lgan startupni o'chirib tashlaydi.
    Boshqa odamning startupini o'chirishga ruxsat yo'q, chunki
    `get_queryset()` faqat shaxsiy startuplarni qaytaradi.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Startup.objects.filter(owner=self.request.user)


class UserStartupUpdateView(generics.RetrieveUpdateAPIView):
    """
    PUT/PATCH /api/my-startups/<pk>/edit/

    Foydalanuvchi o'ziga tegishli startupni faqat yaratilganidan
    keyin 15 daqiqa ichida tahrirlashi mumkin.
    Muddatdan o'tgan bo'lsa, 403 PermissionDenied xatosi qaytariladi.
    """
    serializer_class = StartupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Faqat joriy foydalanuvchiga tegishli startuplarni qaytaramiz
        return Startup.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        startup = serializer.instance
        # Yaratilgan vaqtdan beri o'tgan vaqtni tekshiramiz
        if timezone.now() - startup.created_at > timedelta(minutes=15):
            raise PermissionDenied(
                "E'lonni faqat yaratilganidan keyin 15 daqiqa ichida tahrirlash mumkin."
            )
        serializer.save()


class StartupListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/startups/  — barcha startuplar ro'yxati (hamma ko'ra oladi)
    POST /api/startups/  — yangi startup yaratish (hozircha hamma, keyinchalik IsAuthenticated)

    perform_create — yangi startup yaratilganda `owner` maydonini
    avtomatik ravishda so'rov yuborgan foydalanuvchiga o'rnatadi.
    """
    queryset = Startup.objects.select_related('owner').all()
    serializer_class = StartupSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    # ?search=django     → texnologiya bo'yicha qidiruv
    # ?search=website    → loyiha turi bo'yicha
    # ?search=@alibek    → eganing username bo'yicha (@-ni qo'shish shart emas)
    search_fields = ['title', 'tech_stack', 'project_type', 'owner__username']

    def perform_create(self, serializer):
        startup = serializer.save(owner=self.request.user)
        print("DIQQAT: E'lon saqlandi, botga xabar ketmoqda...")
        send_telegram_notification(startup.title, startup.price, self.request.user.username)


class StartupDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/startups/<pk>/  — bitta startup ko'rish
    PUT    /api/startups/<pk>/  — to'liq yangilash
    PATCH  /api/startups/<pk>/  — qisman yangilash
    DELETE /api/startups/<pk>/  — o'chirish

    Hozircha AllowAny — Next.js frontend bilan oson test qilish uchun.
    Keyinchalik faqat egasiga ruxsat beruvchi IsOwnerOrReadOnly permission
    qo'shish mumkin.
    """
    queryset = Startup.objects.select_related('owner').all()
    serializer_class = StartupSerializer
    permission_classes = [permissions.AllowAny]


class MessageListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/messages/  — Tizimga kirgan foydalanuvchining barcha xabarlarini qaytaradi
    POST /api/messages/  — Boshqa foydalanuvchiga yangi xabar yuborish
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Foydalanuvchi qabul qiluvchi yoxud yuboruvchi bo'lgan xabarlarni qaytaramiz
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).select_related('sender', 'receiver', 'startup').order_by('created_at')

    def perform_create(self, serializer):
        # Yuboruvchini avtomatik tarzda joriy foydalanuvchi etib belgilaymiz
        serializer.save(sender=self.request.user)
