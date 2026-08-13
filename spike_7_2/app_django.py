import sys
import os
from django.conf import settings
from django.urls import path
from django.http import JsonResponse
from django.core.management import execute_from_command_line

if not settings.CONFIGURED:
    settings.configure(
        DEBUG=False,
        SECRET_KEY="spike-logitrack-secret-key",
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=["*"],
    )

def health(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path("health", health),
]

if __name__ == "__main__":
    execute_from_command_line(sys.argv)
