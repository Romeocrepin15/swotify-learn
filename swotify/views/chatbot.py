import os
import openai
from dotenv import load_dotenv

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

# LangChain (SQL agent)
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

import os
import openai
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Initialiser la clé OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")



# Initialisation de la base SQLite
base_dir = os.path.dirname(__file__)
db_path = os.path.abspath(os.path.join(base_dir, '..', '..', 'db.sqlite3'))
db_uri = f"sqlite:///{db_path}"

db = SQLDatabase.from_uri(db_uri)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)


# ✅ Endpoint 1 : Chat général via OpenAI
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

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )

        return Response({"response": response.choices[0].message.content})

    except openai.error.OpenAIError as e:
        return Response({"error": f"Erreur OpenAI : {str(e)}"}, status=500)

    except Exception as e:
        return Response({"error": f"Erreur serveur : {str(e)}"}, status=500)


# ✅ Endpoint 2 : Chat SQL intelligent via LangChain
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
