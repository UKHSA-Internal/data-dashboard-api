# Environment Variables Guide

## Introduction

This document lists and describes all the available environment variables across the application.

---

### Application configuration

#### `APIENV`

This configures the application to run under a set of assumptions.

##### `APIENV=LOCAL`

If this is set to `LOCAL`, then a local sqlite database will be used 
and the underlying `DEBUG` setting will be set to True.

##### `APIENV=STANDALONE`

If this is set to `STANDALONE`, then a local sqlite database will be used 
but the underlying `DEBUG` setting will be set to False.

If this is set to any other value, then the application will try and connect to a postgres database.
The postgres database connections settings in will be used for this connection.

#### `APP_MODE`

This is the switch used to configure the workload. 
The codebase itself is a monolith, but we can separately deploy the same
image and spin a container up from that image to serve different functions. 
This means that we can develop within the same codebase, 
share functionality where needed across modules and maintain the 1 CI/CD pipeline whilst also being able to deploy
the same image as separate services.
The `APP_MODE` environment variable allows us to bring about this behaviour.

##### `APP_MODE=CMS_ADMIN`

- Only the wagtail CMS application endpoints will be exposed
- The application will be found at the base URL. For example, `localhost:8000` will take you to the CMS login page.

##### `APP_MODE=PRIVATE_API`

- Only the endpoints associated with the private API will be exposed. 
This primarily consists of endpoints which are used to create charts, tables and headline numbers.
- The private API will be found at the base URL. 
For example, `localhost:8000/api/swagger` will take you to the swagger docs of the private API.
- A redis cache is expected to be running and reachable.

##### `APP_MODE=PUBLIC_API`

- Only the endpoints associated with the public API will be exposed. 
This primarily consists of the hyperlinked-browsable API which is connected to the main dashboard frontend.
For example, `localhost:8000/api/swagger` will take you to the swagger docs of the public API.
- Whereas, `localhost:8000/api/public/timeseries` will take you to the root of the browsable API.

##### `APP_MODE=FEEDBACK_API`

- Only the endpoints associated with the feedback API will be exposed. 
This primarily consists of the feedback API which is connected to the main dashboard frontend.
For example, `localhost:8000/api/swagger` will take you to the swagger docs of the feedback API.
- Note that the feedback API relies on email configuration being set up correctly.

##### `APP_MODE=INGESTION`

- Only the endpoints associated with ingestion will be exposed. 
This primarily consists of the ingestion service which is configured to ingest messages and populate the
database with the latest metrics data

##### APP_MODE default

If the `APP_MODE` environment variable is set to any value other than the ones listed above.
Then the application will be configured to run in a monolithic-type setting.
In other words, all endpoints will be exposed on the single running instance of the application.
Note that in this scenario, the URLs will be arranged as follows:

- `{base_url}/cms-admin`: The CMS admin application will be served here
- `{base_url}/api/public/timeseries`: The hyperlinked-browsable public API will be served here
- `{base_url}/api/swagger`: The swagger docs for all the endpoints will be served here
- `{base_url}/api/redoc`: The redoc docs for all the endpoints will be served here

---

### Database configuration

#### `POSTGRES_DB`

This should be set to the name of the postgresql database.

#### `POSTGRES_USER`

This should be set to the name of the user on the postgresql database.

#### `POSTGRES_PASSWORD`

This should be set to the password used for the user on the postgresql database.

**Note that when running in `INGESTION` mode, this is fetched from AWS SecretsManager directly.**

#### `POSTGRES_HOST`

This should be set to endpoint host name of the postgresql database.

#### `POSTGRES_PORT`

The port number of the postgresql database. Typically, this is set to 5432.

---

### Django configuration

#### `SECRET_KEY`

This is the secret key used by Django to provide cryptographically signing.
See the [django docs](https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-SECRET_KEY) for more information.

---

### Email configuration

#### `EMAIL_BACKEND`

This represents the backend which is to be used to send emails.
Defaults to `"smtp.EmailBackend"`.

#### `EMAIL_USE_TLS`

Whether to use a TLS (secure) connection when talking to the SMTP server. 
Defaults to `True`.

#### `EMAIL_HOST`

The host to use for sending emails. Defaults to `"smtp.gmail.com"`

#### `EMAIL_PORT`

The port to use for the SMTP server. Defaults to `587`.

#### `EMAIL_HOST_USER`

The email address to send emails from.

#### `EMAIL_HOST_PASSWORD`

The password to use to authenticate the `EMAIL_HOST_USER` with the SMTP server.

#### `FEEDBACK_EMAIL_RECIPIENT_ADDRESS`

The email address to send feedback suggestions emails to.

---

### Caching configuration

#### `REDIS_HOST`

The endpoint of the redis instance which is used to cache the private API.
Defaults to `"redis://127.0.0.1:6379"` if not specified.

---

### Crawler configuration

#### `CDN_AUTH_KEY`

This is the key by the crawler to authenticate against the target load balancer.

#### `FRONTEND_URL`

This is the URL of the deployed frontend application which is being crawled.

#### `PUBLIC_API_URL`

This is the URL of the deployed public API application which is being crawled.

#### `ENABLE_AREA_SELECTOR`

This increases the scope of the private API crawler to include crawling for all geography/topic page combinations.

---

### Ingestion configuration

#### `INGESTION_BUCKET_NAME`

This is the name of the s3 bucket from which to ingest metrics files from.

#### `AWS_PROFILE_NAME`

The name of the AWS profile to use for the AWS client used for ingestion.


#### `SECRETS_MANAGER_DB_CREDENTIALS_ARN`

The ARN of the database credentials secret in AWS SecretsManager.

When running in `INGESTION` mode, the `POSTGRES_PASSWORD` is 
fetched from SecretsManager directly when the application is initialized.
