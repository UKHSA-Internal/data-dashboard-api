@classmethod
def _build_timeseries_ingestion_payloads(
    cls,
    *,
    scale_config: dict[str, int],
    is_public: bool,
) -> list[dict[str, object]]:
    _, _, topic_rows = cls._build_theme_hierarchy_records()
    geographies = cls._build_geography_seed_values(count=scale_config["geographies"])
    refresh_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_date = date.today() - timedelta(days=scale_config["days"] - 1)
    payloads: list[dict[str, object]] = []

    for metric_index in range(scale_config["metrics"]):
        topic_name, sub_theme_name, theme_name = topic_rows[
            metric_index % len(topic_rows)
        ]
        metric_name = f"{topic_name}_cases_randomByDay_{metric_index + 1}"

        for geography in geographies:
            time_series_rows: list[dict[str, object]] = []

            for day_offset in range(scale_config["days"]):
                current_date = start_date + timedelta(days=day_offset)

                metric_value = round(
                    random.uniform(5.0, 250.0),  # noqa: B311
                    2,
                )

                time_series_rows.append(
                    {
                        "epiweek": current_date.isocalendar().week,
                        "date": current_date.isoformat(),
                        "metric_value": metric_value,
                        "embargo": None,
                        "is_public": is_public,
                    }
                )

            sex_value = random.choice(SEED_RANDOM_SEX_OPTIONS)  # noqa: S311

            payloads.append(
                {
                    "parent_theme": theme_name,
                    "child_theme": sub_theme_name,
                    "topic": topic_name,
                    "metric_group": "cases",
                    "metric": metric_name,
                    "metric_frequency": TimePeriod.Weekly.value,
                    "geography_type": geography["geography_type"],
                    "geography": geography["name"],
                    "geography_code": geography["geography_code"],
                    "age": "all",
                    "sex": sex_value,
                    "stratum": "default",
                    "refresh_date": refresh_date,
                    "time_series": time_series_rows,
                }
            )

    return payloads
