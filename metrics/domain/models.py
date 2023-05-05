from typing import Dict, List, Literal, Optional, Tuple

from pydantic.main import Any, BaseModel


class ChartPlotParameters(BaseModel):
    chart_type: str
    topic: str
    metric: str
    stratum: Optional[str]
    geography: Optional[str]
    geography_type: Optional[str]
    date_from: Optional[str]
    date_to: Optional[str]
    label: str = ""

    @property
    def keys_to_omit_from_dict_representation(self) -> Tuple[str, ...]:
        return "chart_type", "date_from", "date_to", "label"

    def to_dict_for_query(self) -> Dict[str, str]:
        """Returns a dict representation of the model used for the corresponding query.

        Notes:
            A number of fields are ommitted which would not be needed
            for a database query related to this plot.

        Returns:
            Dict[str, str]: A dict representation of the model.
                Where the keys are the names of the fields
                and the values are the values of those fields.
                E.g.
                    >>> {"topic": "COVID-19", ...}

        """
        return {
            key: getattr(self, key)
            for key in self.__fields__
            if getattr(self, key)
            if key not in self.keys_to_omit_from_dict_representation
        }


class ChartPlots(BaseModel):
    plots: List[ChartPlotParameters]
    file_format: Literal["png", "svg", "jpg", "jpeg"]


class ChartPlotData(BaseModel):
    parameters: ChartPlotParameters
    data: Any
