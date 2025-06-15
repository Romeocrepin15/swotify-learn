# ton_app/serializers/message_serializer.py
from rest_framework import serializers
from swotify.models import Message
from .utilisateur_serializer import UtilisateurSerializer

class MessageSerializer(serializers.ModelSerializer):
    expediteur = UtilisateurSerializer(read_only=True)
    destinataire = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'contenu', 'expediteur', 'destinataire', 'date_envoi']
