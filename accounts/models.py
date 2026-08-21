from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        DEMANDEUR = 'DEMANDEUR', 'Demandeur'
        TECHNICIEN = 'TECHNICIEN', 'Technicien'
        RESPONSABLE = 'RESPONSABLE', 'Responsable'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.DEMANDEUR
    )

    def __str__(self):
        return self.username