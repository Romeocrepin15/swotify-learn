import os
from dotenv import load_dotenv

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

# OpenAI v1 (nouveau client)
from openai import OpenAI

# LangChain (SQL agent)
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

# 🔄 Charger les variables d'environnement
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🔗 Nouveau client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# 🗃️ Connexion à la base de données SQLite
base_dir = os.path.dirname(__file__)
db_path = os.path.abspath(os.path.join(base_dir, '..', '..', 'db.sqlite3'))
db_uri = f"sqlite:///{db_path}"
db = SQLDatabase.from_uri(db_uri)

# 🤖 LLM utilisé pour LangChain
llm = ChatOpenAI(
    model="gpt-3.5-turbo",  # ou gpt-4 si disponible
    temperature=0,
    openai_api_key=OPENAI_API_KEY
)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)

# ✅ Endpoint 1 : Chat général
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot_view(request):
    try:
        question = request.data.get("question")

        if not question:
            return Response({"error": "Question manquante."}, status=400)

        messages = [
            {"role": "system", "content": "Tu es un assistant scolaire pour la plateforme SWOTify Learn. Réponds de manière claire, concise et adaptée à un élève ou enseignant."},
            {"role": "user", "content": question}
        ]

        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # ou "gpt-3.5-turbo"
            messages=messages,
            temperature=0.7
        )

        return Response({"response": chat_completion.choices[0].message.content})

    except Exception as e:
        return Response({"error": f"Erreur serveur : {str(e)}"}, status=500)

# ✅ Endpoint 2 : Agent LangChain SQL
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot_sql_view(request):
    try:
        question = request.data.get("question")

        if not question:
            return Response({"error": "Question manquante."}, status=400)

        response = agent_executor.run(question)
        return Response({"response": response})

    except Exception as e:
        return Response({"error": f"Erreur serveur : {str(e)}"}, status=500)
