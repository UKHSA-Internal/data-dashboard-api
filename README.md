# UKHSA data dashboard API

This is a [Django](https://www.djangoproject.com/) 
and [Wagtail](https://docs.wagtail.org/en/stable/getting_started/index.html) project. 
The REST API is served via [Django-Rest-Framework](https://www.django-rest-framework.org/)

## Prerequisites

Before proceeding with the initial configuration you will require `postgresql` to be installed
on your development system. For Mac users this will require `homebrew`.

For a guide on setting up home brew please find details on the following link https://brew.sh/

Once homebrew has been setup you can run the following command to install `postgressql`

```bash
brew install postgresql
```

## Standard command tooling

To unify commonly used commands, there is a `Makefile` at the root level of the project.
Note that to use the `Makefile` you will need 

## Initial configuration

There are a number of steps to take before getting the environment setup for local development.

1. Ensure that you have [Python version 3.11](https://www.python.org/downloads/) installed on your system.

2. Set the `APIENV` environment variable set to `LOCAL`. 
```bash
export APIENV=LOCAL
```
To do this, you should include this line in an `.env` file at the root level of the project.
This will ensure that the Django `DEBUG` setting is set to True and the app will use a local sqlite database.


3. Ensure you have set a value for the `SECRET_KEY` environment variable.
```bash
export SECRET_KEY=REPLACE_ME_WITH_ACTUAL_VALUE
```
Once again, you should include this line in the `.env` file at the root level of your project structure.

See the [Django documentation | SECRET_KEY](https://docs.djangoproject.com/en/4.2/ref/settings/#secret-key) for more information.

4. Set up the virtual environment and install the project dependencies via:
```bash
make setup-venv
```

Note that this step requires a Python 3.11 version to be installed on your system.

5. Apply the database migrations, ensure Django collects static files and run the server.
```bash
make run-server
```
This will run the server locally on port 8000 - http://localhost:8000/

6. Create a local superuser by activating the virtual environment and following the prompts:
```bash
source venv/bin/activate
./manage.py createsuperuser
```

7. Sign in to the admin panel at `/admin/` and add an API key. 
**Make sure you note it down** as it won't be displayed in full again. 
You will need this key to be able to use the API later.
If you did not note of the generated key, you can simply create another and use that instead.

---

## Database

When developing locally, the app will point to a local database:

```
...
|- README.md
|- db.sqlite3  # <- this is the database
```

---

## Application data

To seed your environment with data, including CMS content and a snapshot of metrics data, 
you can run the following commands:

```bash
sudo chmod +x boot.sh # <- make the script executable

sudo ./boot.sh <API Key> <Admin Password>
```

Whereby, `API Key` should meet the following criteria:

- Random first 8 alphanumeric characters
- `.` character on the 9th character
- Another random 32 alphanumeric characters

```
APIKey = <8 alphanumeric characters>.<32 alphanumeric characters>
```

---

## Development flows

### Project dependencies

The project dependencies are seperated into usage:
```
requirements.txt        # <- This imports the prod + dev dependencies. This includes all dependencies, regardless of usage.
requirements-prod.txt   # <- These are the Production-only dependencies. This is ingested by the Dockerfile
requirements-dev.txt    # <- These are the Dev dependencies-only. Includes testing/factory libraries
```

If you followed the instructions above in [Initial configuration](#initial-configuration) 
and ran `make setup-venv` then you will have installed the complete set of dependencies, 
including those needed for local development.

---

### Checking for code vulnerabilities

You can check for known vulnerabilities in the codebase with the following command:
```bash
make audit
```

---

### Running tests

The tests are split by type, `unit` and `integration`.

You can run them separately via the `Makefile` or all at once:

```bash
make all-tests
```

### Code quality checks

You can run the standard formatting tooling over your code with the following command:

```bash
make formatting
```

Note that if you push code to the remote repository which does not conform to the styling enforced by this tooling, 
that CI build will fail.

In this case you will need to run `make formatting` and push the code changes to the remote repository.

> In the future, this will be automated.

### Architectural constraints check

We use the `import-linter` package to enforce architectural constraints across the codebase.
You can check these by running the following command:

```bash
make architecture
```

Also note that this will also be enforced by virtue of the CI. 

---

## Remote infrastructure

When developing locally, you should have the `APIENV` environment variable set to `LOCAL`.
However, if you wish to connect to remote infrastructure, then you can do so by configuring 
the following environment variables:

- `APIENV` - The name of the environment. Must not be `LOCAL` for remote development.
- `POSTGRES_DB` - The name of the database
- `POSTGRES_USER` - The name of the user on the database
- `POSTGRES_PASSWORD` - The password associated with the database
- `POSTGRES_HOST` - The hostname of the database
- `POSTGRES_PORT` - (Optional) The port to connect to on the database, defaults to 5432

Note that with the environment variable `APIENV` set to anything other than `LOCAL`, 
the underlying Django `DEBUG` setting will be set to False.

In turn this will mean you have to run the following management command 
for the app to collect the necessary static files:

```
python manage.py collectstatic
```

Alternatively, if you are using the `make run-server` command to start your server, 
then this will be handled for you and you will not need to manually run `python manage.py collectstatic`.

---

## Using the API

### Via Curl

With the server running, you can make requests as follows:

```bash
curl -X 'GET' 'http://localhost:8000/api/pages/' -H 'accept: */*' -H 'Authorization: <Add API Key here>'
```
Make sure you replace the placeholder with the API key generated from the `initial configuration` steps.

### Via Swagger

Alternatively, you can use the swagger docs at `http://localhost:8000/api/swagger/`.
To pass the API key to all requests made by swagger you will need to do the following:
1. Click on the `Authorize` button
2. Enter your generated secret API key in the `api_key` authorization field.
3. You are now free to use the API via the swagger docs!

---

## Detailed documentation

For more detailed technical documentation please refer to the `docs/` folder at the 
root level of the project. 

Here you can find design information on the project structure, architecture and the current data model.
As well as more detailed standards and practices which must be adopted when developing in this codebase.
