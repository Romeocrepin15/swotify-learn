from django.core.management.base import BaseCommand
from swotify.models import (
    CustomUser, Ecole, Classe, Eleve, Enseignant, EnseignantMatiere,
    Matiere, Note, Absence, Comportement, Notification, Message
)

class Command(BaseCommand):
    help = "Vide toutes les données de la base sans supprimer les migrations"

    def handle(self, *args, **kwargs):
        models = [
            Note, Absence, Comportement, Notification, Message,
            Eleve, EnseignantMatiere, Enseignant,
            Classe, Matiere, Ecole,
            CustomUser,
        ]

        for model in models:
            model.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"✔ Données supprimées dans {model.__name__}"))

        self.stdout.write(self.style.SUCCESS("✅ Base de données vidée avec succès."))
