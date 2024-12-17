import gunicorn

workers = 3
threads = 3
worker_class = "gthread"
timeout = 120
