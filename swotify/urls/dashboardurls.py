# swotify/urls/dashboardurls.py
from django.urls import path
from swotify.views.dashboard_views import (
    stats_dashboard,
    moyennes_par_classe,
    top_classes,
    alertes_critiques,
    messages_recents,
    repartition_effectifs_par_classe,
    repartition_effectifs_par_ecole,
)

urlpatterns = [
    path('stats/', stats_dashboard, name='stats_dashboard'),
    path('moyennes/', moyennes_par_classe, name='moyennes_par_classe'),
    path('top_classes/', top_classes, name='top_classes'),
    path('alertes/', alertes_critiques, name='alertes_critiques'),
    path('messages-recents/', messages_recents, name='messages_recents'),
    path('repartition-par-classe/', repartition_effectifs_par_classe, name='repartition_par_classe'),
    path('repartition-par-ecole/', repartition_effectifs_par_ecole, name='repartition_par_ecole'),
]
