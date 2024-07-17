from enum import Enum


class _InfectiousDiseaseChildTheme(Enum):
    VACCINE_PREVENTABLE = "vaccine_preventable"
    RESPIRATORY = "respiratory"
    BLOODSTREAM_INFECTION = "bloodstream_infection"
    GASTROINTESTINAL = "gastrointestinal"


class _ExtremeEventChildTheme(Enum):
    WEATHER_ALERT = "weather_alert"


class _VaccinePreventableTopic(Enum):
    MEASLES = "Measles"


class _WeatherAlertTopic(Enum):
    HEAT_ALERT = "Heat-alert"
    COLD_ALERT = "Cold-alert"


class _RespiratoryTopic(Enum):
    COVID_19 = "COVID-19"
    INFLUENZA = "Influenza"
    RSV = "RSV"
    HMPV = "hMPV"
    PARAINFLUENZA = "Parainfluenza"
    RHINOVIRUS = "Rhinovirus"
    ADENOVIRUS = "Adenovirus"


class _BloodstreamInfectionTopic(Enum):
    MRSA = "MRSA"
    MSSA = "MSSA"
    E_COLI = "E-coli"
    KLEBSIELLA_SPP = "Klebsiella-spp"
    PSEUDOMONAS_AERUGINOSA = "Pseudomonas-aeruginosa"


class _GastrointestinalTopic(Enum):
    C_DIFFICILE = "C-difficile"


class BaseEnum(Enum):
    def return_list(self):
        return [e.value for e in self.value]


class ParentTheme(Enum):
    INFECTIOUS_DISEASE = "infectious_disease"
    EXTREME_EVENT = "extreme_event"


class ChildTheme(BaseEnum):
    INFECTIOUS_DISEASE = _InfectiousDiseaseChildTheme
    EXTREME_EVENT = _ExtremeEventChildTheme


class Topic(BaseEnum):
    WEATHER_ALERT = _WeatherAlertTopic
    VACCINE_PREVENTABLE = _VaccinePreventableTopic
    RESPIRATORY = _RespiratoryTopic
    BLOODSTREAM_INFECTION = _BloodstreamInfectionTopic
    GASTROINTESTINAL = _GastrointestinalTopic
