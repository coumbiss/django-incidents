from django.conf import settings
from django.db import models


class Priority(models.TextChoices):
    BASSE = 'basse', 'Basse'
    NORMALE = 'normale', 'Normale'
    HAUTE = 'haute', 'Haute'
    CRITIQUE = 'critique', 'Critique'


class Status(models.TextChoices):
    OUVERT = 'ouvert', 'Ouvert'
    EN_COURS = 'en_cours', 'En cours'
    RESOLU = 'resolu', 'Resolu'
    FERME = 'ferme', 'Ferme'


class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom


class Incident(models.Model):
    titre = models.CharField(max_length=200)

    description = models.TextField()

    priorite = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMALE
    )

    statut = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OUVERT
    )

    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.PROTECT,
        related_name='incidents'
    )

    demandeur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='incidents_demandes'
    )

    technicien = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidents_assignes'
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    date_resolution = models.DateTimeField(
        null=True,
        blank=True
    )

    solution = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.titre
class Commentaire(models.Model):
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='commentaires'
    )

    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='commentaires'
    )

    contenu = models.TextField()

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire de {self.auteur} sur {self.incident}"