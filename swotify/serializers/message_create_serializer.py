# ton_app/serializers/message_create_serializer.py
from rest_framework import serializers
from swotify.models import Message

class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['contenu', 'destinataire']

    def create(self, validated_data):
        expediteur = self.context['request'].user
        return Message.objects.create(expediteur=expediteur, **validated_data)
