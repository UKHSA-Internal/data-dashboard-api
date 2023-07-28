from metrics.data.models.constants import (
    CHAR_COLUMN_MAX_CONSTRAINT,
    GEOGRAPHY_CODE_MAX_CHAR_CONSTRAINT,
    PERIOD_MAX_CHAR_CONSTRAINT,
    SEX_MAX_CHAR_CONSTRAINT,
)
from tests.fakes.models.metrics.api_time_series import FakeAPITimeSeries


class TestAPITimeSeries:
    period = 0
    age = "all"
    month = 3
    refresh_date = "2023-07-11"
    metric_group = "deaths"
    theme = "infectious_disease"
    sub_theme = "respiratory"
    topic = "COVID-19"
    geography_type = "Government Office Region"
    geography_code = "E45000001"
    geography = "North West"
    metric = "COVID-19_deaths_ONSByDay"
    stratum = "default"
    sex = "all"
    year = "2020"
    epiweek = 11
    dt = "2020-03-10"
    metric_value = 0

    @staticmethod
    def return_concrete_field(model, field_name):
        concreate_field = next(
            field
            for field in model._meta.concrete_fields
            if field.attname == field_name
        )
        return concreate_field

    def test_period_exists(self):
        """
        Given I have a valid period.
        When I initialise a new instance of the api time series model passing the period.
        Then the value will be assigned to the model's period field.
        """
        # Given
        period = self.period

        # When
        api_timeseries_model = FakeAPITimeSeries(period=period)

        # Then
        assert api_timeseries_model.period == period

    def test_period_max_length(self):
        """
        Given I have a period and a max_length value
        When I initialise a new instance of the api time series model passing in the period.
        Then the instance should have meta data of a max_length matching the max_length_constraint
        """
        # Given
        period = self.period
        max_length_constraint = PERIOD_MAX_CHAR_CONSTRAINT

        # When
        api_timeseries_model = FakeAPITimeSeries(period=period)
        period_field = self.return_concrete_field(
            model=api_timeseries_model, field_name="period"
        )

        # Then
        assert period_field.max_length == max_length_constraint

    def test_age_exists(self):
        """
        Given I have a valid age
        When I initialise a new instance of the APITimeSeries model passing the age
        Then the value will be assigned to the model's age field.
        """
        # Given
        age = self.age

        # When
        api_timeseries_model = FakeAPITimeSeries(age=age)

        # Then
        assert api_timeseries_model.age == age

    def test_age_max_length(self):
        """
        Given I have an age and a max_length value
        When I initialise a new instance of the APITimeSeries model passing in the age field.
        Then the instance should have meta_data of a max_length matching the max_length_constraint
        """
        # Given
        age = self.age
        max_length_constraint = CHAR_COLUMN_MAX_CONSTRAINT

        # When
        api_timeseries_model = FakeAPITimeSeries(age=age)
        age_field = self.return_concrete_field(
            model=api_timeseries_model, field_name="age"
        )

        # Then
        assert age_field.max_length == max_length_constraint

    def test_month_exists(self):
        """
        Given I have a valid month
        When I initialise a new instance of the api times series model.
        Then the value will be assigned to the model's month field.
        """
        # Given
        month = self.month

        # When
        api_timeseries_model = FakeAPITimeSeries(month=month)

        # Then
        assert api_timeseries_model.month == month

    def test_refresh_date(self):
        """
        Given I have a valid date.
        When I initialise a new instance of the api times series model passing the refresh date.
        Then the value will be assigned to the model's refresh_date field.
        """
        # Given
        refresh_date = self.refresh_date

        # When
        api_timeseries_model = FakeAPITimeSeries(refresh_date=refresh_date)

        # Then
        assert api_timeseries_model.refresh_date == refresh_date

    def test_metric_group_exists(self):
        """
        Given I have a valid metric group.
        When I initialise a new instance of the api time series model passing the metric_group.
        Then the value will be assigned to the model's metric_group field.
        """
        # Given
        metric_group = self.metric_group

        # When
        api_timeseries_model = FakeAPITimeSeries(metric_group=metric_group)

        # Then
        assert api_timeseries_model.metric_group == metric_group

    def test_metric_group_max_length(self):
        """
        Given I have a metric group and a max_length value
        When I initialise a new instance of the api timeseries model passing in the metric group.
        Then the instance should have meta data of a max_length matching the max_length_constraint
        """
        # Given
        metric_group = self.metric_group
        max_length_constraint = CHAR_COLUMN_MAX_CONSTRAINT

        # When
        api_timeseries_model = FakeAPITimeSeries(metric_group=metric_group)
        metric_group_field = self.return_concrete_field(
            model=api_timeseries_model, field_name="metric_group"
        )

        # Then
        assert metric_group_field.max_length == max_length_constraint

    def test_theme_exists(self):
        """
        Given I have a valid theme.
        When I initialise a new instance of the api timeseries model passing the theme
        Then the value will be assigned to the model's theme field.
        """
        # Given
        theme = self.theme

        # When
        api_timeseries_model = FakeAPITimeSeries(theme=theme)

        # Then
        assert api_timeseries_model.theme == theme

    def test_theme_max_length(self):
        """
        Given I have a theme and a max_length value
        When I initialise a new instance of the api timeseries model passing the theme
        Then the instance should have meta data of a max_length matching max_length_constraint
        """
        # Given
        theme = self.theme
        max_length_constraint = CHAR_COLUMN_MAX_CONSTRAINT

        # When
        api_timeseries_model = FakeAPITimeSeries(theme=theme)
        theme_field = self.return_concrete_field(
            model=api_timeseries_model, field_name="theme"
        )

        # Then
        assert theme_field.max_length == max_length_constraint

    def test_sub_theme_exists(self):
        """
        Given I have a valid sub theme
        When I initialise a new instance of the api timeseries model passing the sub theme
        Then the value will be assigned to the model's sub theme field.
        """
        # Given
        sub_theme = self.sub_theme

        # When
        api_timeseries_model = FakeAPITimeSeries(sub_theme=sub_theme)

        # Then
        assert api_timeseries_model.sub_theme == sub_theme

    def test_sub_theme_max_length(self):
        """
        Given I have a sub theme and a max_length value
        When I initialise a new instance of the api timeseries model passing in the sub_theme.
        Then the instance should have meta data of a max_length matching the max_length_constraint
        """
        # Given
        sub_theme = self.sub_theme
        max_length_constraint = CHAR_COLUMN_MAX_CONSTRAINT

        # When
        api_timeseries_model = FakeAPITimeSeries(sub_theme=sub_theme)
        sub_theme_field = self.return_concrete_field(
            model=api_timeseries_model, field_name="sub_theme"
        )

        # Then
        assert sub_theme_field.max_length == max_length_constraint

    def test_topic_exists(self):
        """
        Given I have a valid topic.
        When I initialise a new instance of the api timeseries model passing the topic
        Then the value will be assigned to the model's topic field.
        """
        # Given
        topic = self.topic

        # When
        api_timeseries_model = FakeAPITimeSeries(topic=topic)

        # Then
        assert api_timeseries_model.topic == topic

    def test_topic_max_length(self):
        """
        Given I have a sub topic and a max_length value
        When I initialise a new instance of the api timeseries model passing in the topic.
        Then the instance should have meta data of a max_length matching the max_length_constraint
        """
        # Given
        topic = self.topic
        max_length_constraint = CHAR_COLUMN_MAX_CONSTRAINT

        # When
        api_timeseries_model = FakeAPITimeSeries(topic=topic)
        topic_field = self.return_concrete_field(
            model=api_timeseries_model, field_name="topic"
        )

        # Then
        assert topic_field.max_length == max_length_constraint

    def test_geography_type_exists(self):
        """
        Given I have a valid geography type.
        When I initialise a new instance of the api series model passing the geography type
        Then the value will be assigned to the model's geography_type field.
        """
        # Given
        geography_type = self.geography_type

        # When
        api_timeseries_model = FakeAPITimeSeries(geography_type=geography_type)

        # Then
        assert api_timeseries_model.geography_type == geography_type

    def test_geography_type_max_length(self):
        """
        Given I have a geography_type and a max_length value
        When I initialise a new instance of the api timeseries model passing in the geography_type
        Then the instance should have meta data of a max_length matching the max_length_constraint
        """
        # Given
        geography_type = self.geography_type
        max_length_constraint = CHAR_COLUMN_MAX_CONSTRAINT

        # When
        api_timeseries_model = FakeAPITimeSeries(geography_type=geography_type)
        geography_type_field = self.return_concrete_field(
            model=api_timeseries_model, field_name="geography_type"
        )

        # Then
        assert geography_type_field.max_length == max_length_constraint

    def test_geography_code(self):
        """
        Given I have a valid geography code.
        When I initialise a new instance of the api time series model passing the geography_code.
        Then the value will be assigned to the model's geography_code field.
        """
        # Given
        geography_code = self.geography_code

        # When
        api_timeseries_model = FakeAPITimeSeries(geography_code=geography_code)

        # Then
        assert api_timeseries_model.geography_code == geography_code

    def test_geography_code_max_length(self):
        """
        Given I have a geography_code and a max_length value
        When I initialise a new instance of the api time series model passing in the geography code.
        Then the instance should have meta data of a max_length matching the max_length_constraint
        """
        # Given
        geography_code = self.geography_code
        max_length_constraint = GEOGRAPHY_CODE_MAX_CHAR_CONSTRAINT

        # When
        api_timeseries_model = FakeAPITimeSeries(geography_code=geography_code)
        geography_code_field = self.return_concrete_field(
            model=api_timeseries_model, field_name="geography_code"
        )

        # Then
        assert geography_code_field.max_length == max_length_constraint

    def test_geography_exists(self):
        """
        Given I have a valid geography value.
        When I initialise a new instance of the api timeseries model passing in geography
        Then the value will be assigned to the model's geography field.
        """
        # Given
        geography = self.geography

        # When
        api_timeseries_model = FakeAPITimeSeries(geography=geography)

        # Then
        assert api_timeseries_model.geography == geography

    def test_geography_max_length(self):
        """
        Given I have a geography and a max_length value
        When I initialise a new instance of the api time series model passing in the geography field.
        Then the instance should have meta data of a max_length matching the max_length_constraint
        """
        # Given
        geography = self.geography
        max_length_constraint = CHAR_COLUMN_MAX_CONSTRAINT

        # When
        api_timeseries_model = FakeAPITimeSeries(geography=geography)
        geography_field = self.return_concrete_field(
            model=api_timeseries_model, field_name="geography"
        )

        # Then
        assert geography_field.max_length == max_length_constraint

    def test_metric_exists(self):
        """
        Given I have a valid metric value.
        When I initialise a new instance of the api timeseries model passing the metric field.
        Then the value will be assigned to the model's geography field.
        """
        # Given
        metric = self.metric

        # When
        api_timeseries_model = FakeAPITimeSeries(metric=metric)

        # Then
        assert api_timeseries_model.metric == metric

    def test_metric_max_length(self):
        """
        Given I have a metric value and a max_length value
        When I initialise a new instance of the api time series model passing in the metric.
        Then the instance should have meta data of a max_length matching the max_length_constraint
        """
        # Given
        metric = self.metric
        max_length_constraint = CHAR_COLUMN_MAX_CONSTRAINT

        # When
        api_timeseries_model = FakeAPITimeSeries(metric=metric)
        metric_field = self.return_concrete_field(
            model=api_timeseries_model, field_name="metric"
        )

        # Then
        assert metric_field.max_length == max_length_constraint

    def test_stratum_exists(self):
        """
        Given I have a valid stratum value.
        When I initialise a new instance of the api time series model passing the stratum.
        Then the value will be assigned to the model's stratum field.
        """
        # Given
        stratum = self.stratum

        # When
        api_timeseries_model = FakeAPITimeSeries(stratum=stratum)

        # Then
        assert api_timeseries_model.stratum == stratum

    def test_stratum_max_length(self):
        """
        Given I have a stratum and a max_length value
        When I initialise a new instance of the api times series model passing in the stratum.
        Then the instance should have meta data of a max_length matching the max_length_constraint
        """
        # Given
        stratum = self.stratum
        max_length_constraint = CHAR_COLUMN_MAX_CONSTRAINT

        # When
        api_timeseries_model = FakeAPITimeSeries(stratum=stratum)
        stratum_field = self.return_concrete_field(
            model=api_timeseries_model, field_name="stratum"
        )

        # Then
        assert stratum_field.max_length == max_length_constraint

    def test_sex_exists(self):
        """
        Given I have a valid sex.
        When I initialise a new instance of the api time series model passing sex.
        Then the value will be assigned to the model's sex field.
        """
        # Given
        sex = self.sex

        # When
        api_timeseries_model = FakeAPITimeSeries(sex=sex)

        # Then
        assert api_timeseries_model.sex == sex

    def test_sex_max_length(self):
        """
        Given I have a sex and a max_length value
        When I initialise a new instance of the api time series model passing in the sex.
        Then the instance should have meta data of a max_length matching the max_length_constraint
        """
        # Given
        sex = self.sex
        max_length_constraint = SEX_MAX_CHAR_CONSTRAINT

        # When
        api_timeseries_model = FakeAPITimeSeries(sex=sex)
        sex_field = self.return_concrete_field(api_timeseries_model, "sex")

        # Then
        assert sex_field.max_length == max_length_constraint

    def test_year_exists(self):
        """
        Given I have a valid year.
        When I initialise a new instance of the api time series model passing the year.
        Then the value will be assigned to the model's year field.
        """
        # Given
        year = self.year

        # When
        api_timeseries_model = FakeAPITimeSeries(year=year)

        # Then
        assert api_timeseries_model.year == year

    def test_epiweek_exists(self):
        """
        Given I have a valid epiweek.
        When I initialise a new instance of the geography model passing the epiweek.
        Then the value will be assigned to the model's epiweek field.
        """
        # Given
        epiweek = self.epiweek

        # When
        api_timeseries_model = FakeAPITimeSeries(epiweek=epiweek)

        # Then
        assert api_timeseries_model.epiweek == epiweek

    def test_dt_exists(self):
        """
        Given I have a valid dt.
        When I initialise a new instance of the api time series model passing the dt.
        Then the value will be assigned to the model's dt field.
        """
        # Given
        dt = self.dt

        # When
        api_timeseries_model = FakeAPITimeSeries(dt=dt)

        # Then
        assert api_timeseries_model.dt == dt

    def test_metric_value_exists(self):
        """
        Given I have a valid metric value.
        When I initialise a new instance of the api time series model passing the metric_value.
        Then the value will be assigned to the model's metric value field.
        """
        # Given
        metric_value = self.metric_value

        # When
        api_timeseries_model = FakeAPITimeSeries(metric_value=metric_value)

        # Then
        assert api_timeseries_model.metric_value == metric_value

    def test_metric_value_max_length(self):
        """
        Given I have a metric value and a max_length value
        When I initialise a new instance of the api time series model passing in the metric value.
        Then the instance should have meta data of a max_length matching the max_length_constraint
        """
        # Given
        metric_value = self.metric_value
        max_length_constraint = CHAR_COLUMN_MAX_CONSTRAINT

        # When
        api_timeseries_model = FakeAPITimeSeries(metric_value=metric_value)
        metric_value_field = self.return_concrete_field(
            model=api_timeseries_model, field_name="metric_value"
        )

        # Then
        assert metric_value_field.max_length == max_length_constraint
