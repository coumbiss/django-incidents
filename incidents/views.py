from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Incident, Categorie, Status
from .serializers import IncidentSerializer, CategorieSerializer
from .permissions import IncidentPermission
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def health_check(request):
    return Response(
        {
            "status": "ok"
        },
        status=status.HTTP_200_OK
    )


class IncidentViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated, IncidentPermission]

    def get_queryset(self):
        user = self.request.user

        # Responsable : voit tous les incidents
        if user.role == 'RESPONSABLE':
            queryset = Incident.objects.all()

        # Technicien : voit les incidents non affectés
        # ou ceux qui lui sont affectés
        elif user.role == 'TECHNICIEN':
            queryset = (
                Incident.objects.filter(technicien=user)
                | Incident.objects.filter(technicien__isnull=True)
            )

        # Demandeur : voit uniquement ses incidents
        else:
            queryset = Incident.objects.filter(demandeur=user)

        # Filtre par statut
        statut = self.request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)

        # Filtre par priorité
        priorite = self.request.query_params.get('priorite')
        if priorite:
            queryset = queryset.filter(priorite=priorite)

        # Filtre par catégorie
        categorie = self.request.query_params.get('categorie')
        if categorie:
            queryset = queryset.filter(categorie=categorie)

        return queryset.distinct()

    def perform_create(self, serializer):
        # L'utilisateur connecté devient automatiquement
        # le demandeur de l'incident
        serializer.save(demandeur=self.request.user)

    # Bloquer la modification complète d'un incident fermé
    def update(self, request, *args, **kwargs):
        incident = self.get_object()

        if incident.statut == Status.FERME:
            return Response(
                {
                    "detail": "Un incident fermé ne peut plus être modifié."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().update(request, *args, **kwargs)

    # Bloquer la modification partielle d'un incident fermé
    def partial_update(self, request, *args, **kwargs):
        incident = self.get_object()

        if incident.statut == Status.FERME:
            return Response(
                {
                    "detail": "Un incident fermé ne peut plus être modifié."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().partial_update(request, *args, **kwargs)

    # Action : prendre en charge un incident
    @action(
        detail=True,
        methods=['post'],
        url_path='prendre-en-charge'
    )
    def prendre_en_charge(self, request, pk=None):
        incident = self.get_object()
        user = request.user

        # Seul un technicien peut prendre en charge
        if user.role != 'TECHNICIEN':
            return Response(
                {
                    "detail": "Seul un technicien peut prendre en charge un incident."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Un incident fermé ne peut pas être modifié
        if incident.statut == Status.FERME:
            return Response(
                {
                    "detail": "Un incident fermé ne peut plus être modifié."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Un incident déjà affecté ne peut pas être
        # pris en charge par un autre technicien
        if incident.technicien is not None:
            return Response(
                {
                    "detail": (
                        "Cet incident est déjà pris en charge "
                        "par un technicien."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Affecter l'incident au technicien connecté
        incident.technicien = user
        incident.statut = Status.EN_COURS
        incident.save()

        serializer = self.get_serializer(incident)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # Action : résoudre un incident
    @action(
        detail=True,
        methods=['post'],
        url_path='resoudre'
    )
    def resoudre(self, request, pk=None):
        incident = self.get_object()
        user = request.user

        # Seul un technicien peut résoudre
        if user.role != 'TECHNICIEN':
            return Response(
                {
                    "detail": "Seul un technicien peut résoudre un incident."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Seul le technicien affecté peut résoudre
        if incident.technicien != user:
            return Response(
                {
                    "detail": (
                        "Vous n'êtes pas le technicien affecté "
                        "à cet incident."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Un incident fermé ne peut pas être modifié
        if incident.statut == Status.FERME:
            return Response(
                {
                    "detail": "Un incident fermé ne peut plus être modifié."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Récupérer la solution
        solution = request.data.get('solution', '').strip()

        # La solution est obligatoire
        if not solution:
            return Response(
                {
                    "solution": (
                        "Une solution est obligatoire "
                        "pour résoudre un incident."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Résoudre l'incident
        incident.solution = solution
        incident.statut = Status.RESOLU
        incident.date_resolution = timezone.now()
        incident.save()

        serializer = self.get_serializer(incident)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # Action : fermer un incident
    @action(
        detail=True,
        methods=['post'],
        url_path='fermer'
    )
    def fermer(self, request, pk=None):
        incident = self.get_object()
        user = request.user

        # L'incident doit être résolu avant d'être fermé
        if incident.statut != Status.RESOLU:
            return Response(
                {
                    "detail": "Seul un incident résolu peut être fermé."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Seul le demandeur concerné ou le responsable
        # peut fermer l'incident
        if user.role == 'RESPONSABLE' or incident.demandeur == user:

            incident.statut = Status.FERME
            incident.save()

            serializer = self.get_serializer(incident)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "detail": (
                    "Seul le demandeur concerné ou un responsable "
                    "peut fermer cet incident."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )


class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [IsAuthenticated]