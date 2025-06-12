from rest_framework import generics, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q

from ..models import Message
from ..serializers import (
    UtilisateurSerializer,
    MessageSerializer,
    MessageCreateSerializer
)

User = get_user_model()


# 🔹 1. Liste des utilisateurs (hors soi-même)
class ListeUtilisateursAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)


# 🔹 2. Liste des messages récents (envoyés ou reçus par l'utilisateur)
class MessagesRecentsAPIView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(expediteur=user) | Q(destinataire=user)
        ).order_by('date_envoi')


# 🔹 3. Envoi d'un nouveau message
class EnvoyerMessageAPIView(generics.CreateAPIView):
    serializer_class = MessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(expediteur=self.request.user)

# views.py
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os

os.environ["OPENAI_API_KEY"] = "TA_CLE_API"

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# Connexion à ta base de données Django (SQLite dans ce cas)
db = SQLDatabase.from_uri("sqlite:../../db.sqlite3")

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)

@api_view(['POST'])
def chatbot_view(request):
    question = request.data.get("question")
    if not question:
        return Response({"error": "Aucune question fournie"}, status=400)

    try:
        result = agent_executor.run(question)
        return Response({"response": result})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
