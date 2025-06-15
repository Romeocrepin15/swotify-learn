from django.apps import AppConfig
from django.db.backends.signals import connection_created
from django.dispatch import receiver


class SwotifyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "swotify"

    # Active les clés étrangères pour SQLite lors de la connexion
    @receiver(connection_created)
    def activate_foreign_keys(sender, connection, **kwargs):
        if connection.vendor == 'sqlite':
            cursor = connection.cursor()
            cursor.execute('PRAGMA foreign_keys = ON;')
