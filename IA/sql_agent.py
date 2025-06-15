# sql_agent.py
import os
from dotenv import load_dotenv
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI

# Charger les variables d'environnement (.env)
load_dotenv()

# 🔑 Clé API (à mettre dans ton .env)
# OPENAI_API_KEY=sk-...

# 🔗 Connexion à ta base SQLite
db = SQLDatabase.from_uri("sqlite:///db.sqlite3")

# 🤖 Modèle OpenAI (tu peux remplacer par un modèle local plus tard si tu veux)
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")  # Nécessite connexion internet

# 🧠 Création de l'agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)

# Exemple d'utilisation
if __name__ == "__main__":
    question = "Quels sont les 3 élèves les plus performants ?"
    reponse = agent_executor.run(question)
    print(reponse)
