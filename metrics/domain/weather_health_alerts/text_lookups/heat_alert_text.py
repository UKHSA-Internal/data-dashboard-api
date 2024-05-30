from metrics.domain.weather_health_alerts.text_lookups import common

_LEVEL_6_TEXT = """
<p>Minor impacts are possible across the health and social care sector, 
including:</p><ul><li>Increased use of health care services by the vulnerable population.</li>
<li>Increase in risk of mortality amongst vulnerable individuals 
and increased potential for indoor environments to become very warm. 
But not expected.</li></ul>
"""
_LEVEL_7_TEXT = """
<p>Minor impacts are probable across the health and social care sector, 
including:</p><ul><li>Increased use of healthcare services by the vulnerable population.</li>
<li>Increase in risk of mortality amongst vulnerable individuals 
and increased potential for indoor environments to become very warm.</li></ul>"""
_LEVEL_8_TEXT = """
<p>Minor impacts are expected across the health and social care sector, 
including:</p><ul><li>Increased use of health care services by the vulnerable population.</li>
<li>Increase in risk of mortality amongst vulnerable individuals 
and increased potential for indoor environments to become very warm.</li></ul>
"""
_LEVEL_9_TEXT = """
<p>There is potential for significant impacts to be observed across the health and social care sector 
due to the high temperatures, including:</p><ul><li>Observed increase in mortality across the population likely, 
particularly in the 65+ age group or those with health conditions, 
but impacts may also be seen in younger age groups.</li>
<li>Increased demand for remote health care services likely
internal temperatures in care settings (hospitals and care homes) may exceed recommended threshold 
for clinical risk assessment.</li>
<li>Impact on ability of services to be delivered due to heat effects on workforce possible 
and many indoor environments likely to be overheating, 
risk to vulnerable people living independently in community as well as in care settings.</li></ul>
"""
_LEVEL_10_TEXT = """
<p>Significant impacts are possible across the health and social care sector due to the high temperatures, 
including:</p><ul><li>Observed increase in mortality across the population likely, 
particularly in the 65+ age group or those with health conditions, 
but impacts may also be seen in younger age groups.</li>
<li>Increased demand for remote health care services likely.</li>
<li>Internal temperatures in care settings (hospitals and care homes) may exceed recommended threshold 
for clinical risk assessment.</li>
<li>Impact on ability of services to be delivered due to heat effects on workforce possible 
and many indoor environments likely to be overheating, 
risk to vulnerable people living independently in community as well as in care settings.</li></ul>
"""
_LEVEL_11_TEXT = """
<p>There is potential for severe impacts to be observed across the health and social care sector 
due to the high temperatures, 
including:</p><ul><li>Increased risk of mortality across the whole population 
with significant mortality observed in older age groups.</li>
<li>Significant increased demand on all health and social care services.</li>
<li>Impact on ability of services to be delivered due to heat effects on workforce.</li>
<li>Indoor environments likely to be hot making provision of care challenging 
and national critical infrastructure failures – generators, power outages etc.</li></ul>
"""
_LEVEL_12_TEXT = """
<p>Significant impacts are probable across the health and social care sector due to the high temperatures, 
including:</p><ul><li>Observed increase in mortality across the population likely, 
particularly in the 65+ age group or those with health conditions, 
but impacts may also be seen in younger age groups.</li>
<li>Increased demand for remote health care services likely.</li>
<li>Internal temperatures in care settings (hospitals and care homes) may exceed recommended threshold 
for clinical risk assessment.</li>
<li>Impact on ability of services to be delivered due to heat effects on workforce possible 
and many indoor environments likely to be overheating, 
risk to vulnerable people living independently in community as well as in care settings.</li>
<li>Medicines management issues.</li><li>Staffing issues due to external factors (e.g. transport).</li> 
<li>Cross system demand for temporary AC capacity being exceeded possible 
and other sectors starting to be observe impacts (e.g. travel delays).</li></ul>
"""
_LEVEL_13_TEXT = """
<p>Significant impacts are expected across the health and social care sector due to the high temperatures, 
including:</p><ul><li>observed increase in mortality across the population likely, 
particularly in the 65+ age group or those with health conditions, 
but impacts may also be seen in younger age groups</li><li>increased demand for remote health care services likely.</li>
<li>internal temperatures in care settings (hospitals and care homes) may exceed recommended threshold 
for clinical risk assessment.</li>
<li>impact on ability of services to be delivered due to heat effects on workforce possible 
and many indoor environments likely to be overheating, 
risk to vulnerable people living independently in community as well as in care settings.</li>
<li>medicines management issues.</li><li>Staffing issues due to external factors (e.g. transport).</li>
<li>cross system demand for temporary AC capacity being exceeded possible 
and other sectors starting to be observe impacts (e.g. travel delays).</li></ul>
"""
_LEVEL_14_TEXT = """
<p>Severe impacts are possible across the health and social care sector due to the high temperatures, 
including:</p><ul><li>Increased risk of mortality across the whole population 
with significant mortality observed in older age groups.</li>
<li>Significant increased demand on all health and social care services.</li>
<li>Impact on ability of services to be delivered due to heat effects on workforce.</li>
<li>Indoor environments likely to be hot making provision of care challenging 
and national critical infrastructure failures – generators, power outages etc.</li></ul>
"""
_LEVEL_15_TEXT = """
<p>Severe impacts are probable across the health and social care sector due to the high temperatures, 
including:</p><ul><li>Increased risk of mortality across the whole population 
with significant mortality observed in older age groups.</li>
<li>Significant increased demand on all health and social care services.</li>
<li>Impact on ability of services to be delivered due to heat effects on workforce.</li>
<li>Indoor environments likely to be hot making provision of care challenging 
and national critical infrastructure failures – generators, power outages etc.</li></ul>
"""
_LEVEL_16_TEXT = """
<p>Severe impacts are expected across the health and social care sector due to the high temperatures, 
including:</p><ul><li>Increased risk of mortality across the whole population 
with significant mortality observed in older age groups.</li>
<li>Significant increased demand on all health and social care services.</li>
<li>Impact on ability of services to be delivered due to heat effects on workforce.</li>
<li>Indoor environments likely to be hot making provision of care challenging 
and national critical infrastructure failures – generators, power outages etc.</li></ul>
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
