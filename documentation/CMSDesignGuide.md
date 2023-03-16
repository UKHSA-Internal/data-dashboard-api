# Content Management System Design Guide

## Introduction

This guide will outline the current architecture of the Content Management System (CMS).

The CMS is built on top of [Wagtail](https://docs.wagtail.org/en/stable/).

---

## Structure

There are 4 main `wagtail` apps within the project.

- `dashboard` - this is the main wagtail app to which the others connect into.

- `common` - this is the wagtail app which handles the non-topic pages e.g. the `About` page.
- `home` - this is the wagtail app for the landing page.
- `topic` - this is the wagtail app for the topic pages e.g the `COVID-19` or the `Influenza` detail pages.

---

## Data model

---

## Integration with the frontend

The CMS operates in headless-mode, exposing the text content in the form of a REST API.
The frontend application integrates with the CMS via this REST API.

As such, the responsibility is entirely on the frontend to render the content passed to it by the CMS.

---

## Current restrictions

### Rich text inputs

All `RichTextField` objects are restricted so that users can only add the following text types:
- h2 headings
- h3 headings
- links
- bullet points

This is achieved by passing the appropriate list of strings to the `features` arg of the `RichTextField` instantiation.

### Related links ordering

The related links functionality is currently orderable by the CMS user.
It is **not** currently ordered based on weighting of end user clicks.

### Previews

Because the CMS integrates with the frontend via a REST API. 
Out of the box, the CMS does not therefore have the ability to render content as it would be seen by the end user.

As such, when the CMS user hits the `Live` button for a page, only a rudimentary HTML view of the page will be rendered.

In the future, the CMS can potentially be 
[configured to point to the frontend URL ](https://github.com/torchbox/wagtail-headless-preview)
and effectively ask it for a rendered view.

---

## Current limitations
