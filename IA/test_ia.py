import os
import sys

# Ajouter le dossier racine du projet au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Initialiser Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "swotify_learn.settings")

import django
django.setup()

# Ensuite ton import fonctionne
from ia_chat import repondre, repondre_avec_bd


question = repondre_avec_bd("What is the overall academic performance of the student?", eleve_id=15)
reponse = repondre(question)

print("Réponse :", reponse)
