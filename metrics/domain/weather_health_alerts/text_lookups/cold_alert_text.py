from metrics.domain.weather_health_alerts.text_lookups import common

_LEVEL_6_TEXT = """
Minor impacts are possible across the health and social care sector, 
including: increased use of health care services by the vulnerable population; 
increase in risk of mortality amongst vulnerable individuals. But not expected.
"""
_LEVEL_7_TEXT = """
Minor impacts are probable across the health and social care sector, 
including: increased use of healthcare services by the vulnerable population; 
increase in risk of mortality amongst vulnerable individuals.
"""
_LEVEL_8_TEXT = """
Minor impacts are expected across the health and social care sector, 
including: increased use of health care services by the vulnerable population; 
increase in risk of mortality amongst vulnerable individuals.
"""
_LEVEL_9_TEXT = """
There is potential for significant impacts to be observed across the health and social care sector 
due to forecast weather conditions, including: observed increase in mortality across the population, 
particularly in the 65+ age group or those with certain underlying health conditions, 
but impacts may also be seen in younger age groups; increased demand for remote health care services likely; 
impact on ability of services delivered due to effects on workforce possible; 
maintaining indoor temperatures at recommended 18°c may become challenging for some, 
leading to increased risk of vulnerable people.
"""
_LEVEL_10_TEXT = """
Significant impacts are possible across the health and social care sector due to forecast weather conditions, 
including: observed increase in mortality across the population, 
particularly in the 65+ age group or those with certain underlying health conditions, 
but impacts may also be seen in younger age groups; 
increased demand for remote health care services likely; 
impact on ability of services delivered due to effects on workforce possible; 
maintaining indoor temperatures at recommended 18°c may become challenging for some, 
leading to increased risk of vulnerable people.
"""
_LEVEL_11_TEXT = """
There is potential for severe impacts to be observed across the health and social care sector 
due to forecast weather conditions, including: increased risk of mortality across the whole population 
with significant mortality observed in older age groups; 
significant increased demand on all health and social care services; 
impact on delivery of services due to poor weather conditions and staff access; 
maintaining indoor temperatures at recommended 18°c may become challenging for some, 
leading to increased risk of vulnerable people; 
national critical infrastructure failures – generators, power outages, gas supplies etc.
"""
_LEVEL_12_TEXT = """
Significant impacts are probable across the health and social care sector due to forecast weather conditions, 
including: observed increase in mortality across the population, 
particularly in the 65+ age group or those with certain underlying health conditions, 
but impacts may also be seen in younger age groups; 
increased demand for remote health care services likely; 
internal temperatures in care settings (e.g. hospitals, care homes and primary care settings) 
may fall below recommended threshold for clinical risk assessment; 
maintaining indoor temperatures at recommended 18°c may become challenging for some, 
leading to increased risk of vulnerable people; 
staffing issues due to external factors (e.g. travel delays); 
other sectors may start to observe impacts (e.g. transport and energy).
"""
_LEVEL_13_TEXT = """
Significant impacts are expected across the health and social care sector due to forecast weather conditions, 
including: observed increase in mortality across the population, 
particularly in the 65+ age group or those with certain underlying health conditions, 
but impacts may also be seen in younger age groups; 
increased demand for remote health care services likely; 
internal temperatures in care settings (e.g. hospitals, care homes and primary care settings) 
may fall below recommended threshold for clinical risk assessment; 
maintaining indoor temperatures at recommended 18°c may become challenging for some, 
leading to increased risk of vulnerable people; staffing issues due to external factors (e.g. travel delays); 
other sectors starting to observe impacts (e.g. transport and energy); 
other sectors starting to observe impacts (e.g. transport and energy).
"""
_LEVEL_14_TEXT = """
Severe impacts are possible across the health and social care sector due to forecast weather conditions, 
including: increased risk of mortality across the whole population with significant mortality 
observed in older age groups; significant increased demand on all health and social care services; 
impact on delivery of services due to poor weather conditions and staff access; 
maintaining indoor temperatures at recommended 18°c may become challenging for some, 
leading to increased risk of vulnerable people; 
national critical infrastructure failures – generators, power outages, gas supplies etc.
"""
_LEVEL_15_TEXT = """
Severe impacts are probable across the health and social care sector due to forecast weather conditions, 
including: increased risk of mortality across the whole population with significant mortality 
observed in older age groups; significant increased demand on all health and social care services; 
impact on delivery of services due to poor weather conditions and staff access; 
maintaining indoor temperatures at recommended 18°c may become challenging for some, 
leading to increased risk of vulnerable people; 
national critical infrastructure failures – generators, power outages, gas supplies etc.
"""
_LEVEL_16_TEXT = """
Severe impacts are expected across the health and social care sector due to forecast weather conditions, 
including: increased risk of mortality across the whole population with significant mortality 
observed in older age groups; significant increased demand on all health and social care services; 
impact on delivery of services due to poor weather conditions and staff access; 
maintaining indoor temperatures at recommended 18°c may become challenging for some, 
leading to increased risk of vulnerable people;
national critical infrastructure failures – generators, power outages, gas supplies etc.
"""

COLD_ALERT_TEXT_LOOKUP: dict[int, str] = {
    1: common.LEVELS_1_TO_4_TEXT,
    2: common.LEVELS_1_TO_4_TEXT,
    3: common.LEVELS_1_TO_4_TEXT,
    4: common.LEVELS_1_TO_4_TEXT,
    5: common.LEVEL_5_TEXT,
    6: _LEVEL_6_TEXT,
    7: _LEVEL_7_TEXT,
    8: _LEVEL_8_TEXT,
    9: _LEVEL_9_TEXT,
    10: _LEVEL_10_TEXT,
    11: _LEVEL_11_TEXT,
    12: _LEVEL_12_TEXT,
    13: _LEVEL_13_TEXT,
    14: _LEVEL_14_TEXT,
    15: _LEVEL_15_TEXT,
    16: _LEVEL_16_TEXT,
}
