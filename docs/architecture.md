# System Architecture Overview

This document provides a high-level overview of the architectural
boundaries and dependency rules enforced across the codebase.

------------------------------------------------------------------------

# 1. High-Level Package Architecture

                            ┌──────────────┐
                            │  public_api  │
                            └───────┬──────┘
                                    │
                                    │ (via designated interface only)
                                    ▼
                             ┌────────────┐
                             │  metrics   │
                             └────────────┘

     ┌────────────┐
     │     cms    │
     └──────┬─────┘
            │
            │ (independent except via interface)
            ▼
         metrics


     ┌────────────┐
     │ ingestion  │
     └──────┬─────┘
            │ (via interface only)
            ▼
         metrics


     ┌────────────┐
     │ validation │
     └──────┬─────┘
            │ (via interface only)
            ▼
         metrics


     ┌────────────┐
     │ feedback   │
     └────────────┘
        (isolated)

Key Principles:

-   `metrics` is the core module.
-   External modules depend on `metrics` only through designated
    interfaces.
-   CMS and Metrics are independent except for controlled integration
    points.
-   Feedback is isolated and behaves like a plugin module.

------------------------------------------------------------------------

# 2. Metrics Internal Layering

Enforced layered architecture:

    metrics.api
          │
          ▼
    metrics.domain
          │
          ▼
    metrics.data

Allowed direction: **top → down**\
Forbidden direction: **bottom → up**

Examples:

-   ✔ `api → domain`
-   ✔ `domain → data`
-   ✖ `data → domain`
-   ✖ `domain → api`

This ensures clean separation of concerns.

------------------------------------------------------------------------

# 3. Metrics Domain Sibling Isolation

Domain submodules are isolated from one another.

    metrics.domain
    │
    ├── bulk_downloads
    ├── charts
    ├── headlines
    ├── tables
    ├── trends
    └── weather_health_alerts

No cross-imports between sibling domains:

-   `charts` ✖ `headlines`
-   `tables` ✖ `trends`
-   `trends` ✖ `weather_health_alerts`

This prevents hidden coupling and keeps business logic modular.

------------------------------------------------------------------------

# 4. Public API Isolation

The Public API module has strict boundaries.

                  public_api
                        │
                        │ (interface only)
                        ▼
                    metrics.interface

Forbidden direct dependencies:

-   metrics.api
-   metrics.domain
-   metrics.data
-   cms
-   ingestion
-   feedback
-   validation

Only designated interfaces are allowed.

------------------------------------------------------------------------

# 5. Ingestion Isolation

    ingestion
        │
        │ (interface only)
        ▼
    metrics.core_models

Ingestion cannot depend directly on:

-   metrics.api
-   cms
-   public_api
-   feedback
-   validation

This maintains a clean ingestion boundary.

------------------------------------------------------------------------

# 6. Feedback Module Isolation

Feedback is intentionally isolated:

    feedback

    (no outward dependencies)

The rest of the system:

-   Cannot import `feedback`
-   Except for explicit URL wiring allowances

This allows feedback to behave like a replaceable subsystem.

------------------------------------------------------------------------

# 7. Source vs Test Boundary

Production code must not depend on test code.

    Source Code  ✖  tests

Prevents accidental coupling to test utilities.

------------------------------------------------------------------------

# Architectural Summary

This architecture represents:

-   A modular monolith
-   Strict layered architecture within the core
-   Interface-based integration
-   Strong dependency direction enforcement
-   Domain isolation
-   Plugin-style subsystems
-   Architectural contracts enforced via Import Linter

The result is a disciplined, maintainable, and evolution-friendly
system.
