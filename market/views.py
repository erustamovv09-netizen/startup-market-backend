import os
import requests
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth, TruncYear, TruncDay
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


def send_telegram_notification(startup):
    """
    Yangi startup yaratilganda admin Telegram'ga HTML formatida xabar yuboradi.
    getattr() yordamida barcha maydonlar xavfsiz o'qiladi —
    birorta maydon None bo'lsa ham server crash bo'lmaydi.
    """
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id   = os.environ.get('TELEGRAM_CHAT_ID', '')

    # Har bir maydon xavfsiz olinadi — yo'q bo'lsa default qiymat qaytaradi
    title    = getattr(startup, 'title', "Noma'lum")
    price    = getattr(startup, 'price', '0')
    desc     = str(getattr(startup, 'description', ''))
    demo     = getattr(startup, 'demo_link', '')   or "Yo'q"
    github   = getattr(startup, 'github_link', '') or "Yo'q"
    username = startup.owner.username if getattr(startup, 'owner', None) else "Noma'lum"
    email    = startup.owner.email    if getattr(startup, 'owner', None) else "Noma'lum"

    # project_type → o'qilishi qulay nomga (Veb-sayt, Telegram Bot, ...) aylantiriladi
    try:
        category = startup.get_project_type_display()
    except Exception:
        category = getattr(startup, 'project_type', 'Boshqa')

    text = (
        f"🚀 <b>Saytga yangi e'lon joylandi!</b>\n\n"
        f"📌 <b>Loyiha nomi:</b> {title}\n"
        f"📂 <b>Kategoriya:</b> {category}\n"
        f"💰 <b>Narxi:</b> ${price}\n"
        f"📝 <b>Tavsif:</b> {desc}\n\n"
        f"🔗 <b>Demo:</b> {demo}\n"
        f"🐱 <b>GitHub:</b> {github}\n\n"
        f"👤 <b>Joyladi:</b> @{username}\n"
        f"📧 <b>Email:</b> {email}\n\n"
        f"⚙️ <i>Iltimos, admin paneldan tekshiring.</i>"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        requests.post(url, data={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'})
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
        user = self.request.user
        
        # Agar admin bo'lsa, vaqt tekshiruvini o'tkazib yuboramiz
        if not (user.is_staff or user.is_superuser):
            # Oddiy foydalanuvchi: yaratilgan vaqtdan beri o'tgan vaqtni tekshiramiz
            if timezone.now() - startup.created_at > timedelta(minutes=15):
                raise PermissionDenied(
                    "E'lonni faqat joylashtirilgandan so'ng 15 daqiqa ichida tahrirlash mumkin."
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
        send_telegram_notification(startup)


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


class ContactMessageView(APIView):
    """
    POST /api/contact/

    Frontend saytidagi murojaat formasidan kelgan xabarni
    admin Telegram botiga HTML formatida yuboradi.
    Autentifikatsiya talab qilinmaydi — har kim murojaat qila oladi.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        name    = request.data.get('name', '').strip()
        email   = request.data.get('email', '').strip()
        message = request.data.get('message', '').strip()

        # Majburiy maydonlarni tekshirish
        if not name or not email or not message:
            return Response(
                {'error': 'name, email va message maydonlari to\'ldirilishi shart.'},
                status=400
            )

        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        chat_id   = os.environ.get('TELEGRAM_CHAT_ID', '')

        text = (
            f"Saytdan yangi murojaat!\n\n"
            f"Ism: {name}\n"
            f"Email: {email}\n"
            f"Xabar: {message}"
        )

        try:
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                data={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
            )
        except Exception as e:
            print("Telegram murojaat xatoligi:", e)

        return Response({'success': True})


class AdminDashboardStatsView(APIView):
    """
    GET /api/admin/stats/

    Admin panel uchun umumiy statistikani qaytaradi.
    Faqat adminlar kira oladi (IsAdminUser).
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        now = timezone.now()
        
        # Foydalanuvchilar statistikasi
        total_users = CustomUser.objects.count()
        users_this_month = CustomUser.objects.filter(
            date_joined__year=now.year,
            date_joined__month=now.month
        ).count()
        
        # Sotilgan loyihalar statistikasi
        total_sold = Startup.objects.filter(is_sold=True).count()
        # Izoh: Aslida qachon sotilganini bilish uchun 'sold_at' sanasi kerak,
        # hozircha e'lon qilingan sanasi (created_at) joriy oyda bo'lgan
        # va sotilganlarini hisoblaymiz.
        sold_this_month = Startup.objects.filter(
            is_sold=True,
            created_at__year=now.year,
            created_at__month=now.month
        ).count()
        
        return Response({
            'total_users': total_users,
            'users_this_month': users_this_month,
            'total_sold': total_sold,
            'sold_this_month': sold_this_month
        })


class AdvancedAnalyticsView(APIView):
    """
    GET /api/admin/advanced-stats/?filter=this_month|last_month|3_months|1_year|all

    Ilg'or analitika: Foydalanuvchilar va sotuvlar tarixini turli
    vaqt oraliqlariga ko'ra filtrlab va guruhlab qaytaradi.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        filter_type = request.query_params.get('filter', 'all')
        
        users_qs = CustomUser.objects.all()
        sales_qs = Startup.objects.filter(is_sold=True)
        active_qs = Startup.objects.filter(is_sold=False)
        now = timezone.now()
        
        if filter_type == 'this_month':
            users_qs = users_qs.filter(date_joined__year=now.year, date_joined__month=now.month)
            sales_qs = sales_qs.filter(created_at__year=now.year, created_at__month=now.month)
            active_qs = active_qs.filter(created_at__year=now.year, created_at__month=now.month)
            trunc_func = TruncDay
        elif filter_type == 'last_month':
            first_day_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_month_date = first_day_of_this_month - timedelta(days=1)
            users_qs = users_qs.filter(date_joined__year=last_month_date.year, date_joined__month=last_month_date.month)
            sales_qs = sales_qs.filter(created_at__year=last_month_date.year, created_at__month=last_month_date.month)
            active_qs = active_qs.filter(created_at__year=last_month_date.year, created_at__month=last_month_date.month)
            trunc_func = TruncDay
        elif filter_type == '3_months':
            start_date = now - timedelta(days=90)
            users_qs = users_qs.filter(date_joined__gte=start_date)
            sales_qs = sales_qs.filter(created_at__gte=start_date)
            active_qs = active_qs.filter(created_at__gte=start_date)
            trunc_func = TruncMonth
        elif filter_type == '1_year':
            start_date = now - timedelta(days=365)
            users_qs = users_qs.filter(date_joined__gte=start_date)
            sales_qs = sales_qs.filter(created_at__gte=start_date)
            active_qs = active_qs.filter(created_at__gte=start_date)
            trunc_func = TruncMonth
        else: # 'all'
            trunc_func = TruncMonth

        users_field = 'date_joined'
        sales_field = 'created_at'

        # Guruhlash (kunga yoki oyga ko'ra)
        users_data = users_qs.annotate(
            period=trunc_func(users_field)
        ).values('period').annotate(count=Count('id')).order_by('period')
        
        sales_data = sales_qs.annotate(
            period=trunc_func(sales_field)
        ).values('period').annotate(count=Count('id')).order_by('period')
        
        # Ma'lumotlarni bitta dictionary ga yig'amiz
        merged_data = {}
        
        for u in users_data:
            if not u['period']: continue
            label = u['period'].strftime('%Y-%m-%d') if trunc_func == TruncDay else u['period'].strftime('%Y-%m')
            if label not in merged_data:
                merged_data[label] = {'label': label, 'users': 0, 'sales': 0}
            merged_data[label]['users'] = u['count']
            
        for s in sales_data:
            if not s['period']: continue
            label = s['period'].strftime('%Y-%m-%d') if trunc_func == TruncDay else s['period'].strftime('%Y-%m')
            if label not in merged_data:
                merged_data[label] = {'label': label, 'users': 0, 'sales': 0}
            merged_data[label]['sales'] = s['count']
            
        # Dictionary ni ro'yxatga o'tkazish va vaqt bo'yicha tartiblash
        chart_data = list(merged_data.values())
        chart_data.sort(key=lambda x: x['label'])

        return Response({
            'summary': {
                'total_users': users_qs.count(),
                'total_sales': sales_qs.count(),
                'total_active': active_qs.count()
            },
            'chart_data': chart_data
        })
