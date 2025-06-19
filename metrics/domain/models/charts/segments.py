from pydantic import BaseModel

from metrics.domain.charts.colour_scheme import RGBAChartLineColours


class SegmentParameters(BaseModel):
    secondary_field_value: str
    colour: str | None
    label: str | None

    @property
    def colour_enum(self) -> RGBAChartLineColours:
        if self.colour:
            return RGBAChartLineColours.get_colour(colour=self.colour)

        return RGBAChartLineColours.COLOUR_1_DARK_BLUE
