# Winter Pressures API

When running `docker-compose` for local development the server port is set to 5100 while in 'prod' it's still 8000

## Winter Pressures DB

---

### Manual Testing Locally

#### Use Docker to run Postgres and create a fresh instance:

* `docker pull postgres`
* `docker run --name winter-pressures-db -e POSTGRES_PASSWORD=mysecretpassword -d postgres`

#### Then enable the virtual environment before running the start script and checking the output.

* `virtualenv venv` (or similar)
* `source venv/bin/activate`
* `pip install -r requirements.txt`
* `cd wpdb`
* `source start.sh`

#### Running Unit Tests

---
