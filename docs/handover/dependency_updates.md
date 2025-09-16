# Dependency Updates

## Defined dependencies

Our dependencies are split into 3 groups:

- `requirements-dev.txt`             <- Development dependencies only (think linting and testing tools)
- `requirements-prod.txt`            <- Dependencies which are required to run the application
- `requirements-prod-ingestion.txt`  <- Dependencies required for the data ingestion lambda function

The dependencies within `requirements-dev.txt` are **not** bundled into the main docker image.
And therefore these dependencies are **not** available in production.

## Dependabot

At the time of writing (Sep 2025), dependabot is in use for automatically raising PRs 
with new 3rd party library updates.

Dependabot is defined at `.github/dependabot.yml`.
Dependabot will search for new updates to 3rd party libraries and raise PRs in the morning.
These must be reviewed and approved by an engineer.

Dependabot does not (and definitely should not) have the ability approve and merge PRs itself.

Dependabot will pick up major, minor and patch version updates.
The only exception being `boto3` and `botocore` which we restricted to major version updates only
as the dependency updates from those packages are automated daily and somewhat noisy. 

## Key dependencies to note

Most dependency updates can generally flow through to the main branch.
However, in the past we have seen the following dependencies introduce breaking changes for minor / patch releases:

- `Django`
- `djangorestframework`
- `drf-nested-routers`
- `kaleido`
- `plotly`
- `wagtail`

## Security patches

Dependabot will automatically raise PRs against identified security vulnerabilities.
The `dependency-checks` CI build which wraps around the `uhd security dependencies` CLI command
will fail in the CI pipeline for any dependencies which contain a reported security vulnerability.
