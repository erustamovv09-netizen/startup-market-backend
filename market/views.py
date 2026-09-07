from rest_framework import generics, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Startup, CustomUser, Message
from .serializers import (
    StartupSerializer, 
    UserRegistrationSerializer, 
    UserSerializer,
    MessageSerializer
)


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
    """
    POST /api/admin/users/<pk>/toggle-status/
    
    Foydalanuvchining is_active (faol/bloklangan) holatini o'zgartiradi.
    Faqat admin/staff foydalana oladi.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        
        # Superadminni tasodifan bloklab qo'ymaslik uchun kichik himoya
        if user.is_superuser:
            return Response({"error": "Superuser holatini o'zgartirib bo'lmaydi!"}, status=400)
            
        user.is_active = not user.is_active
        user.save()
        return Response({"is_active": user.is_active})


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
        serializer.save(owner=self.request.user)


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
