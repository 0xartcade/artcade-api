import logging

from celery.result import AsyncResult
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db import DatabaseError
from django.db.transaction import non_atomic_requests
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response

from api.celery import app as celery_app
from api.celery import debug_task

logger = logging.getLogger(__name__)
process_started_at = now()


@extend_schema(exclude=True)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
@non_atomic_requests
def index(request):
    """
    Noop.
    """
    return Response(data="Hello World.")


@non_atomic_requests
def robots(request):
    """
    Disallow bots
    """
    return HttpResponse(
        "User-agent: * \nDisallow: /",
        content_type="text/plain",
    )


@api_view(["GET", "HEAD"])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
def health(request):
    """
    General app health check
    """

    healthy = True
    db_status = {}
    celery_broker_connected = False

    # Check db connections
    for name in settings.DATABASES.keys():
        try:
            # Trigger a simple query.
            User.objects.using(name).exists()
        except DatabaseError:
            db_status[name] = "error"
            healthy = False
            logger.exception(f"Error when connecting to db: {name}")
        else:
            db_status[name] = "ok"

    # Ping celery workers
    try:
        celery_app.broker_connection().ensure_connection(timeout=3)
        celery_broker_connected = True
    except Exception:
        healthy = False
        logger.exception("Health check failed - celery connection failed")

    return Response(
        {
            "status": "ok" if healthy else "error",
            "db": db_status,
            "broker_connected": celery_broker_connected,
            "version": settings.GIT_COMMIT,
            "started_at": process_started_at,
        },
        status=200 if healthy else 500,
    )


@api_view(["GET", "HEAD"])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
def health_celery(request):
    """
    Returns ok if task was queued and completed.
    """
    task: AsyncResult = debug_task.delay()
    task.get()

    return Response({"status": "ok"})


@authentication_classes([])
@permission_classes([permissions.AllowAny])
@non_atomic_requests
def favicon(request):
    return redirect(staticfiles_storage.url("favicon.ico"))
