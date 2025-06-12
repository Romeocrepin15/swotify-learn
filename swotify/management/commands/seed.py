from django.core.management.base import BaseCommand
from swotify.models import (
    CustomUser, Ecole, Classe, Eleve, Enseignant, EnseignantMatiere,
    Note, Absence, Comportement, Notification, Message, Matiere
)
import random
from faker import Faker
from django.db import transaction

fake = Faker("fr_FR")

class Command(BaseCommand):
    help = "Peuple la base de données avec des données de test"

    def handle(self, *args, **kwargs):
        try:
            # Utiliser une transaction pour garantir la cohérence des données
            with transaction.atomic():
                # --- Vérification ou Création de l'Admin ---
                admin_user, created = CustomUser.objects.get_or_create(
                    username="admin",
                    defaults={
                        "password": "admin123",
                        "role": "admin",
                        "is_staff": True,
                        "email": "admin@ecole.com",
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"✔ Admin créé : {admin_user.email}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠ Admin existe déjà : {admin_user.email}"))

                # Vérifie que l'Admin existe avant de continuer
                if not admin_user:
                    self.stdout.write(self.style.ERROR("❌ Admin introuvable ou invalide. Script arrêté."))
                    return

                # --- Création de l'École avec gestion du directeur ---
                ecole, created = Ecole.objects.get_or_create(
                    nom="VJS",
                    defaults={
                        "adresse": "123 Avenue de l'Indépendance (Dolisie)",
                        "ville": "Dolisie",
                        "directeur": admin_user,  # Assignation directe du directeur
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"✔ École créée : {ecole.nom}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠ École existe déjà : {ecole.nom}"))

                # --- Création des Matières ---
                noms_matieres = [
                    "Maths", "Français", "Histoire", "Physique", "SVT", "Anglais",
                    "Espagnol", "Informatique", "Philosophie", "Arts et Culture", "Education Physique"
                ]
                matieres = []
                for nom in noms_matieres:
                    matiere, created = Matiere.objects.get_or_create(nom=nom)
                    matieres.append(matiere)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"✔ Matière créée : {nom}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"⚠ Matière existe déjà : {nom}"))

                # --- Création des Enseignants ---
                enseignants = []
                for i in range(10):
                    user, created = CustomUser.objects.get_or_create(
                        username=f"enseignant_{i}",
                        defaults={
                            "password": "test123",
                            "role": "teacher",
                            "email": f"enseignant{i}@ecole.com",
                        }
                    )
                    if created:
                        enseignant = Enseignant.objects.create(
                            user=user,
                            ecole=ecole
                        )
                        enseignants.append(enseignant)
                        self.stdout.write(self.style.SUCCESS(f"✔ Enseignant créé : {user.email}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"⚠ Enseignant existe déjà : {user.email}"))

                # --- Création des Classes et Élèves ---
                eleves = []
                for i in range(1, 3):  # 2 niveaux
                    noms_classes = [f"TC{i}", f"TD{i}", f"TA{i}"]
                    for nom_classe in noms_classes:
                        classe, created = Classe.objects.get_or_create(
                            nom=nom_classe,
                            defaults={
                                "ecole": ecole,
                                "niveau": random.choice(["T", "P", "S"]),  # T pour Terminale, P pour Première, S pour Seconde
                            }
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f"✔ Classe créée : {classe.nom}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"⚠ Classe existe déjà : {classe.nom}"))

                        # Associer enseignants aux classes et matières (un seul enseignant par matière par classe)
                        for matiere in matieres:
                            enseignant = random.choice(enseignants)
                            EnseignantMatiere.objects.get_or_create(
                                enseignant=enseignant,
                                matiere=matiere,
                                classe=classe
                            )

                        # Créer des élèves
                        for j in range(1, 10):  # 9 élèves par classe
                            user, created = CustomUser.objects.get_or_create(
                                username=f"eleve_{nom_classe}_{j}",
                                defaults={
                                    "password": "test123",
                                    "role": "student",
                                    "email": f"eleve{j}@ecole.com",
                                }
                            )
                            if created:
                                sexe = random.choice(["M", "F"])
                                nom = fake.last_name_male() if sexe == "M" else fake.last_name_female()
                                prenom = fake.first_name_male() if sexe == "M" else fake.first_name_female()

                                eleve = Eleve.objects.create(
                                    user=user,
                                    classe=classe,
                                    nom=nom,
                                    prenom=prenom,
                                    sexe=sexe,
                                    date_naissance=fake.date_of_birth(minimum_age=10, maximum_age=18),
                                    lieu_naissance=fake.city(),
                                    adresse=fake.address(),
                                    telephone_parent=fake.phone_number()
                                )
                                eleves.append(eleve)
                                self.stdout.write(self.style.SUCCESS(f"✔ Élève créé : {prenom} {nom}"))
                            else:
                                self.stdout.write(self.style.WARNING(f"⚠ Élève existe déjà : {user.email}"))

                # --- Ajout de Notes ---
                for eleve in eleves:
                    for matiere in matieres:
                        note = Note.objects.create(
                            eleve=eleve,
                            matiere=matiere,
                            trimestre=1,
                            type_note='controle',
                            valeur=random.uniform(0, 20)
                        )
                        
                        self.stdout.write(self.style.SUCCESS(f"✔ Note ajoutée : {note.eleve} - {note.valeur}"))

                # --- Ajout d'Absences ---
                for eleve in eleves:
                    # Récupérer un enseignant aléatoire à partir de l'utilisateur
                    enseignant_user = random.choice(enseignants).user
                    enseignant = Enseignant.objects.get(user=enseignant_user)  # Utilisation correcte de l'enseignant
                    
                    # Associer la classe de l'élève à l'absence
                    classe = eleve.classe  # On prend la classe de l'élève pour l'absence
                    
                    # Choisir une matière aléatoire pour l'absence
                    matiere = random.choice(matieres)
                    
                    absence = Absence.objects.create(
                        eleve=eleve,
                        classe=classe,  # Associer la classe ici
                        matiere=matiere,  # Associer une matière ici
                        date=fake.date_this_year(),
                        justification=fake.sentence(nb_words=10),
                        type_seance=random.choice(['cours', 'tp', 'evaluation']),
                        enseignant=enseignant,  # L'enseignant récupéré est maintenant associé
                        nombre_heures=random.randint(1, 4)
                    )
                    self.stdout.write(self.style.SUCCESS(f"✔ Absence ajoutée pour {eleve.nom} : {absence.date} - Matière : {matiere.nom}"))

                # --- Ajout de Notifications ---
                for eleve in eleves:
                    notification = Notification.objects.create(
                        eleve=eleve,
                        message=fake.sentence(nb_words=12),
                        date_creation=fake.date_time_this_year(),
                        lu=random.choice([True, False]),
                        priorite=random.choice(['haute', 'moyenne', 'basse']),
                        type_notification=random.choice(['alerte', 'information'])
                    )
                    self.stdout.write(self.style.SUCCESS(f"✔ Notification ajoutée pour {eleve.nom}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Une erreur inattendue s'est produite : {e}"))
