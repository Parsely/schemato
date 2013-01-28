BROKER_HOST = '127.0.0.1'
BROKER_PORT = 5672
BROKER_USER = "myuser"
BROKER_PASSWORD = "mypassword"
BROKER_VHOST = "myvhost"

CELERY_IMPORTS = ("schemato",)
CELERY_RESULT_BACKEND = "amqp"
CELERY_TASK_PUBLISH_RETRY = {
    "max_retries": 3,
    "interval_start": 1,
    "interval_step": 0.2,
    "interval_max": 2
}

CELERYD_HIJACK_ROOT_LOGGER = False
CELERYD_LOG_LEVEL = 'DEBUG'
