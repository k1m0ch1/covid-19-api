import os
port = os.environ.get('PORT', 5000)
bind = f"0.0.0.0:{port}"

# Copied from gunicorn.glogging.CONFIG_DEFAULTS
logconfig_dict = {
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "gunicorn.error": {
            "propagate": True,
        },
        "gunicorn.access": {
            "propagate": True,
        },
        "app.app": {
            "propagate": False,
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stdout"
        },
    },
    "formatters": {
        "generic": {
            "format": "[%(name)s] [%(process)s] [%(levelname)s] %(message)s",
            "class": "logging.Formatter"
        }
    }
}
