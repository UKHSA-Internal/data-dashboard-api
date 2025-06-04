import gunicorn

workers = 3
threads = 3
worker_class = "gthread"
timeout = 120
max_requests = 300

gunicorn.SERVER = "undisclosed"
gunicorn.SERVER_SOFTWARE = "0.0.0"
