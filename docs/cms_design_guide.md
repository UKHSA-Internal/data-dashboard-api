# Content Management System Design Guide

## Introduction

This guide will outline the current architecture of the Content Management System (CMS).

The CMS is built on top of [Wagtail](https://docs.wagtail.org/en/stable/).

---

## Structure

There are a number of main `wagtail` apps within the project.

- `dashboard` - this is the main wagtail app to which the others connect into.
- `common` - this is the wagtail app which handles the non-topic pages e.g. the `About` page.
- `composite` - this is the wagtail app which handles non-topic pages that require more customisation e.g. `access-our-data` pages.
- `forms` - this is the wagtail app which handles form-based pages e.g. the `Feedback` page.
- `home` - this is the wagtail app for the landing page.
- `metrics_documentation` - this is the wagtail app for `metrics documentation` pages of the dashboard, including `parent` and `child` page types.
- `snippets` - this is the wagtail app for non-page type models including `internal` and `external` buttons. e.g. `bulk_download button` 
- `topic` - this is the wagtail app for the topic pages e.g. the `COVID-19` or the `Influenza` detail pages.
- `whats_new` - this is the wagtail app for `whats new` section of the dashboard, including both `parent` and `child` page types.
it also includes data migrations for each metric documentation child page.
---

## Data model

The data model is split according to the page types.
There are currently the following main page types:

- `CommonPage`
- `CompositePage`
- `LandingPage`
- `MetricsDocumentationParentPage`
- `MetricsDocumentationChildPage`
- `TopicPage`
- `WhatsNewParentPage`
- `WhatsNewChildEntry`

For each type of page there will also be a foreign key 1-to-many relationship out to 
a corresponding related links type model:

- `CommonPage`(1) -> (many) `CommonPageRelatedLink`
- `TopicPage`(1) -> (many) `TopicPageRelatedLink`
- `CompositePage`(1) -> (many) `CompositePageRelatedLink`
- `MetricsDocumentationParentPage`(1) -> (many) `MetricsDocumentationParentPageRelatedLink`
- `WhatNewParentPage`(1) -> (many) `WhatNewParentPageParentPageRelatedLink`

As a design choice, each object should have a `title` field as well as a `body` field.
Note that the `title` field is inherited from the `wagtail` `Page` class.

---

## Metrics interface

Each section of this codebase is designed so that it communicates across explicitly defined boundaries.
In other words, if code which lives in the `cms/` directory wants to import things from `metrics/`, 
then it **must** do so via the `MetricsAPIInterface` class.

Note that these boundaries are enforced by the `importlinter` tool which will cause the architectural constraints CI 
build to break, if the rules are violated i.e. if communication occurs outside the defined boundaries.

---

## Integration with the frontend

The CMS operates in headless-mode, exposing the text content in the form of a REST API.
The frontend application integrates with the CMS via this REST API.

This API is provided out of the box by wagtail. 
This in the form of a viewset -> `cms/dashboard/viewsets.py`.
Note that the `PagesAPIViewSet` class has been extended to place an API key in front of the CMS endpoints.

This API provides the frontend with all the neccessary parameters required for subsequent calls to the private API.
Note that it is the private API (`charts`, `tables`, `downloads`, `maps`, `headlines`, `trends`) 
which provides the actual page content.

Consider the response returned by the CMS API to be a cookbook of recipes of content items which the content creator
wants to be shown on each page.

---

## Design

The colour scheme can be overriden and modified by changing the `cms/dashboard/static/css/theme.css` file.

This file is currently being injected into the wagtail app by virtue of the `global_admin_css` hook.
This hook can be found at `cms/dashboard/wagtail_hooks.py`.

---

## Current restrictions

### Rich text inputs

All `RichTextField` objects are restricted so that users can only add the following text types:
- bold
- italic
- links
- bullet points

This is achieved by passing the appropriate list of strings to the `features` arg of the `RichTextField` instantiation.

For the `CompositePage` type this list has been extended to include the `code` text type.

### Related links ordering

The related links functionality is currently orderable by the CMS user.
It is **not** currently ordered based on weighting of end user clicks.

### Previews

The CMS integrates with the frontend via a REST API using a token-based preview flow.

When a CMS user clicks the preview button, they are redirected to the frontend with:
- `page_id`: the Wagtail page ID
- `token`: a short-lived signed token (default 15 minutes TTL)

The frontend uses these parameters to fetch draft content:
1. Call `/api/drafts/{page_id}/` with `Authorization: Bearer {token}` header
2. The API validates the token signature, `page_id` match, and expiration
3. Returns the latest draft revision including unpublished changes

The preview URL template is configurable via `PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE` environment variable (defaults to `http://localhost:3000/preview?page_id={page_id}&draft=true&t={token}`).

Token validation:
- Verifies signature using `PAGE_PREVIEWS_TOKEN_SALT` (default: `preview-token`)
- Checks `page_id` claim matches the requested page
- Ensures token hasn't expired (`exp` claim)

See the [environment variables documentation](environment_variables.md#frontend-preview-integration) for frontend integration details and testing.
