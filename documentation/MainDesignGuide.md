# Winter Pressures API Rolling Design Guide

## Introduction

This guide will outline the current architecture of the winter-pressures API project.
The purpose of this document is to provide the reader with a view of the following:

- The design of the system and its dependencies.
- The project structure for the readers navigation purposes.

---

## System components

This system comprises the following:
- API to expose set of private and public-facing endpoints for metrics associated with disease incidence.
- Content Management System (CMS) to serve content from on-technical users.
- Relational database to store data associated with disease insights & text-based content for the site.

---

## Project structure

This project is currently split with the metrics and CMS distinct from each other.
This structure has been designed with modularity in mind. 
If in the future, a decision is made to move the CMS out and into its own codebase then that should be achievable.

The `metrics/` app takes a layered architectural approach:

```
|API / interfaces|
|Domain|
|Data|
|Database|
```

Whereby each layer can only reach down (but not upwards).
In the future, this could be enforced with `import-linter`.

```
|- cms/
   |- common/  # The wagtail app for the non-topic pages (about page).
   |- dashboard/ # This is the *main/primary* wagtail app.
   |- home/ # The wagtail app for the landing page.
   |- topic/ # The wagtal app for the topic pages (diseases e.g. COVID-19)
   ...

|- metrics/
    |- api/ # This is the *main/primary* django app of the project. The centralised settings can be found within.
        settings.py # Settings for the main django app. The CMS apps are wired into place here.
        urls.py # URLs for the main django app. The CMS routes are wired into place here.
        ... # views, serializers and viewsets associated with the API layer.
    |- data/ # Represents the database layer.
        |- models/
            |- api_models.py # The flat model which holds everything in the single flat table.
            |- core_models.py # The normalized models which house a series of FK relationships.
        |- access/ # Read-like functionality for interacting with the db (via managers ideally).
        |- operations/ # Write-like functionality for interacting with the db (via managers ideally).
        |- managers/ # Contains files with custom queryset and model manager classes for the models.
        |- migrations/ # Contains the associated django migrations.
    |- domain/ # Represents the business logic layer. Currently houses the charts generation module.
    |- interfaces/ # Represents the boundary of the system. Currently holds only management commands. `api/` arguably should be here.
    
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
