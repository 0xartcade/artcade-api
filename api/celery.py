import logging
from datetime import timedelta

import environ
import structlog
from celery import Celery
from celery.contrib.django.task import DjangoTask
from celery.signals import setup_logging
from django_structlog.celery.steps import DjangoStructLogInitStep
from kombu import Queue

log = logging.getLogger(__name__)


class Task(DjangoTask):
    """
    Global task defaults.
    https://docs.celeryq.dev/en/stable/userguide/tasks.html
    """

    # Since retry_backoff makes first retry always start 1 second after,
    # we set a high max_retry default and up the retry delay to 30 seconds.
    # this gives external services a chance to recover before we give up.
    max_retries = 7
    default_retry_delay = 30
    retry_backoff = True
    retry_backoff_max = 180
    retry_jitter = True

    # Set some sensible time limits in case tasks get stuck
    task_soft_time_limit = 120
    task_time_limit = 150


class Priority:
    """
    Celery priority queues. Needs to match Procfile worker config.
    p0 is the highest priority
    p1 is regular
    p2 is low
    """

    p0 = Queue("p0", routing_key="p0")
    p1 = Queue("p1", routing_key="p1")
    p2 = Queue("p2", routing_key="p2")


# Load Environment Variables
env = environ.Env()
environ.Env.read_env(".env")

# Celery app
app = Celery("api", task_cls=Task)
app.config_from_object("django.conf:settings", namespace="CELERY")

# A step to initialize django-structlog
app.steps["worker"].add(DjangoStructLogInitStep)

# https://docs.celeryq.dev/en/stable/userguide/configuration.html
app.conf.update(
    #
    # Broker settings
    #
    broker_pool_limit=100,
    redis_max_connections=20,
    #
    # Setup priority queues, sorted with order from worker command
    #
    task_default_queue=Priority.p1.name,
    task_queues=[Priority.p0, Priority.p1, Priority.p2],
    broker_transport_options={"queue_order_strategy": "sorted"},
    broker_connection_retry_on_startup=True,
    #
    # Result backend config
    #
    result_extended=True,
    result_expires=timedelta(days=3).total_seconds(),
    # Share connection pool instead of creating a new connection for every thread
    result_backend_thread_safe=True,
)

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@setup_logging.connect
def receiver_setup_logging(
    loglevel, logfile, format, colorize, **kwargs
):  # pragma: no cover
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json_formatter": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(),
                },
                "plain_console": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.dev.ConsoleRenderer(),
                },
                "key_value": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.KeyValueRenderer(
                        key_order=["timestamp", "level", "event", "logger"]
                    ),
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "plain_console",
                },
                "json_file": {
                    "class": "logging.handlers.WatchedFileHandler",
                    "filename": "logs/json.log",
                    "formatter": "json_formatter",
                },
                "flat_line_file": {
                    "class": "logging.handlers.WatchedFileHandler",
                    "filename": "logs/flat_line.log",
                    "formatter": "key_value",
                },
            },
            "loggers": {
                "django_structlog": {
                    "handlers": ["console", "flat_line_file", "json_file"],
                    "level": "INFO",
                },
                "django_structlog_demo_project": {
                    "handlers": ["console", "flat_line_file", "json_file"],
                    "level": "INFO",
                },
            },
        }
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


@app.task(bind=True, queue=Priority.p0)
def debug_task(self):
    log.info(f"debug_task: {self.request!r}")


#
# Crontab/Periodic tasks
# https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html
#


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    pass
