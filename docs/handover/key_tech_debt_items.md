# Handover Documentation

## Key outstanding tech debt items 

This document lists and outlines the major outstanding tech debt items 
which should be considered by the next engineering team taking ownership of the UKHSA data dashboard.

### Plotly / Kaleido / Python version bumps

The latest version of `plotly` now depends on the 1st major version of `kaleido` (`v1.0.0`).
`plotly` is used to draw charts, and `kaleido` is used for static chart generation. 
This is what we use to draw `svg` charts and pass them to the frontend.

The problem is that the stable major release of `kaleido` introduces a large breaking change in that it now 
requires Chromium to be bundled into the application.

To be able to upgrade the version of `kaleido`, you will need to include Chromium into the build of the application.
And then you can safely bump `kaleido` and consequently `Python` itself.

> Until then do not bump `kaleido` until the next major version has been properly tested in a live environment.

### Maps API endpoint optimization

The maps API endpoint was completed under the last major release (COVER) and this endpoint is hugely inefficient. 
This will need optimizing moving forward, particularly as more topic pages make use of the global filter linked maps. 
See [CDD-2808](https://ukhsa.atlassian.net/browse/CDD-2808) for more information on this.

### Application of ingestion validation to CMS module

Currently, we have a layer of validation at the point of data ingestion.
This can be found in the top-level `validation` module.
The code in this module used to exist only in the ingestion module but with its extraction and move to a top-level
module it can be shared with the `cms` code, allowing for input validation in the CMS which is consistent with the
ingestion pipeline.

### Specifying complete parameters in CMS inputs

In the CMS, we have a number of components such as charts & headline numbers.
Generally, they ask for the following parameters:

- `topic`
- `metric`
- `geography`
- `geography_type`
- `sex`
- `age`
- `stratum`

However, `topic` **names are not unique** as we can now have the same `topic` appear under multiple `sub_themes`.
At the time of writing (September 2025) this is only the case with the `topic` of `"E-Coli"`, 
which appears under the `sub_themes` of `"bloodstream_infection"` and `"antimicrobial_resistance""`.

As such, you will need to enforce `theme` and `sub_theme` to be provided by the CMS content author.
With those 2 additional fields, the parameters as a whole become entirely explicit and granular.

### Duplication across charts

At the time of writing (September 2025) there are multiple types of charts:

- Single category - seen predominantly across the dashboard
- Dual category - development on this was paused in August 2025 to accommodate the COVER deliverable
- Sub plots - can be seen as the bar charts on the COVER topic page

There is duplication across these modules, particularly across serializers, models and interfaces.
We've now reached the point where it makes sense to implement shared components across these modules.
So this should be resolved when the engineering team have more time and runway to do so.

### Restrict CMS input for selectable maps colours 

The filter linked map in the CMS currently allows any colours for the colours to be applied to threshold filters.
However, the frontend only allows the 5 designated maps colours (as well 4 other deprecated colours)
As such, the selectable colours on the `colour` `ChoiceBlock` of the `ThresholdFilterElement` should 
be restricted to just the 5 designated maps colours:

- `"MAP_COLOUR_1_LIGHT_YELLOW"`
- `"MAP_COLOUR_2_LIGHT_GREEN"`
- `"MAP_COLOUR_3_TURQUOISE"`
- `"MAP_COLOUR_4_BLUE"`
- `"MAP_COLOUR_5_DARK_BLUE"`

### Concurrency methodology in area selector private API crawler

At the time of writing (November 2025), we use the `call_with_star_map_multiprocessing()` handler 
for processing geography combinations in the `AreaSelectorOrchestrator` when crawling the private API.

Moving forward, this could easily be switched to using multi-threading instead as the 
`process_geography_page_combination()` method which is passed to the `call_with_star_map_multiprocessing()` handler.

Once this is done at the infra level we will be able to switch to the `worker` ECS job instead of the `utility-worker`.
This will help save costs and resources which are allocated to the cache flush jobs.
