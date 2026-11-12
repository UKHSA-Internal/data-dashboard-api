import pytest

from metrics.domain.charts.chart_axis_groups import X_DOMINANT_CHARTS, pick_axis
from metrics.domain.common.utils import ChartTypes

"""
    File name: test_chart_axis_groups.py
    individually tests chart types without referencing the lists within chart axis groups    
"""
class TestChartAxisGroups:

    def test_chart_types_return_expected(self):

        # X Chart
        assert pick_axis(ChartTypes.stacked_bar.value, True, False)

        # Y Chart
        assert pick_axis(ChartTypes.butterfly.value, False, True)

        # Neither
        with pytest.raises(ValueError):
            assert pick_axis(ChartTypes.bar.value, False, False)

        with pytest.raises(ValueError):
            assert pick_axis(ChartTypes.line_multi_coloured.value, False, False)

        with pytest.raises(ValueError):
            assert pick_axis(ChartTypes.line_single_simplified.value, False, False)

        with pytest.raises(ValueError):
            assert pick_axis("unknown", False, False)
