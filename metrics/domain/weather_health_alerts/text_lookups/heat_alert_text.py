from metrics.domain.weather_health_alerts.text_lookups import common

_LEVEL_6_TEXT = """
<p>Minor impacts are possible across the health and social care services, including:</p>
<ul><li>Increased use of healthcare services by vulnerable people</li>
<li>Greater risk to life of vulnerable people</li>
<li>Increased potential for indoor environments to become very warm</li></ul>
<p>But these are not expected.</p>
"""
_LEVEL_7_TEXT = """
<p>Minor impacts are likely across health and social services, 
including:</p><ul><li>increased use of healthcare services by vulnerable people</li>
<li>greater risk to life of vulnerable people</li>
<li>increased potential for indoor environments to become very warm</li></ul>
"""
_LEVEL_8_TEXT = """
<p>Minor impacts are expected across health and social care services, 
including:</p><ul><li>increased use of healthcare services by vulnerable people</li>
<li>greater risk to life of vulnerable people</li>
<li>increased potential for indoor environments to become very warm</li></ul>
"""
_LEVEL_9_TEXT = """
<p>There is potential for significant impacts across health and social care services 
from high temperatures, including:</p><ul><li>a rise in deaths, particularly among those ages 65 and over or with health conditions. 
There may also be impacts on younger age groups</li>
<li>a likely increase in demand for health services</li>
<li>internal temperatures in care settings (hospitals and care homes) may exceed recommended threshold 
for clinical risk assessment</li>
<li>the heat affecting the ability of the workforce to deliver services</li>
<li>indoor environments overheating increasing the risk to vulnerable people living independently in community and care settings</li></ul>
"""
_LEVEL_10_TEXT = """
<p>Significant impacts are possible across the health and social care services due to the high temperatures, 
including:</p><ul><li>a rise in deaths, particularly among those aged 65 and over or with health conditions. There may also be impacts on younger age groups</li>
<li>a likely increase in demand for health services</li>
<li>internal temperatures in care settings (hospitals and care homes) may exceed the recommended threshold 
for clinical risk assessment</li>
<li>the heat affecting the ability of the workforce to deliver services</li>
<li>indoor environments overheating increasing the risk to vulnerable people living independently in community and care settings</li></ul>
"""
_LEVEL_11_TEXT = """
<p>There is potential for severe impacts across health and social care services due to the high temperatures, 
including:</p><ul><li>increased risk to life across the whole population,
with significant impacts on older people</li>
<li>significantly increased demand on all health and social care services</li>
<li>the heat affecting the ability of the workforce to deliver services</li>
<li>hot indoor environments making provision of care challenging and national critical infrastructure failures, such as generators and power outages</li></ul>
"""
_LEVEL_12_TEXT = """
<p>Significant impacts are likely across health and social care services due to the high temperatures, 
including:</p><ul><li>a rise in deaths, particularly among those ages 65 and over or with health conditions.
There may also be impacts on younger age groups</li>
<li>likely increased demand on all health and social care services</li>
<li>internal temperatures in care settings (hospitals and care homes) may exceed recommended threshold 
for clinical risk assessment</li>
<li>the heat affecting the ability of the workforce to deliver services</li>
<li>indoor environments overheating increasing the risk to vulnerable people living independently in community and care settings</li>
<li>issues managing medicines</li>
<li>staffing issues due to external factors (for example, affecting transport)</li>
<li>increased demand for power exceeding capacity</li>
<li>other sectors starting to observe impacts (for example, travel delays)</li></ul>
"""
_LEVEL_13_TEXT = """
<p>Significant impacts are expected across health and social care services due to the high temperatures, 
including:</p><ul><li>a rise in deaths, particularly among those aged 65 and over or with health conditions.
There may also be impacts on younger age groups</li>
<li>likely increased demand on all health and social care services</li>
<li>internal temperatures in care settings (hospitals and care homes) may exceed the recommended threshold 
for clinical risk assessment</li>
<li>the heat affecting the ability of the workforce to deliver services</li>
<li>indoor environments overheating increasing the risk to vulnerable people living independently in community and care settings</li>
<li>issues managing medicines</li>
<li>staffing issues due to external factors (for example, affecting transport)</li>
<li>increased demand for power exceeding capacity</li><li>other sectors starting to observe
impacts (for example, travel delays)</li></ul>
"""
_LEVEL_14_TEXT = """
<p>Severe impacts are possible across health and social care services due to the high temperatures, 
including:</p><ul><li>increased risk to life across the whole population 
with significant impacts on older people</li>
<li>significantly increased demand on all health and social care services</li>
<li>the heat affecting the ability of the workforce to deliver services</li>
<li>hot indoor environments making provision of care challenging 
and national critical infrastructure failures, such as generators and power outages</li></ul>
"""
_LEVEL_15_TEXT = """
<p>Severe impacts are likely across health and social care services due to the high temperatures, 
including:</p><ul><li>increased risk to life across the whole population 
with significant impacts on older people</li>
<li>significantly increased demand on all health and social care services</li>
<li>heat the ability of the workforce to deliver services</li>
<li>hot indoor environments making provision of care challenging and national critical infrastructure failures, such as generators and power outages</li></ul>
"""
_LEVEL_16_TEXT = """
<p>Severe impacts are expected across health and social care services due to the high temperatures, 
including:</p><ul><li>increased risk to life across the whole population,
with significant impacts on older people</li>
<li>significantly increased demand on all health and social care services</li>
<li>the heat affecting the ability of the workforce to deliver services</li>
<li>hot indoor environments making provision of care challenging 
and national critical infrastructure failures, such as generators and power outages</li></ul>
"""

HEAT_ALERT_TEXT_LOOKUP: dict[int, str] = {
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
