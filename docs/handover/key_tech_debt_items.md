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

### Maps API endpoint optimization

The maps API endpoint was completed under the last major release (COVER) and this endpoint is hugely inefficient. 
This will need optimizing moving forward, particularly as more topic pages make use of the global filter linked maps. 
See [CDD-2808](https://ukhsa.atlassian.net/browse/CDD-2808) for more information on this.

### Extraction of validation & applying to CMS module

Currently, we have a layer of validation at the point of data ingestion.
This can be found primarily at `ingestion/data_transfer_models/`.
It is recommended that you extract the validation functionality from the `ingestion` module and make the validation
its own 1st class module. 
This way you can then share that module with both data ingestion and the `cms/` so that you can bolt on 
CMS input validation for free.

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
