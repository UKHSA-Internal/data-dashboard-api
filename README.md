# UKHSA data dashboard API

This is a [Django](https://www.djangoproject.com/) 
and [Wagtail](https://docs.wagtail.org/en/stable/getting_started/index.html) project. 
The REST API is served via [Django-Rest-Framework](https://www.django-rest-framework.org/)

## Prerequisites

Before proceeding with the initial configuration you will require `postgresql` to be installed
on your development system. For Mac users this will require `homebrew`.

For a guide on setting up home brew please find details on the following link https://brew.sh/

Once homebrew has been set up you can run the following command to install `postgressql`

```bash
brew install postgresql
```

## Standard command tooling

To unify commonly used commands for local development, there is a script at the root level of the project.
Source our CLI tool:

```bash
source uhd.sh
```

The CLI provides a set of high level modules, which you can see by running the following command:

```bash
uhd
```

These are grouped by category. 
You can then select the category by determining which commands are available.
For example, if we run the following command:

```bash
uhd bootstrap
```

We will see a list of commands available for bootstrapping and populating the database.

This CLI tool provides common workflows for local development. 
This will help you for things such as but not limited to:

- Running the test suite
- Starting the application server
- Populating the database with test data

The Continuous Integration (CI) pipeline also uses the same CLI tool for the various CI builds.
This includes running the test suite and performing static analysis over the codebase.

## Initial configuration

There are a number of steps to take before getting the environment setup for local development.

1. At the time of writing you will need to ensure that 
you have [Python version 3.12.6](https://www.python.org/downloads/) installed on your system.
If in doubt, please check the `.python-version` file at the root level of the project. 
This is the Python version used by the CLI tooling and the CI pipeline.

2. Set the `APIENV` environment variable set to `LOCAL`. 
```bash
export APIENV=LOCAL
```
To do this, you should include this line in an `.env` file at the root level of the project.
This will ensure that the Django `DEBUG` setting is set to True.
The application will also point to a local [SQLite](https://www.sqlite.org/index.html) database.

3. Ensure you have set a value for the `SECRET_KEY` environment variable.
```bash
export SECRET_KEY=REPLACE_ME_WITH_ACTUAL_VALUE
```
Once again, you should include this line in the `.env` file at the root level of your project structure.

See the [Django documentation | SECRET_KEY](https://docs.djangoproject.com/en/4.2/ref/settings/#secret-key) for more information.

4. Set up the virtual environment and install the project dependencies via:
```bash
uhd venv create
```
This command will create a virtual environment at the `.venv/` folder at the root level of the project.
The version of Python which will be used is dictated by the aforementioned `.python-version` file.
And finally, the entire project dependencies will be installed within the virtual environment.

5. Apply the database migrations and ensure Django collects all required static files.
```bash
uhd server setup-all
```

6. Run a development server:
```bash
uhd server run-local
```

This will run the server locally on port 8000 - http://localhost:8000/

Note that you can also override the port by passing a port number into the command:

```bash
uhd server run-local 1234
```

---

## Database

When developing locally, the app will point to a local SQLite database:

```
|- venv/
...
|- README.md
|- db.sqlite3  # <- this is the database
```

---

## Application data

To seed your environment with data, including CMS content, a snapshot of metrics data and an admin user,
you can run the following command:

```bash
uhd bootstrap all <Admin Password>
```

Alternatively you can populate those items individually.
As mentioned previously, you can determine which commands are available 
by entering the high level `bootstrap` module in the CLI:

```bash
uhd bootstrap
```

For example, the following command will create the admin user:

```bash
uhd bootstrap admin-user <Admin Password>
```

And the following command will populate the database with the base template CMS pages:

```bash
uhd bootstrap test-content
```

And finally, the following command will populate the database with the truncated test dataset:

```bash
uhd bootstrap test-data
```

## Logging into the CMS admin application

Once your database has been populated, with the `uhd bootstrap all` or `uhd bootstrap admin-user` commands, 
you will be able to log in.
Head to http://localhost:8000/cms-admin/ and use the following credentials:

- Username: **testadmin**
- Password: `<Admin Password>`

Where the `<Admin Password>` is the password you provided to the call made 
to the `uhd bootstrap all` or `uhd bootstrap admin-user` script.

---

## Development flows

### Project dependencies

The project dependencies are seperated into usage:
```
requirements.txt                  # <- This imports the prod + dev dependencies. This includes all dependencies, regardless of usage.
requirements-prod.txt             # <- These are the Production-only dependencies. This is ingested by the main Dockerfile
requirements-prod-ingestion.txt   # <- These are the Production dependencies for the ingestion image only.
requirements-dev.txt              # <- These are the Dev dependencies-only. Includes testing/factory libraries
```

If you followed the instructions above in the [Initial configuration](#initial-configuration) section
and ran `uhd server create` then you will have installed the complete set of dependencies, 
including those needed for local development.

---

### Running tests

The tests are split by type, `unit`, `integration`, `system` and `migrations`.
To see which commands are available for the `tests` module, you should run:

```bash
uhd tests
```

You can run these groups of tests all at once:

```bash
uhd tests all
```

Or you can run them separately. For example, to run the unit tests:

```bash
uhd tests unit
```

We also enforce 100% test coverage across the codebase.
You can calculate the test coverage with the following command:

```bash
uhd tests coverage
```

Please note that test coverage provides a minimum baseline only.
It is simply a measure of the lines of source code which have been executed throughout the test suite.
Just because you have 100% test coverage does **not** indicate your development branch or feature is fully/well tested.

---

### Code quality checks

You can run the standard formatting tooling over your code with the following command:

```bash
uhd quality format
```

---

Note that if you push code to the remote repository which does not conform to the styling enforced by this tooling, 
that CI build will fail.

In this case you will need to run `uhd quality format` and push the code changes to the remote repository.

> In the future, this will be automated.

---

### Checking for code vulnerabilities

You can check for known vulnerabilities in the codebase with the following command:
```bash
uhd security vulnerabilities
```
---

### Pre-commit Hooks

This repository uses **pre-commit** to automatically scan for hardcoded secrets before allowing commits.

#### Setup (one-time)

1. Install Python (if not already installed)

2. Install pre-commit:

```bash
pip install pre-commit
```
---

### Architectural constraints check

We use the `import-linter` package to enforce architectural constraints across the codebase.
You can check these by running the following command:

```bash
uhd security architecture
```

Also note that this is also be enforced by virtue of the CI.

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

In turn this will mean you have to run the following command 
for the app to collect the necessary static files:

```
uhd server setup-static-files
```

---

## Using the API

### Via Curl

With the server running, you can make requests as follows:

```bash
curl -X 'GET' 'http://localhost:8000/api/pages/'
```

### Via Swagger

Alternatively, you can use the swagger docs at `http://localhost:8000/api/swagger/`.

### Via Redoc

Or redoc at `http://localhost:8000/api/redoc/`

---

## Detailed documentation

For more detailed technical documentation please refer to the `docs/` folder at the 
root level of the project. 

Here you can find design information on the project structure, architecture and the current data model.
As well as more detailed standards and practices which must be adopted when developing in this codebase.
