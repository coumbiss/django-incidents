from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import IncidentViewSet, CategorieViewSet, health_check


router = DefaultRouter()

router.register(
    r'incidents',
    IncidentViewSet,
    basename='incident'
)

router.register(
    r'categories',
    CategorieViewSet,
    basename='categorie'
)


urlpatterns = [
    path('health/', health_check, name='health-check'),
]

urlpatterns += router.urls