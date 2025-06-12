from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# Modèle pour l'utilisateur personnalisé
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    date_naissance = models.DateField(null=True, blank=True)
    nationalite = models.CharField(max_length=100, null=True, blank=True)
    photo_de_profil = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)  # 🔥 Ajout ici

    def __str__(self):
        return self.username



# Modèle Ecole
class Ecole(models.Model):
    nom = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255, null=True, blank=True)
    directeur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'admin'},
        related_name='ecoles_dirigees'
    )
    ville = models.CharField(max_length=255, null=True, blank=True)  
    def __str__(self):
        return self.nom


# Modèle Classe
class Classe(models.Model):

    NIVEAU_CHOICES = [
        ('T', 'Terminale'),
        ('P', 'Première'),
        ('S', 'Seconde'),
        ('6', 'Sixième'),
        ('5', 'Cinquième'),
        ('4', 'Quatrième'),
        ('3', 'Troisième'),
        ('0', 'Autre'),  # Pour d'autres niveaux non spécifiés
    ]
    niveau = models.CharField(
        max_length=1,
        choices=NIVEAU_CHOICES,
        default='S',
        verbose_name="Niveau"
    )
    capacite = models.IntegerField(default=50)
    nom = models.CharField(max_length=255)
    ecole = models.ForeignKey(
        Ecole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes'
    )
    frais_scolarite = models.DecimalField(max_digits=10, decimal_places=2, default=100000)
    def __str__(self):
        return self.nom


# Modèle Eleve
#from .models import Classe  # Assurez-vous que Classe est bien importé

class Eleve(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'student'}
    )
    classe = models.ForeignKey('Classe', on_delete=models.CASCADE, related_name="eleves")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=10)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)
    telephone_parent = models.CharField(max_length=20)
    date_inscription = models.DateField(auto_now_add=True)
    nationalite = models.CharField(max_length=100)
    photo_profile = models.ImageField(upload_to='photos/%Y/%m/%d/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"


# Modèle Enseignant


class Enseignant(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'}
    )
    is_active = models.BooleanField(default=True)
    specialite = models.CharField(max_length=255, null=True, blank=True)
    date_recrutement = models.DateField(null=True, blank=True)
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE, null=True, blank=True)

    # Champs supplémentaires avec valeurs par défaut
    nom = models.CharField(max_length=255, default="Nom générique", blank=True)
    prenom = models.CharField(max_length=255, default="Prénom générique", blank=True)
    grade = models.CharField(max_length=255, default="Professeur", blank=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.grade})"



# Modèle Matiere
class Matiere(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nom


# Modèle EnseignantMatiere (relie un enseignant à une matière)

# Modèle EnseignantMatiere
class EnseignantMatiere(models.Model):
    enseignant = models.ForeignKey(
        Enseignant,
        on_delete=models.CASCADE,
        related_name='enseignant_matieres'
    )
    matiere = models.ForeignKey(
        Matiere,
        on_delete=models.CASCADE,
        related_name='matieres_enseignes',
        default=1  # Remplacez 1 par l'ID d'une matière existante que vous souhaitez comme défaut
    )
    classe = models.ForeignKey(
        Classe,
        on_delete=models.CASCADE,
        null=True,
        default=1  # Remplacez 1 par l'ID d'une classe existante que vous souhaitez comme défaut
    )

    def __str__(self):
        return f"{self.enseignant} enseigne {self.matiere} à {self.classe}"


# Modèle Note (pour gérer les notes des élèves par matière)

class Note(models.Model):
    # Choix pour le trimestre
    TRIMESTRE_CHOICES = [
        (1, 'Premier trimestre'),
        (2, 'Deuxième trimestre'),
        (3, 'Troisième trimestre'),
    ]
    
    # Choix pour le type de note
    TYPE_NOTE_CHOICES = [
        ('controle', 'Contrôle'),
        ('examens', 'Examens'),
    ]
    
    eleve = models.ForeignKey('Eleve', on_delete=models.CASCADE)
    matiere = models.ForeignKey('Matiere', on_delete=models.CASCADE)
    valeur = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Trimestre avec choix et valeur par défaut (Premier trimestre)
    trimestre = models.IntegerField(choices=TRIMESTRE_CHOICES, default=1)
    
    # Type de note avec choix et valeur par défaut (Contrôle)
    type_note = models.CharField(max_length=20, choices=TYPE_NOTE_CHOICES, default='controle')
    
    date_note = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.eleve} - {self.matiere} - {self.valeur} ({self.get_trimestre_display()})"






#from .models import Enseignant

# Modèle Absence
class Absence(models.Model):
    eleve = models.ForeignKey(
        Eleve,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="absences"
    )
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    classe = models.ForeignKey(
        'Classe', 
        on_delete=models.CASCADE, 
        null=False,  # S'assurer que la classe ne peut pas être nulle
        blank=False,  # Empêche l'absence de classe
         related_name='absences'

    ) 
 
    matiere = models.ForeignKey(
        'Matiere', 
        on_delete=models.CASCADE
    )  # Lien vers la matière
    
    # Champs d'absence
    date = models.DateField()
    justification = models.TextField(blank=True, null=True)
    type_seance = models.CharField(max_length=20)  # Par exemple : 'cours', 'examen'
    nombre_heures = models.IntegerField()

    def __str__(self):
        return f"Absence de {self.eleve} le {self.date} en {self.matiere} (Classe: {self.classe})"

# Modèle Comportement
class Comportement(models.Model):
    eleve = models.ForeignKey(
        Eleve,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comportements'
    )
    positif = models.BooleanField(default=False)
    observation = models.TextField()

    def __str__(self):
        return f"{self.eleve.user.first_name} - {self.observation[:20]}..."

#from django.db import models
#from django.utils import timezone

# Modèle Notification
class Notification(models.Model):
    # L'élève à qui la notification est destinée
    eleve = models.ForeignKey(
        Eleve,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    # Message de la notification
    message = models.TextField()
    
    # Date de création de la notification (automatique)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    # Statut de la notification : "lue" ou "non lue"
    lu = models.BooleanField(default=False)
    
    # Priorité de la notification (par exemple, Haute, Moyenne, Basse)
    PRIORITE_CHOICES = [
        ('haute', 'Haute'),
        ('moyenne', 'Moyenne'),
        ('basse', 'Basse'),
    ]
    priorite = models.CharField(max_length=10, choices=PRIORITE_CHOICES, default='moyenne')

    # Champ pour indiquer si la notification est une alerte ou une simple information
    type_notification = models.CharField(
        max_length=15, 
        choices=[('alerte', 'Alerte'), ('information', 'Information')],
        default='information'
    )

    def __str__(self):
        return f"{self.eleve.user.first_name} - {self.date_creation} - {self.get_priorite_display()} - {self.get_type_notification_display()}"

    def marquer_comme_lue(self):
        """Méthode pour marquer la notification comme lue"""
        self.lu = True
        self.save()

from django.db import models
from django.conf import settings

class Message(models.Model):
    expediteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Utiliser la config AUTH_USER_MODEL pour plus de flexibilité
        on_delete=models.CASCADE,
        related_name='messages_envoyes',
        # default=1,  # Évite un default arbitraire, mieux vaut forcer l’expéditeur dans la vue
    )
    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages_recus',
        # default=2,  # pareil, mieux vaut pas de valeur par défaut ici
    )
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_envoi']  # trier par date d'envoi, plus logique pour une messagerie

    def __str__(self):
        return f"{self.expediteur.first_name} → {self.destinataire.first_name} ({self.date_envoi.strftime('%Y-%m-%d %H:%M')})"


# Modèle Message
from django.conf import settings
from django.db import models
from .models import CustomUser  # ou User selon ce que tu utilises
from django.contrib.auth import get_user_model
"""
class Message(models.Model):
    expediteur = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='messages_envoyes',
         default=1
        
    )

    destinataire = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='messages_recus',
         default=2
    )
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.expediteur.first_name} → {self.destinataire.first_name} ({self.date_envoi})"
"""



class Paiement(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name='paiements')
    montant_verse = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateField(auto_now_add=True)
    moyen_paiement = models.CharField(max_length=50, blank=True, null=True)  # Espèces, mobile money...
    commentaire = models.TextField(null=True, blank=True)
    annee_scolaire = models.CharField(max_length=20) 

    def __str__(self):
        return f"{self.eleve} - {self.montant_verse} FCFA le {self.date_paiement}"

