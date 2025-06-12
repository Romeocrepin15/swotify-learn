from django.core.management.base import BaseCommand
from swotify.models import Ecole, CustomUser

class Command(BaseCommand):
    help = "Ajoute un directeur à une école existante"

    def handle(self, *args, **kwargs):
        try:
            admin_user = CustomUser.objects.get(username="admin")
            ecole = Ecole.objects.get(nom="VJS")
            ecole.directeur = admin_user
            ecole.save()
            self.stdout.write(self.style.SUCCESS(f"✔ Directeur ajouté à l'école : {ecole.nom}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erreur : {e}"))
