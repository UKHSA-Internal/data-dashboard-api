import gunicorn

workers = 3
threads = 3
worker_class = "gthread"
timeout = 120

gunicorn.SERVER = "undisclosed"
gunicorn.SERVER_SOFTWARE = "0.0.0"
