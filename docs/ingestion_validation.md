# Ingestion validation documentation

## Introduction

This document outlines the ingestion validation rules and provides a guide to updating these rules. 

---
## Ingestion validation rules

## Metric 

The metric must be constructed in the following way.
`<topic>_<metric_group>_<metric_detail>`

- The `<topic>` must match the provided `Topic` property, this comparison is case insensitive
  - Eg: `influenza` and `Influenza` is a valid match.
- The `<metric_group>` must match the provided `Metric Group`, this comparison is case sensitive
  - Eg: `COVID-19_cases_casesByDay` requires a metric group of `cases`, `Cases` or `deaths` would be invalid
- The metric_detail must be alphanumeric and contain no special characters other than `_`

## Age

The age property can be any of the following:

- The literal string "all"
- An older than type band, which must be a double digit number followed by `+` Eg: 85+
- An age range, which consists of a double digit number, separated by a `-` character, where
the second number must be greater than the first Eg: 45-64

## Parent Theme

The `Parent theme` is validated against an enum, which can be found
at the following location `ingestion/utils/enums/theme_and_topic_enums.py`

Please see **How to add new parent theme, child theme and topics** in the guides section for details on how 
to add new parent themes.

## Child theme

The `Child theme` is validated against an enum, which can be found
at the following location `ingestion/utils/enums/theme_and_topic_enums.py`

A Child theme must also be validated against the `Parent theme`. Eg: a child theme
of `respiratory` will only be valid if the parent theme is `infectious_disease`. This
is done through a hierarchical relationship between enums.

Please see **How to add new parent theme, child theme and topics** in the guides section for details on how
to add new child themes.

## Topic

The `Topic` is validated against a topic enum, which can be found in the
following location `ingestion/utils/enums/theme_and_topic_enums.py`.

A topic must also be validated against both the `Parent theme` and `Child theme`. Eg:
a topic of `influenza` is only valid when the `Parent theme` is `infectious_disease` and the
`Child theme` is `respiratory`.

Please see **How to add new parent theme, child theme and topics** in the guides section for details on how
to add new topics themes.

## Geography Codes

The `geography_code` is validated against the `geography_type` to ensure it follows the correct convention.

- Nation should start with `E92`
- Lower Tier Local Authority should start with one of the following: `E06`, `E07`, `E08`, `E09`
- Upper Tier Local Authority should start with one of the following: `E06`, `E07`, `E08`, `E09`, `E10`
- NHS Region should start with `E40`
- UKHSA Region should start with `E45`
- Government office region should start with `E12`

---

## Guides 

## How to add new parent theme, child theme and topics

The `Parent theme`, `Child theme` and `Topic` properties are all validated against enums, this means that to add any
additional properties in these categories a code change is required.

There is also a requirement that each of these three fields are validated against one another. For example a `Topic` of 
`Influenza` is only valid if the `Child theme` provided is `respiratory` and the `Parent theme` is 
`infectious_disease`.

This is achieved using a collection of enums that are selected via a "parent" enum, meaning that when the `Topic` 
property is being validated, the "topic" enum used to validate against is selected via the `Child theme` name, for example: 
`_RespiartoryTopic` see the code example below.

```python
# Top level enums - ChildTheme and Topic have enums as their value.
class ParentTheme(Enum):
    INFECTIOUS_DISEASE = "infectious_disease"
    
class ChildTheme(Enum):
    INFECTIOUS_DISEASE = _InfectiousDiseaseChildTheme

class Topic(Enum):
    RESPIRATORY = _RespiartoryTopic

# The supported child themes where `Infectious_disease` is the parent theme.
class _InfectiousDiseaseChildTheme(Enum):
    RESPIRATORY = "respiratory"

# The supported topics where `respiratory` is the child theme.
class _RespiartoryTopic(Enum):
    COVID_19 = "COVID-19"
    INFLUENZA = "Influenza"
    RSV = "RSV"
    HMPV = "hMPV"
    PARAINFLUENZA = "Parainfluenza"
    RHINOVIRUS = "Rhinovirus"
    ADENOVIRUS = "Adenovirus"

```

In the example above we can see that our top level enums each match the properties we're validating, for the two "child" properties
`Child theme` and `Topic` their values are also enums, which are named after their parent value. 
Eg: `_InfectioiusDiseaseChildTheme` where the enum contains child theme values that are valid when the `Parent theme`
provided is `infectious_disease`.

To illustrate this further we'll add a new topic, `Measles`. This will belong to a new child theme `vaccine_preventable` and the existing parent theme
`infectious_disease`.

To do this we'll first need to create a new topic enum `_VaccinePreventableTopic`, where we'll include a `Measles` item. In our `_InfectiousDiseaseChildTheme`
enum we'll add a value for `vaccine_preventable`. See the example below.

```python
class _InfectiousDiseaseChildTheme(Enum):
    VACCINE_PREVENTABLE = "vaccine_preventable"
    RESPIRATORY = "respiratory"
    
class _VaccinePreventableTopic(Enum):
    MEASLES = "Measles"
```

With a new topic enum added and our new child theme included in our list of `infectious_disease` child themes we can then add our new `Topic` to the top
level enum under the new `Child theme` name. See the example below.

```python
class Topic(Enum):
  RESPIRATORY = _RespiartoryTopic
  VACCINE_PREVENTABLE = _VaccinePreventableTopic
```

With these updates added our enum file should now look like the example below. Our validation here would work as follows,
Given a `Parent theme` of `infectious_disease` our `Child theme` property would be validated against `_InfectiousDiseaseChildTheme` enum.
Assuming we've provided both `infectious_disease` and `vaccine_preventable` our validation would pass and we'd move on to validating
the `Topic`, which would be validated against the `_VaccinePreventableTopic` enum.

```python
# Top level enums - ChildTheme and Topic have enums as their value.
class ParentTheme(Enum):
    INFECTIOUS_DISEASE = "infectious_disease"
    
class ChildTheme(Enum):
    INFECTIOUS_DISEASE = _InfectiousDiseaseChildTheme

class Topic(Enum):
    RESPIRATORY = _RespiartoryTopic
    VACCINE_PREVENTABLE = _VaccinePreventableTopic
    
# The supported child themes where `Infectious_disease` is the parent theme.
class _InfectiousDiseaseChildTheme(Enum):
    VACCINE_PREVENTABLE = "vaccine_preventable"
    RESPIRATORY = "respiratory"

# The supported topics where `vaccine_preventable` is the child theme.
class _VaccinePreventableTopic(Enum):
    MEASLES = "Measles"

# The supported topics where `respiratory` is the child theme.
class _RespiartoryTopic(Enum):
    COVID_19 = "COVID-19"
    INFLUENZA = "Influenza"
    RSV = "RSV"
    HMPV = "hMPV"
    PARAINFLUENZA = "Parainfluenza"
    RHINOVIRUS = "Rhinovirus"
    ADENOVIRUS = "Adenovirus"
```


**Note**: These changes need to be made to the codebase before any metrics for `Measles` could be ingested.
