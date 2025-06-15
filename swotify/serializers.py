from rest_framework import serializers
from .models import (
    Ecole, Classe, Eleve, Note, CustomUser, Message,
    Enseignant, Matiere, EnseignantMatiere, Absence,
    Comportement, Notification, Paiement
)

# ======== CustomUser Serializer ========
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'photo_de_profil', 'role', 'date_joined', 'nationalite'
        ]


# ======== Enseignant Serializer ========
class EnseignantSerializer(serializers.ModelSerializer):
    nom = serializers.CharField(source='user.last_name')
    prenom = serializers.CharField(source='user.first_name')

    class Meta:
        model = Enseignant
        fields = ['id', 'nom', 'prenom']


# ======== Matiere Serializer ========
class MatiereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matiere
        fields = ['id', 'nom', 'description']


# ======== EnseignantMatiere Serializer ========
class EnseignantMatiereSerializer(serializers.ModelSerializer):
    enseignant = EnseignantSerializer()
    matiere = MatiereSerializer()

    class Meta:
        model = EnseignantMatiere
        fields = ['enseignant', 'matiere']


# ======== Ecole Serializer ========
class EcoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ecole
        fields = '__all__'


# ======== Classe Serializer (avec enseignants_matieres et effectif) ========
class ClasseSerializer(serializers.ModelSerializer):
    enseignants_matieres = serializers.SerializerMethodField()
    effectif = serializers.SerializerMethodField()

    class Meta:
        model = Classe
        fields = ['id', 'nom', 'niveau', 'frais_scolarite', 'ecole', 'enseignants_matieres', 'effectif']

    def get_enseignants_matieres(self, obj):
        relations = EnseignantMatiere.objects.filter(classe=obj)
        return EnseignantMatiereSerializer(relations, many=True).data

    def get_effectif(self, obj):
        return obj.eleves.count()


# ======== Eleve Serializer (version enrichie) ========
class EleveSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    classe_nom = serializers.CharField(source='classe.nom', read_only=True)

    class Meta:
        model = Eleve
        fields = [
            'id', 'user', 'classe_nom', 'nationalite', 'date_inscription',
            'photo_profile'
        ]


# ======== Note Serializer (avec nom/prénom élève, matière, classe) ========
class NoteSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.utilisateur.last_name', read_only=True)
    eleve_prenom = serializers.CharField(source='eleve.utilisateur.first_name', read_only=True)
    matiere_nom = serializers.CharField(source='matiere.nom', read_only=True)
    classe_id = serializers.IntegerField(source='eleve.classe.id', read_only=True)
    classe_nom = serializers.CharField(source='eleve.classe.nom', read_only=True)

    class Meta:
        model = Note
        fields = [
            'id', 'eleve', 'eleve_nom', 'eleve_prenom',
            'matiere', 'matiere_nom', 'valeur', 'type_note',
            'trimestre', 'date_note', 'classe_id', 'classe_nom'
        ]


# ======== Absence Par Matière Serializer (statistique) ========
class AbsenceParMatiereSerializer(serializers.Serializer):
    matiere__nom = serializers.CharField()
    total_heures = serializers.FloatField()


# ======== Absence Standard Serializer ========
class AbsenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Absence
        fields = '__all__'


# ======== Comportement Serializer ========
class ComportementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comportement
        fields = ['id', 'observation', 'positif', 'date']


# ======== Message Serializer ========
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Message

User = get_user_model()

class MessageSerializer(serializers.ModelSerializer):
    expediteur = serializers.StringRelatedField(read_only=True)  # afficher nom expéditeur (read only)
    destinataire_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),  # ✅ Correction ici
        source='destinataire',
        write_only=True
    )
    destinataire = serializers.StringRelatedField(read_only=True)  # affichage lisible

    class Meta:
        model = Message
        fields = ['id', 'expediteur', 'destinataire', 'destinataire_id', 'contenu', 'date_envoi']

# ======== Notification Serializer ========
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


# ======== Paiement Serializer ========
class PaiementDetailSerializer(serializers.ModelSerializer):
    nom_eleve = serializers.CharField(source='eleve.nom', read_only=True)
    prenom_eleve = serializers.CharField(source='eleve.prenom', read_only=True)
    classe = serializers.CharField(source='eleve.classe.nom', read_only=True)

    class Meta:
        model = Paiement
        fields = [
            'id', 'nom_eleve', 'prenom_eleve', 'classe',
            'montant_verse', 'date_paiement', 'moyen_paiement',
            'commentaire', 'annee_scolaire'
        ]
