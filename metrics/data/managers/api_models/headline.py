"""
This file contains the custom queryset and Manger classes associated with the `APIHeadline` model.

"""

from typing import Self

from django.db import models
from django.db.models.functions.window import Rank
from django.utils import timezone


class APIHeadlineQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `APIHeadlineManger`"""

    @staticmethod
    def _newest_to_oldest(
        *, queryset: models.QuerySet, apply_refresh_date_only: bool
    ) -> models.QuerySet:
        if apply_refresh_date_only:
            return queryset.order_by("-refresh_date")
        return queryset.order_by("-period_end", "-refresh_date")

    @staticmethod
    def _exclude_data_under_embargo(*, queryset: models.QuerySet) -> models.QuerySet:
        """Excludes any data which is currently embargoed from the given `queryset`.

        Notes:
            if the `embargo` value is None then it will be included
            in the returned queryset

        Args:
            queryset: The queryset to exclude dates under embargo from

        RETURNS:
            The filtered queryset which includes dates under embargo
        """
        current_time = timezone.now()
        return queryset.filter(
            models.Q(embargo__lte=current_time) | models.Q(embargo=None)
        )

    def get_all_headlines_released_from_embargo(
        self,
        *,
        theme: str,
        sub_theme: str,
        topic: str,
        metric: str,
        geography: str,
        geography_type: str,
        geography_code: str = "",
        stratum: str,
        sex: str,
        age: str,
    ):
        """Filters by the given parameters, includes public and non-public data.

        Args:
           theme: The name of the parent theme being queried.
               E.g. `infectious_disease`
           sub_theme: The name of the child theme being queried.
               E.g. `respiratory`
           topic: The name of the threat being queried.
                E.g. `COVID-19`
           metric: The name of the metric being queried.
               E.g. `COVID-19_headline_7DayAdmissions`
           geography: The name of the geography being queried.
               E.g. `England`
           geography_type: The name of the geography type being queried.
               E.g. `Nation`
           geography_code: Code associated with the geography being queried.
               E.g. "E45000010"
           stratum: The value of the stratum to apply additional filtering to.
               E.g. `default`, which would be used to capture all strata.
           sex: The gender to apply additional filtering to.
               E.g. `F`, would be used to capture Females.
               Note that options are `M`, `F`, or `ALL`.
           age: The age range to apply additional filtering to.
               E.g. `0_4` would be used to capture the age of 0-4 years old

        Returns:
            An ordered queryset from oldest -> newest:
        """
        queryset = self.filter(
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            metric=metric,
            geography=geography,
            geography_type=geography_type,
            geography_code=geography_code,
            stratum=stratum,
            sex=sex,
            age=age,
        )
        queryset = self._exclude_data_under_embargo(queryset=queryset)
        apply_refresh_date_only: bool = "alert" in topic
        return self._newest_to_oldest(
            queryset=queryset, apply_refresh_date_only=apply_refresh_date_only
        )

    def get_public_only_headlines_released_from_embargo(
        self,
        *,
        theme: str,
        sub_theme: str,
        topic: str,
        metric: str,
        geography: str,
        geography_type: str,
        geography_code: str = "",
        stratum: str,
        sex: str,
        age: str,
    ) -> Self:
        queryset = self.get_all_headlines_released_from_embargo(
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            metric=metric,
            geography=geography,
            geography_type=geography_type,
            geography_code=geography_code,
            stratum=stratum,
            age=age,
            sex=sex,
        )
        queryset = queryset.filter(is_public=True)
        apply_refresh_date_only: bool = "alert" in topic
        return self._newest_to_oldest(
            queryset=queryset, apply_refresh_date_only=apply_refresh_date_only
        )

    def get_non_public_only_headlines_released_from_embargo(
        self,
        *,
        theme: str,
        sub_theme: str,
        topic: str,
        metric: str,
        geography: str,
        geography_type: str,
        geography_code: str = "",
        stratum: str,
        sex: str,
        age: str,
    ) -> Self:
        queryset = self.get_all_headlines_released_from_embargo(
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            metric=metric,
            geography=geography,
            geography_type=geography_type,
            geography_code=geography_code,
            stratum=stratum,
            age=age,
            sex=sex,
        )
        queryset = queryset.filter(is_public=False)
        apply_refresh_date_only: bool = "alert" in topic
        return self._newest_to_oldest(
            queryset=queryset, apply_refresh_date_only=apply_refresh_date_only
        )


class APIHeadlineManager(models.Manager):
    """Custom model manager class for the `APIHeadline` model."""

    def get_queryset(self) -> APIHeadlineQuerySet:
        return APIHeadlineQuerySet(self.model, using=self._db)

    def query_for_superseded_data(
        self,
        *,
        theme: str,
        sub_theme: str,
        topic: str,
        metric: str,
        geography: str,
        geography_type: str,
        geography_code: str,
        stratum: str,
        sex: str,
        age: str,
        is_public: bool = True,
    ):
        """Grabs all stale records which are not under embargo.

        Args:
           theme: The name of the parent theme being queried.
               E.g. `infectious_disease`
           sub_theme: The name of the child theme being queried.
               E.g. `respiratory`
           topic: The name of the threat being queried.
                E.g. `COVID-19`
           metric: The name of the metric being queried.
               E.g. `COVID-19_headline_7DayAdmissions`
           geography: The name of the geography being queried.
               E.g. `England`
           geography_type: The name of the geography type being queried.
               E.g. `Nation`
           geography_code: Code associated with the geography being queried.
               E.g. "E45000010"
           stratum: The value of the stratum to apply additional filtering to.
               E.g. `default`, which would be used to capture all strata.
           sex: The gender to apply additional filtering to.
               E.g. `F`, would be used to capture Females.
               Note that options are `M`, `F`, or `ALL`.
           age: The age range to apply additional filtering to.
               E.g. `0_4` would be used to capture the age of 0-4 years old
           is_public: Boolean to decide whether to query for public data.
                If False, then non-public data will be queried for instead.

        Returns:
           The stale records in their entirety as a queryset
        """
        if is_public:
            queryset = (
                self.get_queryset().get_public_only_headlines_released_from_embargo(
                    theme=theme,
                    sub_theme=sub_theme,
                    topic=topic,
                    metric=metric,
                    geography=geography,
                    geography_type=geography_type,
                    geography_code=geography_code,
                    stratum=stratum,
                    age=age,
                    sex=sex,
                )
            )
        else:
            queryset = (
                self.get_queryset().get_non_public_only_headlines_released_from_embargo(
                    theme=theme,
                    sub_theme=sub_theme,
                    topic=topic,
                    metric=metric,
                    geography=geography,
                    geography_type=geography_type,
                    geography_code=geography_code,
                    stratum=stratum,
                    age=age,
                    sex=sex,
                )
            )

        try:
            live_headline_id: int = queryset.first().id
        except AttributeError:
            # Thrown when the queryset was empty
            # And `first()` returned `None`
            return queryset

        return queryset.exclude(id=live_headline_id)

    def delete_superseded_data(
        self,
        *,
        theme: str,
        sub_theme: str,
        topic: str,
        metric: str,
        geography: str,
        geography_type: str,
        geography_code: str,
        stratum: str,
        sex: str,
        age: str,
        is_public: bool = True,
    ) -> None:
        """Deletes all stale records which are not under embargo.


        Args:
           theme: The name of the parent theme being queried.
               E.g. `infectious_disease`
           sub_theme: The name of the child theme being queried.
               E.g. `respiratory`
           topic: The name of the threat being queried.
                E.g. `COVID-19`
           metric: The name of the metric being queried.
               E.g. `COVID-19_headline_7DayAdmissions`
           geography: The name of the geography being queried.
               E.g. `England`
           geography_type: The name of the geography type being queried.
               E.g. `Nation`
           geography_code: Code associated with the geography being queried.
               E.g. "E45000010"
           stratum: The value of the stratum to apply additional filtering to.
               E.g. `default`, which would be used to capture all strata.
           sex: The gender to apply additional filtering to.
               E.g. `F`, would be used to capture Females.
               Note that options are `M`, `F`, or `ALL`.
           age: The age range to apply additional filtering to.
               E.g. `0_4` would be used to capture the age of 0-4 years old
           is_public: Boolean to decide whether to query for public data.
                If False, then non-public data will be queried for instead.

        Returns:
           None
        """
        superseded_records = self.query_for_superseded_data(
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            metric=metric,
            geography=geography,
            geography_type=geography_type,
            geography_code=geography_code,
            stratum=stratum,
            age=age,
            sex=sex,
            is_public=is_public,
        )
        superseded_records.delete()
