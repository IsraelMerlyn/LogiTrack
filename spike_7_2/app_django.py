import sys
import os
from django.conf import settings

if not settings.CONFIGURED:
    settings.configure(
        DEBUG=False,
        SECRET_KEY="spike-logitrack-secret-key",
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=["*"],
        APPEND_SLASH=False,
        MIDDLEWARE=[
            "django.middleware.common.CommonMiddleware",
        ],
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
    )

import django
django.setup()

from django.urls import path
from django.http import JsonResponse
from django.core.wsgi import get_wsgi_application
from wsgiref.simple_server import make_server

def health(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path("health", health),
]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    application = get_wsgi_application()
    httpd = make_server("127.0.0.1", port, application)
    httpd.serve_forever()