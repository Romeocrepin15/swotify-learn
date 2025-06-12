# swotify_learn/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # Routes API (ViewSets ou autres)
    path('api/', include('swotify.urls.urlsapi')),

    # Routes du dashboard (frontend ou backend si c’est une app Django)
    path('dashboard/', include('swotify.urls.dashboardurls')),

    # JWT authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Pour les fichiers médias en mode développement (photos de profil, etc.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
