from typing import Dict, List, Literal, Optional

from pydantic.main import Any, BaseModel


class ChartPlotParameters(BaseModel):
    chart_type: str
    topic: str
    metric: str
    stratum: Optional[str]
    geography: Optional[str]
    geography_type: Optional[str]
    date_from: Optional[str]

    def to_dict(self) -> Dict[str, str]:
        """Returns a dict representation of the model.

        Notes:
            The `chart_type` and `date_from` are omitted.

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
            if key not in ("chart_type", "date_from")
        }


class ChartPlots(BaseModel):
    plots: List[ChartPlotParameters]
    file_format: Literal["png", "svg", "jpg", "jpeg"]


class ChartPlotData(BaseModel):
    parameters: ChartPlotParameters
    data: Any
