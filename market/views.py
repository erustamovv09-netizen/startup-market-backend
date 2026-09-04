from rest_framework import generics, permissions, filters

from .models import Startup
from .serializers import StartupSerializer, UserRegistrationSerializer, UserSerializer


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


class StartupListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/startups/  — barcha startuplar ro'yxati (hamma ko'ra oladi)
    POST /api/startups/  — yangi startup yaratish (hozircha hamma, keyinchalik IsAuthenticated)

    perform_create — yangi startup yaratilganda `owner` maydonini
    avtomatik ravishda so'rov yuborgan foydalanuvchiga o'rnatadi.
    """
    queryset = Startup.objects.select_related('owner').all()
    serializer_class = StartupSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    # ?search=django     → texnologiya bo'yicha qidiruv
    # ?search=website    → loyiha turi bo'yicha
    # ?search=@alibek    → eganing username bo'yicha (@-ni qo'shish shart emas)
    search_fields = ['title', 'tech_stack', 'project_type', 'owner__username']

    def perform_create(self, serializer):
        """
        JWT autentifikatsiyasi ulangandan so'ng owner avtomatik
        o'rnatiladi. Hozircha autentifikatsiyadan o'tgan bo'lsa
        request.user, aks holda None qoladi.
        """
        if self.request.user.is_authenticated:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()


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
