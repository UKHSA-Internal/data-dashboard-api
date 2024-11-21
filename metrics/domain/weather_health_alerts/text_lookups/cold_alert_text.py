from metrics.domain.weather_health_alerts.text_lookups import common

_LEVEL_6_TEXT = """
<p>Minor impacts are possible across health and social services, 
including:</p><ul><li>increased use of healthcare services by vulnerable people</li>
<li>greater risk to life of vulnerable people</li></ul>
<p>But not expected.</p>
"""
_LEVEL_7_TEXT = """
<p>Forecast weather is likely to have minor impacts on health and social care services, 
including:</p><ul><li>increased use of healthcare services by vulnerable people</li>
<li>greater risk to life of vulnerable people</li></ul>
"""
_LEVEL_8_TEXT = """
<p>Forecast weather is expected to have minor impacts on health and social care services, 
including:</p><ul><li>increased use of healthcare services by vulnerable people</li>
<li>greater risk to life of vulnerable people</li></ul>
"""
_LEVEL_9_TEXT = """
<p>There is potential for significant impacts across health and social care services, including:</p>
<ul><li>a rise in deaths, particularly among those aged 65 and over or with health conditions. 
We may also see impacts on younger age groups</li>
<li>a likely increase in demand for health services</li>
<li>impacts on the workforce affecting delivery of services</li>
<li>challenges keeping indoor temperatures at the recommended 18°C leading to more risk to vulnerable people</li></ul>
"""
_LEVEL_10_TEXT = """
<p>Significant impacts are possible across health and social care services, 
including:</p><ul><li>a rise in deaths, particularly among those aged 65 and over or 
with health conditions. We may also see impacts on younger age groups</li>
<li>increased demand for remote healthcare services</li>
<li>impacts on the workforce affecting delivery of services</li>
<li>challenges keeping indoor temperatures at the recommended 18°C leading to more risk to vulnerable people</li></ul>
"""
_LEVEL_11_TEXT = """
<p>Forecast weather has the potential to have severe impacts across health and social care services, including:</p>
<ul><li>increased risk to life across the whole population, with significant impacts on older people</li> 
<li>significantly increased demand on all health and social care services</li>
<li>impact on delivery of services due to poor weather conditions and staff access</li>
<li>challenges keeping indoor temperatures at the recommended 18°C leading to more risk to vulnerable people</li>
<li>national critical infrastructure failures, such as generators, power outages and gas supplies</li></ul>
"""
_LEVEL_12_TEXT = """
<p>Forecast weather is likely to cause significant impacts across health and social care services, 
including:</p><ul><li>a rise in deaths, particularly among those aged 65 and over or with 
health conditions. We may also see impacts on younger age groups</li>
<li>a likely increase in demand for health services</li>
<li>temperatures inside places like hospitals, care homes, and clinics dropping below the levels 
recommended for assessing health risks</li>
<li>challenges keeping indoor temperatures at the recommended 18°C leading to more risk to vulnerable people</li>
<li>staffing issues due to external factors (such as travel delays)</li>
<li>other sectors starting to observe impacts (such as transport and energy)</li></ul>
"""
_LEVEL_13_TEXT = """
<p>Forecast weather is expected to have significant impacts across health and social care services, 
including:</p><ul><li>a rise in deaths, particularly among those aged 65 and over 
or with health conditions. We may also see impacts on younger age groups</li>
<li>a likely increase in demand for health services</li>
<li>temperatures inside places like hospitals, care homes, and clinics dropping below the levels 
recommended for assessing health risks</li>
<li>challenges keeping indoor temperatures at the recommended 18°C leading to more risk to vulnerable people</li>
<li>staffing issues due to external factors (such as travel delays)</li>
<li>other sectors starting to observe impacts (such as transport and energy)</li></ul>
"""
_LEVEL_14_TEXT = """
<p>Severe impacts are possible across health and social care services, 
including:</p><ul><li>increased risk to life across the whole population, 
with significant impacts on older people</li><li>significantly increased demand on 
all health and social care services</li>
<li>impact on delivery of services due to poor weather conditions and staff access</li>
<li>challenges keeping indoor temperatures at the recommended 18°C leading to more risk to vulnerable people</li>
<li>national critical infrastructure failures, such as generators, power outages, and gas supplies</li></ul>
"""
_LEVEL_15_TEXT = """
<p>Forecast weather is likely to cause significant impacts across health and social care services, 
including:</p><ul><li>increased risk to life across the whole population, with significant impacts on older people</li>
<li>significantly increased demand on all health and social care services</li>
<li>impact on delivery of services due to poor weather conditions and staff access</li>
<li>challenges keeping indoor temperatures at the recommended 18°C leading to more risk to vulnerable people</li> 
<li>national critical infrastructure failures, such as generators, power outages and gas supplies</li></ul>
"""
_LEVEL_16_TEXT = """
<p>Severe impacts are expected across health and social care services due to forecast weather conditions, 
including:</p><ul><li>increased risk to life across the whole population, with significant impacts on older people
</li><li>significantly increased demand on all health and social care services</li>
<li>impact on delivery of services due to poor weather conditions and staff access</li>
<li>challenges keeping indoor temperatures at the recommended 18°c leading to more risk to vulnerable people</li>
<li>national critical infrastructure failures, such as generators, power outages and gas supplies</li></ul>
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
