from django.contrib import admin
from .models import CustomUser, Ecole, Classe, Eleve, Enseignant, Matiere, EnseignantMatiere, Note, Absence, Comportement, Notification, Message, Paiement

@admin.register(Ecole)
class EcoleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ville', 'directeur')  # Le champ 'ville' existe désormais dans le modèle
    search_fields = ('nom', 'directeur__username')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "directeur":
            kwargs["queryset"] = CustomUser.objects.filter(role="admin")  # 🔥 Filtre les admins
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Enregistrement des autres modèles
admin.site.register(CustomUser)
admin.site.register(Classe)
admin.site.register(Eleve)
admin.site.register(Enseignant)
admin.site.register(Matiere)
admin.site.register(EnseignantMatiere)
admin.site.register(Note)
admin.site.register(Absence)
admin.site.register(Comportement)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(Paiement)
