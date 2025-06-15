# ton_app/serializers/utilisateur_serializer.py
from rest_framework import serializers
from swotify.models import CustomUser  # adapte le chemin si besoin

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'nom', 'prenom', 'photo_de_profil']
