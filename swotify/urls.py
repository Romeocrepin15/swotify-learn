# swotify/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import api_views
#from .views import moyennes_par_classe

# Configuration du routeur pour les API
router = DefaultRouter()
router.register(r'ecoles', api_views.EcoleViewSet)
router.register(r'classes', api_views.ClasseViewSet)
router.register(r'eleves', api_views.EleveViewSet)
router.register(r'notes', api_views.NoteViewSet)

# Définition des URLs
urlpatterns = [
    #path('', views.index, name='index'),  # Route pour la page d'accueil de l'application
    path('api/', include(router.urls)),  # Routes API gérées par DefaultRouter
    #path('api/moyennes/', moyennes_par_classe),  # Route pour obtenir les moyennes par classe
]
