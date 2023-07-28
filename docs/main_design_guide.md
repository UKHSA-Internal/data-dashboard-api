# Winter Pressures API Rolling Design Guide

## Introduction

This guide will outline the current architecture of the winter-pressures API project.
The purpose of this document is to provide the reader with a view of the following:

- The design of the system and its dependencies.
- The project structure for the readers navigation purposes.

---

## System components

This system comprises the following:
- Private API for metrics associated with health threat incidence.
- Public API to provide view of data associated with health threat information.
- Content Management System (CMS) to provide the means of serving content to the dashboard.
- Relational database to store data associated with health threat insights & text-based content for the site.

---

## Project structure

This project is currently split with the metrics, CMS and public API distinct from each other.
This structure has been designed with modularity in mind. 
If in the future, a decision is made to move the CMS out and into its own codebase then that should be achievable.

The `metrics/` app takes a layered architectural approach:

```
|API|
|Interfaces|
|Domain|
|Data|
|Database|
```

Whereby each layer can only reach down (but not upwards).
This is enforced in this project with `import-linter`.

The codebase itself is *generally* structured as follows, this is not an exhaustive list:

```
|- cms/
    |- common/  # The wagtail app for the non-topic pages (about page).
    |- dashboard/ # This is the *main/primary* wagtail app.
    |- home/ # The wagtail app for the landing page.
    |- topic/ # The wagtal app for the topic pages (diseases e.g. COVID-19)
    |- dynamic_content/ # Contains the primary customised blocks and components used for dynamic content 
    |- metrics_interface/ # Contains the funnel abstractions which links the cms <- metrics parts of the application
   
|- feedback/ # Encapsulates the feedback module, email message construction and sending functionality
    |- serializers/ Primarily used to validate the correct question answer pairs are in inbound requests
    |- views/ # The view associated with the suggestions/ API
    |- email.py # The functionality for creating email objects and sending them
    |- email_template.py # Writing the body of the suggestions email

|- ingestion/
    |- api/ # views, serializers and viewsets associated with the ingestion API
    |- data_transfer_models/ # The DTOs used for parsing the source file and for translating into the data layer
    |- metrics_interface/ # Contains the funnel abstractions which links the ingestion <- metrics parts of the application
    |- consumer.py # Holds the object used to open source files, orchestrating the creation of DTOs, and calling to the reader 
    |- reader.py # The object used to parse the source file and perform any processing steps before the file can be consumed
    
|- metrics/
    |- api/ # This is the *main/primary* django app of the project. The centralised settings can be found within.
        settings.py # Settings for the main django app. The CMS apps are wired into place here.
        urls.py # URLs for the main django app. The CMS routes are wired into place here.
        urls_construction.py # Where the URLs are configured, grouped and toggled accordingly
        ... # views, serializers and viewsets associated with the API layer.
    |- data/ # Represents the data layer and access to the database.
        |- models/
            |- api_models.py # The flat denormalized model which holds everything in the single flat table.
            |- core_models.py # The normalized models which house a series of FK relationships.
        |- access/ # Read-like functionality for interacting with the db (via managers ideally).
        |- operations/ # Write-like functionality for interacting with the db (via managers ideally).
        |- managers/ # Contains files with custom queryset and model manager classes for the models.
        |- migrations/ # Contains the associated django migrations.
    |- domain/ # Represents the business logic layer. Currently houses the charts generation module.
    |- interfaces/ # Represents the interaction layer of the system. E.g. the API interacts with charts logic via the `interfaces/charts` module.
    |- templates/ # Contains .html templates for base pages which have been customized with the UKHSA branding.
    
|- public_api/ # This is the public facing unrestricted API, which provides programmatic access to the data.
    |- metrics_interface/ # Holds the class which bridges the public API -> metrics app
    |- serializers/ # All the serializers needed for the public API
    |- views/ # All the views needed for the public API
    |- urls.py # The constructed group of url patterns for the public API
    
|- tests/
    |- fakes/ # Contains fake implementations to remove additional dependencies for tests
    |- fixtures/ # The home for any fixtures/test data for the project.
    |- unit/ # The home for all unit tests across the project.
    |- integration/ # The home for all integration tests across the project.
    
|- manage.py # The main entrypoint into the app.
|- Dockerfile # The dockerfile for the app. The entrypoint is pointed to the manage.py file above.
```

>Note that the `metrics.api` is the primary django app to which everything is wired into.

---

## Separately deployable monolith

The various backend components touch the same parts of the database. 
As such, the codebase is at the time of writing (Jul 2023) is monolithic primarily because of:

a) The shared database models/other parts of code.
b) Ease of use/development speed for a small team.

There is simply the 1 single Docker image used for the backend application.

The `APP_MODE` environment variable is used to **switch the mode** in which the application is running.
There are a number of different options available for this setting:

- `"CMS_ADMIN"` - Used for deploying the CMS admin application only. This is the component used by the content creators.
- `"PRIVATE_API"` - Deployment of the private API, which will only be used by the front end application.
- `"PUBLIC_API"` - Deploying the hyperlinked browsable public API.

Note that the same image is used to deploy each of these services. 
The `APP_MODE` environment variable is used to toggle certain groups of endpoints off depending on the value being set.

For example, if a container is spun up with the `APP_MODE` environment variable set to "CMS_ADMIN", 
then the endpoints which belong to the private API and the public API will **not be available**.

> When no value is specified for the `APP_MODE` environment variable, then the application server will run with no restrictions.
i.e. all endpoints will be toggled on and available.

---

## Testing approach

### Framework
We have adopted `pytest` as the primary test runner for this project.

### Test folder structure

The `tests/` folder should mimic the source code structure as close as possible.
E.g. for a test which targets a function which sits in:
```
|- metrics/data/operations/api_models.py::generate_weekly_time_series
```
Then the corresponding unit test should reside in:
```
|- tests/unit/metrics/data/operations/test_api_models.py
```
