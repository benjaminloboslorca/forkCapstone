from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from miapp.views import dashboard_admin_view, CustomPasswordResetView

urlpatterns = [
    # ===== DASHBOARD ADMIN (DEBE IR ANTES DE admin/) =====
    path('admin/dashboard/', dashboard_admin_view, name='admin-dashboard'),
    
    path('admin/', admin.site.urls),
    path('', include('miapp.urls')),
    
    # ===== PASSWORD RESET CON RESEND API =====
    path('auth/olvide-contrasena/', CustomPasswordResetView.as_view(), name='password_reset'),
    
    path('auth/olvide-contrasena/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='miapp/registro/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('auth/olvide-contrasena/confirmar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='miapp/registro/password_reset_confirm.html',
        success_url='/auth/olvide-contrasena/completado/'
    ), name='password_reset_confirm'),
    
    path('auth/olvide-contrasena/completado/', auth_views.PasswordResetCompleteView.as_view(
        template_name='miapp/registro/password_reset_complete.html'
    ), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)