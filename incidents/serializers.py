from rest_framework import serializers

from .models import Incident, Categorie, Commentaire


class CategorieSerializer(serializers.ModelSerializer):

    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description']


class IncidentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Incident
        fields = [
            'id',
            'titre',
            'description',
            'priorite',
            'statut',
            'categorie',
            'demandeur',
            'technicien',
            'date_creation',
            'date_resolution',
            'solution',
        ]

        read_only_fields = [
            'demandeur',
            'date_creation',
            'date_resolution',
        ]


class CommentaireSerializer(serializers.ModelSerializer):

    class Meta:
        model = Commentaire
        fields = [
            'id',
            'incident',
            'auteur',
            'contenu',
            'date_creation',
        ]

        read_only_fields = [
            'auteur',
            'date_creation',
        ]