API Endpoints (Public API)
==========================

Timeseries Slice
----------------

*/timeseries/themes*
Lists available themes.

*/timeseries/themes/{themename}*
Returns information on a theme.

*/timeseries/themes/{themename}/subthemes*
Lists available subthemes for a given theme.

*/timeseries/themes/{themename}/subthemes/{subthemename}*
Returns information on a subtheme.

*/timeseries/themes/{themename}/subthemes/{subthemename}/topics/*
Lists available topics for a subtheme.

*/timeseries/themes/{themename}/subthemes/{subthemename}/topics/{topicname}*
Returns information on a topic.

*/timeseries/themes/{themename}/subthemes/{subthemename}/topics/{topicname}/geography_types/*
Lists available geography types for a topic.

*/timeseries/themes/{themename}/subthemes/{subthemename}/topics/{topicname}/geography_types/{geography_type}*
Returns information on a geography type.

*/timeseries/themes/{themename}/subthemes/{subthemename}/topics/{topicname}/geography_types/{geography_type}/geography_names/*
Lists available geography names for a given geography type.

*/timeseries/themes/{themename}/subthemes/{subthemename}/topics/{topicname}/geography_types/{geography_type}/geography_names/{geography_name}*
Returns information for a geography name.

*/timeseries/themes/{themename}/subthemes/{subthemename}/topics/{topicname}/geography_types/{geography_type}/geography_names/{geography_name}/metrics*
Lists available metrics for a given geography.

*/timeseries/themes/{themename}/subthemes/{subthemename}/topics/{topicname}/geography_types/{geography_type}/geography_names/{geography_name}/metrics/{metric_name}*
Lists all data for the selected theme, topics and geography for a given metric.

  

Global Query Parameters
-----------------------

?stratum={stratum}: metric subdivision
?year={year}: data for a given year
?epiweek={epiweek}: data for a particular epiweek
?dt={dt}: data for a particular date
?page={page}: the data is paged and this selects the data page

Examples

/timeseries/themes/infectious_disease/subthemes/respiratory/topics/covid-19/geography_types/nation/geography_names/england/metrics/new_cases_daily?year=2023

/timeseries/themes/allergic_diseases/subthemes/respiratory/topics/farmers_lung/geography_types/msoa/geography_names/marple_bridge_and_mellor/metrics/deaths_daily?epiweek=2023_20

