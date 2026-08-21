from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.http import JsonResponse


def health(request):
    return JsonResponse({
        "status": "ok"
    })
def health_check(request):
    return JsonResponse({
        "status": "ok"
    })

urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'api/v1/',
        include('incidents.urls')
    ),

    path(
        'api-auth/',
        include('rest_framework.urls')
    ),

    path(
        'health/',
        health,
        name='health'
    ),

]