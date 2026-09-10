from django.urls import path
# pyrefly: ignore [missing-import]
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    StartupListCreateView, 
    StartupDetailView, 
    UserRegistrationView, 
    UserProfileView, 
    AdminUserListView,
    ToggleUserStatusView,
    AdminStartupDeleteView,
    AdminStartupUpdateView,
    ToggleStartupPremiumView,
    MyStartupListView,
    UserStartupDeleteView,
    UserStartupUpdateView,
    MessageListCreateView,
    ContactMessageView,
    AdminDashboardStatsView,
    AdvancedAnalyticsView
)

urlpatterns = [
    # ------------------------------------------------------------------
    # Autentifikatsiya endpointlari
    # ------------------------------------------------------------------

    # Yangi foydalanuvchi ro'yxatdan o'tkazish
    # POST /api/register/  →  { username, password, email? }
    path('register/', UserRegistrationView.as_view(), name='user-register'),

    # Login: username va password bilan access + refresh token olish
    # POST /api/login/  →  { username, password }  =>  { access, refresh }
    path('login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),

    # Access token muddati tugaganda refresh token bilan yangilash
    # POST /api/token/refresh/  →  { refresh }  =>  { access }
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Tizimga kirgan foydalanuvchining o'z profili
    # GET/PUT/PATCH /api/profile/  (Authorization: Bearer <access_token>)
    path('profile/', UserProfileView.as_view(), name='user-profile'),

    # ------------------------------------------------------------------
    # Maxsus Admin endpointlari
    # ------------------------------------------------------------------
    
    # Admin Panel Statistikasi (Dashboard)
    # GET /api/admin/stats/
    path('admin/stats/', AdminDashboardStatsView.as_view(), name='admin-stats'),

    # Ilg'or analitika (Advanced Stats)
    # GET /api/admin/advanced-stats/?filter=all|yearly|monthly
    path('admin/advanced-stats/', AdvancedAnalyticsView.as_view(), name='admin-advanced-stats'),

    # Barcha foydalanuvchilar ro'yxati (faqat Admin/Staff uchun)
    # GET /api/admin/users/
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),

    # Foydalanuvchini bloklash / blokdan chiqarish
    # POST /api/admin/users/<id>/toggle-status/
    path('admin/users/<int:pk>/toggle-status/', ToggleUserStatusView.as_view(), name='admin-user-toggle-status'),

    # Admin tomonidan istalgan startupni o'chirish
    # DELETE /api/admin/startups/<id>/delete/
    path('admin/startups/<int:pk>/delete/', AdminStartupDeleteView.as_view(), name='admin-startup-delete'),

    # Admin tomonidan istalgan startupni vaqt chegarasisiz tahrirlash
    # PUT/PATCH /api/admin/startups/<id>/edit/
    path('admin/startups/<int:pk>/edit/', AdminStartupUpdateView.as_view(), name='admin-startup-edit'),

    # Admin tomonidan istalgan startupning premium holatini o'zgartirish
    # POST /api/admin/startups/<id>/toggle-premium/
    path('admin/startups/<int:pk>/toggle-premium/', ToggleStartupPremiumView.as_view(), name='admin-startup-toggle-premium'),

    # ------------------------------------------------------------------
    # Foydalanuvchining shaxsiy (My) Startup endpointlari
    # ------------------------------------------------------------------
    
    # GET /api/my-startups/
    path('my-startups/', MyStartupListView.as_view(), name='my-startups'),

    # DELETE /api/my-startups/<id>/delete/
    path('my-startups/<int:pk>/delete/', UserStartupDeleteView.as_view(), name='user-startup-delete'),

    # PUT/PATCH /api/my-startups/<id>/edit/  (faqat 15 daqiqa ichida)
    path('my-startups/<int:pk>/edit/', UserStartupUpdateView.as_view(), name='user-startup-edit'),

    # ------------------------------------------------------------------
    # Umumiy Startup (loyiha) endpointlari
    # ------------------------------------------------------------------

    # GET (ro'yxat) va POST (yaratish)
    path('startups/', StartupListCreateView.as_view(), name='startup-list-create'),

    # GET (ko'rish), PUT/PATCH (yangilash), DELETE (o'chirish)
    path('startups/<int:pk>/', StartupDetailView.as_view(), name='startup-detail'),

    # ------------------------------------------------------------------
    # Chat (Xabarlar) endpointi
    # ------------------------------------------------------------------
    # GET /api/messages/ (Mening xabarlarim)
    # POST /api/messages/ (Yangi xabar yuborish)
    path('messages/', MessageListCreateView.as_view(), name='messages'),

    # ------------------------------------------------------------------
    # Murojaat (Contact Form) endpointi
    # ------------------------------------------------------------------
    # POST /api/contact/  — frontend formasidan kelgan murojaatni Telegram botga yuboradi
    path('contact/', ContactMessageView.as_view(), name='contact'),
]
