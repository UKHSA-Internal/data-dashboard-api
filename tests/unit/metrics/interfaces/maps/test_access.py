from unittest import mock

import pytest

from metrics.data.models.core_models import Geography
from metrics.domain.models.map import (
    MapAccompanyingPoint,
    MapAccompanyingPointOptionalParameters,
    MapsParameters,
    MapMainParameters,
)
from metrics.interfaces.maps.access import (
    MapsInterface,
    GeographyNotFoundForAccompanyingPointError,
    MapGeographyResult,
)


class TestMapsInterface:
    def test_get_related_geography_for_accompanying_point_uses_fallback_geography_from_main_parameters(
        self,
    ):
        """
        Given a `MapsParameters` model
            which does not define a geography on an accompanying point
        When `_get_related_geography_for_accompanying_point()` is called
            from an instance of the `MapsInterface`
        Then the geography associated with the main parameters
            is used as the fallback geography.
        """
        # Given
        accompanying_point = MapAccompanyingPoint(
            label_prefix="abc",
            label_suffix="",
            parameters=MapAccompanyingPointOptionalParameters(
                theme=None,
                sub_theme=None,
                topic=None,
                metric=None,
                age=None,
                sex=None,
                stratum=None,
                geography_type=None,
                geography=None,
            ),
        )
        maps_parameters = MapsParameters(
            date_from="2020-01-01",
            date_to="2020-12-31",
            parameters=MapMainParameters(
                theme="immunisation",
                sub_theme="childhood-vaccines",
                topic="6-in-1",
                metric="6-in-1_coverage_coverageByYear",
                stratum="12m",
                age="all",
                sex="all",
                geography_type="Upper Tier Local Authority",
                geographies=[],
            ),
            accompanying_points=[accompanying_point],
        )
        maps_interface = MapsInterface(maps_parameters=maps_parameters)
        main_geography = "Leeds"

        # When
        related_geography: str = (
            maps_interface._get_related_geography_for_accompanying_point(
                accompanying_point=accompanying_point,
                main_geography=main_geography,
            )
        )

        # Then
        assert related_geography == main_geography

    def test_get_related_geography_for_accompanying_point_uses_main_geography_when_not_selected(
        self,
    ):
        """
        Given a `MapsParameters` model
            which does define the same geography_type
            on an accompanying point as the main parameter
        When `_get_related_geography_for_accompanying_point()` is called
            from an instance of the `MapsInterface`
        Then the geography associated with the main parameters
            is used as the fallback geography.
        """
        # Given
        accompanying_point = MapAccompanyingPoint(
            label_prefix="abc",
            label_suffix="",
            parameters=MapAccompanyingPointOptionalParameters(
                theme=None,
                sub_theme=None,
                topic=None,
                metric="6-in-1_coverage_oneYearChange",
                age=None,
                sex=None,
                stratum=None,
                geography_type="Upper Tier Local Authority",
                geography=None,
            ),
        )
        maps_parameters = MapsParameters(
            date_from="2020-01-01",
            date_to="2020-12-31",
            parameters=MapMainParameters(
                theme="immunisation",
                sub_theme="childhood-vaccines",
                topic="6-in-1",
                metric="6-in-1_coverage_coverageByYear",
                stratum="12m",
                age="all",
                sex="all",
                geography_type="Upper Tier Local Authority",
                geographies=[],
            ),
            accompanying_points=[accompanying_point],
        )
        maps_interface = MapsInterface(maps_parameters=maps_parameters)
        main_geography = "Leeds"

        # When
        selected_geography: str = (
            maps_interface._get_related_geography_for_accompanying_point(
                accompanying_point=accompanying_point,
                main_geography=main_geography,
            )
        )

        # Then
        assert selected_geography == main_geography

    def test_fetch_related_geography_by_type_raises_error(self):
        """
        Given a payload for a geography which cannot be found
        When `_fetch_related_geography_by_type()` is called
            from an instance of the `MapsInterface`
        Then a `GeographyNotFoundForAccompanyingPointError` is raised
        """
        # Given
        geography = "Leeds"
        main_geography_type = "Upper Tier Local Authority"
        target_geography_type = "Government Office Region"
        mocked_geography_manager = mock.Mock()
        mocked_geography_manager.get_geography_code_for_geography.side_effect = [
            Geography.DoesNotExist
        ]
        maps_interface = MapsInterface(
            maps_parameters=mock.Mock(),
            geography_manager=mocked_geography_manager,
        )

        # When / Then
        with pytest.raises(GeographyNotFoundForAccompanyingPointError):
            maps_interface._fetch_related_geography_by_type(
                geography=geography,
                main_geography_type=main_geography_type,
                target_geography_type=target_geography_type,
            )

    def test_fetch_related_geography_by_type_raises_error_for_unsupported_geography_type(
        self,
    ):
        """
        Given a payload for a geography which can be found
            but an unsupported geography_type
        When `_fetch_related_geography_by_type()` is called
            from an instance of the `MapsInterface`
        Then a `GeographyNotFoundForAccompanyingPointError` is raised
        """
        # Given
        geography = "Leeds"
        main_geography_type = "Upper Tier Local Authority"
        target_geography_type = "UKHSA Super-Region"
        mocked_geography_manager = mock.Mock()
        mocked_geography_manager.get_geography_code_for_geography.return_value = (
            "E08000035"
        )
        maps_interface = MapsInterface(
            maps_parameters=mock.Mock(),
            geography_manager=mocked_geography_manager,
        )

        # When / Then
        with pytest.raises(GeographyNotFoundForAccompanyingPointError):
            maps_interface._fetch_related_geography_by_type(
                geography=geography,
                main_geography_type=main_geography_type,
                target_geography_type=target_geography_type,
            )

    def test_create_null_geography_result(self):
        """
        Given a geography which cannot be found
        When `_create_null_geography_result()` is called
            from an instance of the `MapsInterface`
        Then the returned `MapGeographyResult`
            sets the `geography_code` to an empty string
        """
        # Given
        geography = "Invalid geography"
        mocked_geography_manager = mock.Mock()
        mocked_geography_manager.get_geography_code_for_geography.side_effect = [
            Geography.DoesNotExist
        ]
        maps_interface = MapsInterface(
            maps_parameters=mock.Mock(),
            geography_manager=mocked_geography_manager,
        )

        # When
        map_geography_result: MapGeographyResult = (
            maps_interface._create_null_geography_result(geography=geography)
        )

        # Then
        assert map_geography_result.geography == geography
        assert (
            map_geography_result.geography_type
            == maps_interface.maps_parameters.parameters.geography_type
        )
        assert map_geography_result.geography_code == ""
        assert map_geography_result.metric_value is None
        assert map_geography_result.accompanying_points is None

    @mock.patch.object(MapsInterface, "_get_related_geography_for_accompanying_point")
    def test_process_accompanying_point_returns_none_when_geography_not_found(
        self, mocked_get_related_geography_for_accompanying_point: mock.Mock
    ):
        """
        Given a geography which cannot be found
        When `_process_accompanying_point() is called
            from an instance of the `MapsInterface`
        Then None is returned
        """
        # Given
        mocked_get_related_geography_for_accompanying_point.side_effect = [
            GeographyNotFoundForAccompanyingPointError
        ]
        geography = "Invalid geography"
        mocked_accompanying_point = mock.Mock()
        maps_interface = MapsInterface(maps_parameters=mock.Mock())

        # When
        accompanying_point = maps_interface._process_accompanying_point(
            accompanying_point=mocked_accompanying_point, geography=geography
        )

        # Then
        mocked_get_related_geography_for_accompanying_point.assert_called_once_with(
            accompanying_point=mocked_accompanying_point,
            main_geography=geography,
        )
        assert accompanying_point is None
