from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Avg, Count, F, Q, Sum
from swotify.models import Classe, Eleve, Note, Absence, Ecole, Comportement
from rest_framework.decorators import api_view
from swotify.models import Message  # Assure-toi que ce modèle est bien importé
from swotify.serializers import ClasseSerializer, MessageSerializer  # Assure-toi que le serializer existe aussi
from django.db.models import Prefetch
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view
from django.db.models import Sum, F


from django.http import JsonResponse
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from swotify.models import Absence
# ======== STATISTIQUES GÉNÉRALES DU DASHBOARD ========
@api_view(['GET'])
def stats_dashboard(request):
    effectif_total = Eleve.objects.count()
    effectif_filles = Eleve.objects.filter(sexe='F').count()
    effectif_garcons = Eleve.objects.filter(sexe='M').count()
    moyenne_generale = Note.objects.aggregate(moyenne=Avg('valeur'))['moyenne'] or 0

    if effectif_total > 0:
        nb_reussites = Eleve.objects.annotate(
            moyenne=Avg('note__valeur')
        ).filter(moyenne__gte=10).count()
        taux_reussite = (nb_reussites / effectif_total) * 100
        taux_echec = 100 - taux_reussite
    else:
        taux_reussite = taux_echec = 0

    stats = {
        'moyenne_generale': round(moyenne_generale, 2),
        'taux_reussite': round(taux_reussite, 2),
        'taux_echec': round(taux_echec, 2),
        'effectif_total': effectif_total,
        'effectif_filles': effectif_filles,
        'effectif_garcons': effectif_garcons,
    }
    return Response(stats)


# ======== MOYENNES PAR CLASSE ========
@api_view(['GET'])
def moyennes_par_classe(request):
    moyennes = Classe.objects.annotate(
        moyenne_classe=Avg('eleves__note__valeur')
    ).values('nom', 'moyenne_classe')
    return Response(moyennes)


# ======== TOP 3 CLASSES ========
@api_view(['GET'])
def top_classes(request):
    order_by = request.GET.get('order_by', 'moyenne')

    if order_by == 'moyenne':
        classes = Classe.objects.annotate(
            moyenne=Avg('eleves__note__valeur')
        ).order_by('-moyenne')[:]
    else:
        classes = Classe.objects.all()[:]

    top_classes = [{
        'id': classe.id,
        'nom': classe.nom,
        'moyenne': round(classe.moyenne or 0, 2),
        'nombre_eleves': classe.eleves.count()
    } for classe in classes]

    return Response(top_classes)


# ======== TOP 3 ÉLÈVES GLOBAUX OU PAR CLASSE ========

@api_view(['GET'])
def top_eleves(request, classe_id):
    try:
        eleves = (
            Eleve.objects
            .filter(classe__id=classe_id)
            .annotate(moyenne=Avg('note__valeur'))
            .order_by('-moyenne')
        )

        resultats = [
            {
                'id': eleve.id,
                'nom': eleve.nom,
                'moyenne': round(eleve.moyenne or 0, 2),
            }
            for eleve in eleves
        ]

        return Response(resultats)
    except Exception as e:
        return Response({"error": str(e)}, status=500)



# ======== MEILLEURS ÉLÈVES D’UNE CLASSE ========

@api_view(['GET'])
def meilleurs_eleves_par_classe(request, classe_id):
    # On vérifie que la classe existe (optionnel)
    if not Classe.objects.filter(id=classe_id).exists():
        return Response({'error': 'Classe non trouvée'}, status=404)
    
    eleves = Eleve.objects.filter(classe_id=classe_id).annotate(
        moyenne=Avg('note__valeur')  # Remplace 'note' par 'notes' si besoin
    ).order_by('-moyenne')[:3]

    meilleurs_eleves = [{
        'nom': eleve.nom,
        'moyenne': round(eleve.moyenne or 0, 2),
        'classe': eleve.classe.nom
    } for eleve in eleves]

    return Response(meilleurs_eleves)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Avg, Count, Sum, F, Q
from swotify.models import Classe, Eleve

@api_view(['GET'])
def alertes_critiques(request):
    alertes = []

    # Alertes pour classes à moyenne faible
    classes_basses = Classe.objects.annotate(
        moyenne_classe=Avg('eleves__note__valeur')
    ).filter(moyenne_classe__lt=8)

    for classe in classes_basses:
        alertes.append({
            'type': 'classe',
            'id': classe.id,
            'classe': classe.nom,
            'alerte': '⚠️ Moyenne de classe faible',
            'gravite': 3,
            'moyenne': round(classe.moyenne_classe or 0, 2),
            'resume': f"La classe {classe.nom} a une moyenne générale inférieure à 8.",
            'suggestion': "Analyser les causes possibles et proposer un soutien pédagogique."
        })

    # Alertes pour classes avec taux d'absentéisme > 30h/élève
    classes_absences = Classe.objects.annotate(
        total_heures_absence=Sum('eleves__absences__nombre_heures'),
        total_eleves=Count('eleves')
    ).filter(
        total_eleves__gt=0,
        total_heures_absence__gt=F('total_eleves') * 30
    )

    for classe in classes_absences:
        taux = classe.total_heures_absence / classe.total_eleves
        alertes.append({
            'type': 'classe',
            'id': classe.id,
            'classe': classe.nom,
            'alerte': '🚨 Taux d’absentéisme élevé (classe)',
            'gravite': 1,
            'taux_absence_moyen': round(taux, 2),
            'resume': f"La classe {classe.nom} présente un taux moyen d'absences supérieur à 30h par élève.",
            'suggestion': "Organiser une réunion avec les enseignants."
        })

    # Élèves avec moyenne < 8
    eleves_faibles = Eleve.objects.annotate(
        moyenne=Avg('note__valeur')
    ).filter(moyenne__lt=8)

    for eleve in eleves_faibles:
        alertes.append({
            'type': 'eleve',
            'id': eleve.id,
            'eleve': str(eleve),
            'classe': eleve.classe.nom,
            'alerte': '⚠️ Moyenne générale faible',
            'gravite': 3,
            'moyenne': round(eleve.moyenne or 0, 2),
            'resume': f"{eleve} a une moyenne inférieure à 8.",
            'suggestion': "Prévoir un accompagnement personnalisé."
        })

    # Élèves avec comportements négatifs ≥ 3
    eleves_disciplinaires = Eleve.objects.annotate(
        nb_negatifs=Count('comportements', filter=Q(comportements__positif=False))
    ).filter(nb_negatifs__gte=3)

    for eleve in eleves_disciplinaires:
        alertes.append({
            'type': 'eleve',
            'id': eleve.id,
            'eleve': str(eleve),
            'classe': eleve.classe.nom,
            'alerte': '🚫 Trop de comportements négatifs',
            'gravite': 2,
            'comportements_negatifs': eleve.nb_negatifs,
            'resume': f"{eleve} a cumulé {eleve.nb_negatifs} comportements négatifs.",
            'suggestion': "Convoquer l’élève et ses parents."
        })

    # Élèves avec > 30h d’absence
    eleves_absents = Eleve.objects.annotate(
        total_heures_absence=Sum('absences__nombre_heures')  # ✅ correction ici
    ).filter(total_heures_absence__gt=30)

    for eleve in eleves_absents:
        alertes.append({
            'type': 'eleve',
            'id': eleve.id,
            'eleve': str(eleve),
            'classe': eleve.classe.nom,
            'alerte': '🚨 Taux d’absentéisme élevé (élève)',
            'gravite': 1,
            'heures_absence': eleve.total_heures_absence,
            'resume': f"{eleve} a cumulé plus de 30h d'absences.",
            'suggestion': "Prévoir une rencontre avec les parents."
        })

    return Response(alertes)


from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def messages_recents(request):
    utilisateur_connecte = request.user
    messages = Message.objects.filter(destinataire=utilisateur_connecte).order_by('-date_envoi')[:5]
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

# ======== RÉPARTITION DES EFFECTIFS PAR CLASSE ========
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Q
from swotify.models import Classe  # adapte le chemin si nécessaire

@api_view(['GET'])
def repartition_effectifs_par_classe(request):
    repartition = Classe.objects.annotate(
        nombre_eleves=Count('eleves'),
        nombre_filles=Count('eleves', filter=Q(eleves__sexe='F')),
        nombre_garcons=Count('eleves', filter=Q(eleves__sexe='M'))
    ).values('id', 'nom', 'nombre_eleves', 'nombre_filles', 'nombre_garcons')
    
    return Response(repartition)

@api_view(['GET'])
def repartition_effectifs_par_ecole(request):
    repartition = Ecole.objects.annotate(
        nombre_eleves=Count('classes__eleves')
    ).values('nom', 'nombre_eleves')
    return Response(repartition)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from swotify.models import Eleve

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from swotify.models import Eleve

@api_view(['GET'])
def heures_absence_par_eleve(request):
    classe_id = request.GET.get('classe_id', None)
    order = request.GET.get('order', 'asc')  # 'asc' par défaut

    # Base queryset
    queryset = Eleve.objects.all()

    # Filtrer par classe si classe_id fourni
    if classe_id:
        queryset = queryset.filter(classe_id=classe_id)

    # Annoter avec total heures absence
    queryset = queryset.annotate(
        total_heures_absence=Sum('absences__nombre_heures')
    )

    # Trier selon order
    if order == 'desc':
        queryset = queryset.order_by('-total_heures_absence')
    else:
        queryset = queryset.order_by('total_heures_absence')

    # Extraire les données désirées
    data = queryset.values('nom', 'total_heures_absence')

    return Response(data)


@api_view(['GET'])
def heures_absence_par_classe(request):
    resultats = Classe.objects.annotate(
        total_heures_absence=Coalesce(Sum('absences__nombre_heures'), 0)
    ).values('nom', 'total_heures_absence').order_by('-total_heures_absence')

    return Response(resultats)


@api_view(['GET'])
def heures_absence_par_enseignant_matiere(request):
    classe_id = request.GET.get('classe_id')
    enseignant_id = request.GET.get('enseignant_id')
    matiere_id = request.GET.get('matiere_id')

    filters = {}

    if classe_id:
        filters['classe__id'] = classe_id
    if enseignant_id:
        filters['enseignant__id'] = enseignant_id
    if matiere_id:
        filters['matiere__id'] = matiere_id

    # Global (sans regroupement par classe)
    global_data = Absence.objects.filter(**filters).values(
        'enseignant__id',
        'enseignant__user__last_name',
        'enseignant__user__first_name',
        'matiere__id',
        'matiere__nom'
    ).annotate(
        total_heures_absence=Coalesce(Sum('nombre_heures'), 0)
    ).order_by('-total_heures_absence')

    # Répartition par classe
    par_classe_data = Absence.objects.filter(**filters).values(
        'enseignant__id',
        'enseignant__user__last_name',
        'enseignant__user__first_name',
        'matiere__id',
        'matiere__nom',
        'classe__id',
        'classe__nom'
    ).annotate(
        total_heures_absence=Coalesce(Sum('nombre_heures'), 0)
    ).order_by('classe__nom', '-total_heures_absence')

    return Response({
        "global": list(global_data),
        "par_classe": list(par_classe_data)
    })


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from swotify.serializers import CustomUserSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profil_utilisateur(request):
    user = request.user
    serializer = CustomUserSerializer(user)
    return Response(serializer.data)




from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profil(request):
    user = request.user
    if user.is_authenticated:
        return Response({
            "nom": user.last_name,
            "prenom": user.first_name,
            "photo": user.photo_de_profil.url if user.photo_de_profil else None
        })
    return Response({"detail": "Non authentifié"}, status=401)


from rest_framework import viewsets
from django.db.models import Sum
from swotify.models import Absence
from swotify.serializers import AbsenceParMatiereSerializer

class AbsencesParMatiereViewSet(viewsets.ViewSet):
    def list(self, request):
        annee = request.query_params.get('annee')
        trimestre = request.query_params.get('trimestre')
        mois = request.query_params.get('mois')
        semaine = request.query_params.get('semaine')

        absences = Absence.objects.all()

        if annee:
            absences = absences.filter(date__year=int(annee))

        if trimestre:
            trimestre = int(trimestre)
            if trimestre in [1, 2, 3]:
                mois_debut = (trimestre - 1) * 3 + 1
                mois_fin = mois_debut + 2
                absences = absences.filter(date__month__gte=mois_debut, date__month__lte=mois_fin)

        if mois:
            absences = absences.filter(date__month=int(mois))

        if semaine and annee:
            annee = int(annee)
            semaine = int(semaine)
            from datetime import datetime, timedelta
            premier_janvier = datetime(annee, 1, 1)
            jour_debut_semaine = premier_janvier + timedelta(days=(semaine - 1) * 7)
            jour_debut_semaine -= timedelta(days=jour_debut_semaine.weekday())
            jour_fin_semaine = jour_debut_semaine + timedelta(days=6)
            absences = absences.filter(date__range=[jour_debut_semaine, jour_fin_semaine])

        resultats = absences.values('matiere__nom').annotate(total_heures=Sum('nombre_heures')).order_by('matiere__nom')

        serializer = AbsenceParMatiereSerializer(resultats, many=True)
        return Response(serializer.data)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from swotify.models import Paiement, Eleve

from django.db.models import Sum, F, Q, Case, When, IntegerField, Value
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Subquery, OuterRef, IntegerField
from swotify.models import Paiement, Eleve  # Ajuste selon l'emplacement de tes modèles

class PaiementStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        annee = request.query_params.get('annee')  # ex: "2024-2025"
        classe_id = request.query_params.get('classe')  # optionnel

        # Filtrer les paiements selon l'année et la classe
        paiements = Paiement.objects.all()
        #if annee:
            #paiements = paiements.filter(annee_scolaire=annee)

        if classe_id:
            paiements = paiements.filter(eleve__classe_id=classe_id)

        # Somme totale reçue (globale)
        total_recu = paiements.aggregate(total=Sum('montant_verse'))['total'] or 0

        # Liste des élèves concernés
        eleves = Eleve.objects.select_related('classe').all()
        if classe_id:
            eleves = eleves.filter(classe_id=classe_id)

        # Sous-requête pour total des paiements par élève (corrigée)
        paiements_eleve_qs = Paiement.objects.filter(eleve=OuterRef('pk'))
        #if annee:
            #paiements_eleve_qs = paiements_eleve_qs.filter(annee_scolaire=annee)

        paiements_eleve_qs = paiements_eleve_qs.annotate(
            total=Sum('montant_verse')
        ).values('total')[:1]

        eleves = eleves.annotate(
            total_paye=Subquery(paiements_eleve_qs, output_field=IntegerField())
        )

        # Statistiques
        total_paye_global = 0
        complet = 0
        partiel = 0
        non_paye = 0
        total_attendu = 0

        for eleve in eleves:
            attendu = eleve.classe.frais_scolarite or 0
            total_attendu += attendu

            total_paye = eleve.total_paye or 0
            total_paye_global += total_paye

            if total_paye >= attendu:
                complet += 1
            elif total_paye > 0:
                partiel += 1
            else:
                non_paye += 1

        taux_recouvrement = round((total_paye_global / total_attendu) * 100, 2) if total_attendu > 0 else 0

        return Response({
            "annee_scolaire": annee or "toutes",
            "total_attendu": total_attendu,
            "total_recu": total_recu,
            "taux_recouvrement": taux_recouvrement,
            "eleves_total": eleves.count(),
            "paiements_complets": complet,
            "paiements_partiels": partiel,
            "paiements_non_payes": non_paye
        })



# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Max
from swotify.models import Paiement, Eleve, Classe

class PaiementsDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        annee = request.query_params.get('annee')
        classe_id = request.query_params.get('classe_id')
        statut_filter = request.query_params.get('statut')  # "Complet", "Partiel", "Non payé"

        eleves = Eleve.objects.select_related('classe').prefetch_related('paiements')
        if classe_id:
            eleves = eleves.filter(classe_id=classe_id)

        data = []

        for eleve in eleves:
            classe = eleve.classe
            if not classe or not hasattr(classe, 'frais_scolarite'):
                continue

            attendu = classe.frais_scolarite or 0
            paiements = eleve.paiements.all()
            if annee:
                paiements = paiements.filter(annee_scolaire=annee)

            total_paye = sum(p.montant_verse for p in paiements)
            dernier_paiement = paiements.order_by('-date_paiement').first()

            if total_paye >= attendu:
                statut = "Complet"
            elif total_paye > 0:
                statut = "Partiel"
            else:
                statut = "Non payé"

            if statut_filter and statut != statut_filter:
                continue

            data.append({
                "eleve_id": eleve.id,
                "nom": eleve.nom,
                "prenom": eleve.prenom,
                "classe": classe.nom,
                "statut": statut,
                "attendu": attendu,
                "total_paye": total_paye,
                "dernier_paiement": {
                    "date": dernier_paiement.date_paiement if dernier_paiement else None,
                    "moyen": dernier_paiement.moyen_paiement if dernier_paiement else None,
                    "commentaire": dernier_paiement.commentaire if dernier_paiement else None,
                }
            })

        return Response(data)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Avg
from swotify.models import Eleve

@api_view(['GET'])
def eleves_par_classe(request, classe_id):
    try:
        eleves = (
            Eleve.objects
            .filter(classe__id=classe_id)
            .annotate(moyenne=Avg('note__valeur'))
            .order_by('-moyenne')
        )

        resultats = [
            {
                'id': eleve.id,
                'nom': eleve.nom,
                'moyenne': round(eleve.moyenne or 0, 2),
            }
            for eleve in eleves
        ]

        return Response(resultats)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return Response({'message': 'Connexion réussie'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Nom d’utilisateur ou mot de passe invalide'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'message': 'Déconnexion réussie'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def test_auth_view(request):
    if request.user.is_authenticated:
        return Response({'authenticated': True, 'username': request.user.username})
    else:
        return Response({'authenticated': False}, status=status.HTTP_401_UNAUTHORIZED)

# views.py
class ClasseViewSet(viewsets.ModelViewSet):
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from swotify.models import Eleve, Comportement
from swotify.serializers import ComportementSerializer, EleveSerializer


@api_view(['GET'])
def comportements_par_eleve(request, eleve_id):
    try:
        eleve = Eleve.objects.get(id=eleve_id)
    except Eleve.DoesNotExist:
        return Response({"error": "Élève non trouvé"}, status=status.HTTP_404_NOT_FOUND)

    comportements = Comportement.objects.filter(eleve=eleve)
    serializer = ComportementSerializer(comportements, many=True)
    eleve_data = EleveSerializer(eleve).data

    return Response({
        "eleve": eleve_data,
        "comportements": serializer.data
    })

# swotify/views/message_views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from swotify.models import Message, CustomUser
from swotify.serializers import MessageSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def envoyer_message(request):
    expediteur = request.user
    contenu = request.data.get('contenu')
    destinataire_id = request.data.get('destinataire')

    if not contenu or not destinataire_id:
        return Response({"error": "Champs 'contenu' et 'destinataire' sont obligatoires."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        destinataire = CustomUser.objects.get(id=destinataire_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "Destinataire introuvable."}, status=status.HTTP_404_NOT_FOUND)

    message = Message.objects.create(
        expediteur=expediteur,
        destinataire=destinataire,
        contenu=contenu
    )

    serializer = MessageSerializer(message)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# swotify/views/dashboard_views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from swotify.models import CustomUser

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_utilisateurs(request):
    utilisateurs = CustomUser.objects.exclude(id=request.user.id)
    data = [
        {
            "id": utilisateur.id,
            "nom": utilisateur.last_name,
            "prenom": utilisateur.first_name,
            "role": utilisateur.role
        }
        for utilisateur in utilisateurs
    ]
    return Response(data, status=200)


from rest_framework import viewsets
from swotify.models import *
from swotify.serializers import *

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class EcoleViewSet(viewsets.ModelViewSet):
    queryset = Ecole.objects.all()
    serializer_class = EcoleSerializer

class ClasseViewSet(viewsets.ModelViewSet):
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer

class EleveViewSet(viewsets.ModelViewSet):
    queryset = Eleve.objects.all()
    serializer_class = EleveSerializer

class EnseignantViewSet(viewsets.ModelViewSet):
    queryset = Enseignant.objects.all()
    serializer_class = EnseignantSerializer

class MatiereViewSet(viewsets.ModelViewSet):
    queryset = Matiere.objects.all()
    serializer_class = MatiereSerializer

class EnseignantMatiereViewSet(viewsets.ModelViewSet):
    queryset = EnseignantMatiere.objects.all()
    serializer_class = EnseignantMatiereSerializer

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

class AbsenceViewSet(viewsets.ModelViewSet):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer

class ComportementViewSet(viewsets.ModelViewSet):
    queryset = Comportement.objects.all()
    serializer_class = ComportementSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

from rest_framework import viewsets, permissions
from swotify.models import Message
from swotify.serializers import MessageSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('date_envoi')
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(expediteur=self.request.user)
# dashboard_views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from swotify.models import Message
from django.utils.timezone import now

User = get_user_model()


class MessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retourne les 50 derniers messages où l'utilisateur est impliqué."""
        user = request.user

        messages = Message.objects.filter(
            expediteur=user
        ) | Message.objects.filter(destinataire=user)

        messages = messages.order_by('-date_envoi')[:50]

        data = []
        for msg in messages:
            data.append({
            'id': msg.id,
            'expediteur': {
                'id': msg.expediteur.id,
                'username': msg.expediteur.username,
                'first_name': msg.expediteur.first_name,
                'last_name': msg.expediteur.last_name,
                'photo_de_profil': getattr(msg.expediteur, 'photo_de_profil', None),
            },
            'destinataire': {
                'id': msg.destinataire.id,
                'username': msg.destinataire.username,
                'first_name': msg.destinataire.first_name,
                'last_name': msg.destinataire.last_name,
                'photo_de_profil': getattr(msg.destinataire, 'photo_de_profil', None),
            },
            'contenu': msg.contenu,
            'date_envoi': msg.date_envoi.isoformat()
        })


        return Response(data)

    def post(self, request):
        """Création d’un nouveau message."""
        user = request.user
        contenu = request.data.get('contenu')
        destinataire_id = request.data.get('destinataire_id')

        if not contenu or not destinataire_id:
            return Response({'error': 'Champs requis manquants'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            destinataire = User.objects.get(id=destinataire_id)
        except User.DoesNotExist:
            return Response({'error': 'Destinataire introuvable'}, status=status.HTTP_404_NOT_FOUND)

        message = Message.objects.create(
            expediteur=user,
            destinataire=destinataire,
            contenu=contenu,
            date_envoi=now()
        )

        return Response({
            'id': message.id,
            'expediteur': user.id,
            'destinataire': destinataire.id,
            'contenu': message.contenu,
            'date_envoi': message.date_envoi.isoformat()
        }, status=status.HTTP_201_CREATED)

class MessageDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, message_id):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return Response({'error': 'Message non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != message.destinataire:
            return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)

        message.lu = True
        message.save()

        return Response({'message': 'Message marqué comme lu'}, status=status.HTTP_200_OK)

class UserListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.exclude(id=request.user.id)
        data = []

        for user in users:
            data.append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'photo_de_profil': getattr(user, 'photo_de_profil', None),
            })

        return Response(data)
class ProfilAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'photo_de_profil': getattr(user, 'photo_de_profil', None),
        })
