bind = "0.0.0.0:8000"
workers = 2
loglevel = "info"
accesslog = "/var/log/gunicorn_access"
access_log_format = "%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"
errorlog = "/var/log/gunicorn_error"

secure_scheme_headers = {"X-FORWARDED-PROTOCOL": "ssl", "X-FORWARDED-PROTO": "https", "X-FORWARDED-SSL": "on"}
