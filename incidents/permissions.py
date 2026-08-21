from rest_framework.permissions import BasePermission, SAFE_METHODS


class IncidentPermission(BasePermission):

    def has_object_permission(self, request, view, obj):

        user = request.user

        # Responsable : accès à tous les incidents
        if user.role == 'RESPONSABLE':
            return True

        # Demandeur : accès uniquement à ses propres incidents
        if user.role == 'DEMANDEUR':
            return obj.demandeur == user

        # Technicien :
        # accès aux incidents non affectés
        # ou aux incidents qui lui sont affectés
        if user.role == 'TECHNICIEN':
            return (
                obj.technicien is None
                or obj.technicien == user
            )

        return False