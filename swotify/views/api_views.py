# api_views.py
from rest_framework import viewsets
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from swotify.models import (
    Ecole,
    Classe,
    Eleve,
    Note,
    Enseignant,
    Matiere,
    EnseignantMatiere,
)
from swotify.serializers import (
    EcoleSerializer,
    ClasseSerializer,
    EleveSerializer,
    NoteSerializer,
    EnseignantSerializer,
    MatiereSerializer,
    EnseignantMatiereSerializer,
)

class EcoleViewSet(viewsets.ModelViewSet):
    queryset = Ecole.objects.all()
    serializer_class = EcoleSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ['nom', 'ville']
    ordering_fields = ['nom', 'ville']

class ClasseViewSet(viewsets.ModelViewSet):
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ['nom', 'niveau']
    ordering_fields = ['nom', 'niveau']

class EleveViewSet(viewsets.ModelViewSet):
    queryset = Eleve.objects.all()
    serializer_class = EleveSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ['classe', 'sexe']
    ordering_fields = ['user__username']

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ['eleve', 'matiere']
    ordering_fields = ['eleve', 'matiere']

class EnseignantViewSet(viewsets.ModelViewSet):
    queryset = Enseignant.objects.all()
    serializer_class = EnseignantSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ['nom', 'specialite']
    ordering_fields = ['nom']

class MatiereViewSet(viewsets.ModelViewSet):
    queryset = Matiere.objects.all()
    serializer_class = MatiereSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ['nom']
    ordering_fields = ['nom']

class EnseignantMatiereViewSet(viewsets.ModelViewSet):
    queryset = EnseignantMatiere.objects.all()
    serializer_class = EnseignantMatiereSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ['enseignant', 'matiere']
    ordering_fields = ['enseignant', 'matiere']
