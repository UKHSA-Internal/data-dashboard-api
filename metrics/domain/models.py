from typing import Dict, List, Literal, Optional, Tuple

from pydantic.main import Any, BaseModel


class PlotParameters(BaseModel):
    chart_type: str
    topic: str
    metric: str
    stratum: Optional[str]
    geography: Optional[str]
    geography_type: Optional[str]
    date_from: Optional[str]
    date_to: Optional[str]
    label: Optional[str] = ""
    line_colour: Optional[str] = ""
    line_type: Optional[str] = ""

    @property
    def topic_name(self) -> str:
        return self.topic

    @property
    def metric_name(self) -> str:
        return self.metric

    @property
    def geography_name(self) -> Optional[str]:
        return self.geography

    @property
    def geography_type_name(self) -> Optional[str]:
        return self.geography_type

    @property
    def stratum_name(self) -> Optional[str]:
        return self.stratum

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
                    >>> {"topic_name": "COVID-19", ...}

        """
        return {
            "metric_name": self.metric_name,
            "topic_name": self.topic_name,
            "stratum_name": self.stratum_name,
            "geography_name": self.geography_name,
            "geography_type_name": self.geography_type_name,
            "date_from": self.date_from,
        }


class PlotsCollection(BaseModel):
    plots: List[PlotParameters]
    file_format: Literal["png", "svg", "jpg", "jpeg"]
    chart_width: int
    chart_height: int


class PlotsData(BaseModel):
    parameters: PlotParameters
    x_axis: Any
    y_axis: Any
