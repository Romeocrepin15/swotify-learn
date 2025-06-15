from django.urls import path, include
from rest_framework.routers import DefaultRouter

# ViewSets API REST
from swotify.views.api_views import (
    EcoleViewSet, ClasseViewSet, EleveViewSet, NoteViewSet,
    EnseignantViewSet, MatiereViewSet, EnseignantMatiereViewSet
)

# ViewSets ou API dashboard personnalisées
from swotify.views.dashboard_views import (
    CustomUserViewSet, AbsenceViewSet, ComportementViewSet, NotificationViewSet, MessageViewSet,
    AbsencesParMatiereViewSet,
    stats_dashboard, moyennes_par_classe, top_classes, alertes_critiques,
    messages_recents, repartition_effectifs_par_classe, repartition_effectifs_par_ecole,
    heures_absence_par_enseignant_matiere, heures_absence_par_eleve, heures_absence_par_classe,
    top_eleves, meilleurs_eleves_par_classe, eleves_par_classe,
    comportements_par_eleve, envoyer_message, liste_utilisateurs, profil,
    login_view, logout_view, test_auth_view,
    PaiementStatsAPIView, PaiementsDetailAPIView,
)
from swotify.views.dashboard_views import (
    MessageAPIView,
    MessageDetailAPIView,
    UserListAPIView,
    ProfilAPIView
)

# ✅ Ceci est le bon router DRF
router = DefaultRouter()

# Enregistrement des ViewSets REST
router.register(r'ecoles', EcoleViewSet)
router.register(r'classes', ClasseViewSet)
router.register(r'eleves', EleveViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'enseignants', EnseignantViewSet)
router.register(r'matieres', MatiereViewSet)
router.register(r'enseignant-matieres', EnseignantMatiereViewSet)
router.register(r'utilisateurs', CustomUserViewSet)
router.register(r'absences', AbsenceViewSet)
router.register(r'comportements', ComportementViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'absences-par-matiere', AbsencesParMatiereViewSet, basename='absences-par-matiere')

from swotify.views.chatbot import chatbot_view, chatbot_sql_view

from django.urls import path
from swotify.views.dashboard_views import MessageAPIView
urlpatterns = [
    # Authentification
    path('login/', login_view),
    path('logout/', logout_view),
    path('test-auth/', test_auth_view),

    # API RESTful via ViewSets
    path('', include(router.urls)),

    # Statistiques générales
    path('indicateurs/', stats_dashboard, name='stats-dashboard'),
    path('moyennes-par-classe/', moyennes_par_classe, name='moyennes-par-classe'),
    path('top-classes/', top_classes, name='top-classes'),
    path('alertes-critiques/', alertes_critiques, name='alertes-critiques'),

    # Répartition
    path('repartition-par-classe/', repartition_effectifs_par_classe, name='repartition-par-classe'),
    path('repartition-par-ecole/', repartition_effectifs_par_ecole, name='repartition-par-ecole'),

    # Absences
    path('heures-absence-par-classe/', heures_absence_par_classe, name='heures-absence-par-classe'),
    path('heures-absence-par-enseignant-matiere/', heures_absence_par_enseignant_matiere, name='heures-absence-par-enseignant-matiere'),
    path('heures-absence-par-eleve/', heures_absence_par_eleve, name='heures_absence_par_eleve'),

    # Élèves et performances
    path('eleves-par-classe/<int:classe_id>/', eleves_par_classe, name='eleves-par-classe'),
    path('meilleurs-eleves-par-classe/<int:classe_id>/', meilleurs_eleves_par_classe, name='meilleurs-eleves-par-classe'),
    path('eleves/<int:eleve_id>/comportements/', comportements_par_eleve, name='comportements-par-eleve'),

    # Paiements
    path('paiement-stats/', PaiementStatsAPIView.as_view(), name='paiement-stats'),
    path("paiements/details/", PaiementsDetailAPIView.as_view(), name="paiements-details"),

    # Messages et utilisateurs
    path('messages-recents/', messages_recents, name='messages-recents'),
    path('utilisateurs/', liste_utilisateurs, name='liste-utilisateurs'),
    path('messages/', MessageAPIView.as_view(), name='messages'),
    path('messages-recents1/', MessageAPIView.as_view(), name='messages-recents'),
    # Profil
    path('profil/', profil, name='profil-utilisateur'),
    
   
    path('messages/<int:message_id>/', MessageDetailAPIView.as_view(), name='message-detail'),
    path('utilisateurs/', UserListAPIView.as_view(), name='utilisateurs'),
    path('profil/', ProfilAPIView.as_view(), name='profil'),
    #IA
    path('chatbot/', chatbot_view, name='chatbot'),
     path('chatbot-sql/', chatbot_sql_view, name='chatbot_sql'),

]
from django.urls import path


