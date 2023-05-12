# Winter Pressures API

This is a [Django](https://www.djangoproject.com/) 
and [Wagtail](https://docs.wagtail.org/en/stable/getting_started/index.html) project. 
The REST API is served via [Django-Rest-Framework](https://www.django-rest-framework.org/)


## Standard command tooling

To unify commonly used commands, there is a `Makefile` at the root level of the project.
Note that to use the `Makefile` you will need 

## Initial configuration 

There are a number of steps to take before getting the environment setup locally.

1. Ensure you have the `APIENV` environment variable set to `"LOCAL"`. 
```bash
export APIENV=LOCAL
```
To do this, you should include this line in an `.env` file at the root level of the project.

2. Set up the virtual environment and install the project dependencies via:
```bash
make setup-venv
```

3. Apply the database migrations and run the server.
```bash
make run-server
```
This will run the server locally on port 8000 - http://localhost:8000/

4. Create a local superuser by activating the virtual environment and following the prompts:
```bash
source venv/bin/activate
./manage.py createsuperuser
```

5. Sign in to the admin panel at `/admin/` and add an API key. 
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

## Development flows


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

### Architectural constraints check

We use the `import-linter` package to enforce architectural constraints across the codebase.
You can check these by running the following command:
```bash
make architecture
```

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
