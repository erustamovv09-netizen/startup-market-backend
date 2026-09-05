from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    StartupListCreateView, 
    StartupDetailView, 
    UserRegistrationView, 
    UserProfileView, 
    AdminUserListView,
    ToggleUserStatusView,
    AdminStartupDeleteView
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
    
    # Barcha foydalanuvchilar ro'yxati (faqat Admin/Staff uchun)
    # GET /api/admin/users/
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),

    # Foydalanuvchini bloklash / blokdan chiqarish
    # POST /api/admin/users/<id>/toggle-status/
    path('admin/users/<int:pk>/toggle-status/', ToggleUserStatusView.as_view(), name='admin-user-toggle-status'),

    # Admin tomonidan istalgan startupni o'chirish
    # DELETE /api/admin/startups/<id>/delete/
    path('admin/startups/<int:pk>/delete/', AdminStartupDeleteView.as_view(), name='admin-startup-delete'),

    # ------------------------------------------------------------------
    # Startup (loyiha) endpointlari
    # ------------------------------------------------------------------

    # GET (ro'yxat) va POST (yaratish)
    path('startups/', StartupListCreateView.as_view(), name='startup-list-create'),

    # GET (ko'rish), PUT/PATCH (yangilash), DELETE (o'chirish)
    path('startups/<int:pk>/', StartupDetailView.as_view(), name='startup-detail'),
]
