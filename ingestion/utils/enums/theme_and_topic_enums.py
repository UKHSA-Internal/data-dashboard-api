from enum import Enum


class _InfectiousDiseaseChildTheme(Enum):
    VACCINE_PREVENTABLE = "vaccine_preventable"
    RESPIRATORY = "respiratory"
    BLOODSTREAM_INFECTION = "bloodstream_infection"
    GASTROINTESTINAL = "gastrointestinal"
    ANTIMICROBIAL_RESISTANCE = "antimicrobial_resistance"
    CONTACT = "contact"


class _ExtremeEventChildTheme(Enum):
    WEATHER_ALERT = "weather_alert"


class _NonCommunicableChildTheme(Enum):
    RESPIRATORY = "respiratory"


class _VaccinePreventableTopic(Enum):
    MEASLES = "Measles"


class _ContactTopic(Enum):
    MPOX_CLADE_1B = "mpox-clade-1b"


class _WeatherAlertTopic(Enum):
    HEAT_ALERT = "Heat-alert"
    COLD_ALERT = "Cold-alert"


class _RespiratoryTopic(Enum):
    COVID_19 = "COVID-19"
    COVID_19_LIKE = "COVID-19-like"
    INFLUENZA = "Influenza"
    INFLUENZA_LIKE = "influenza-like"
    RSV = "RSV"
    ACUTE_BRONCHIOLITIS = "acute-bronchiolitis"
    ACUTE_RESPIRATORY_INFECTION = "acute-respiratory-infection"
    HMPV = "hMPV"
    PARAINFLUENZA = "Parainfluenza"
    RHINOVIRUS = "Rhinovirus"
    ADENOVIRUS = "Adenovirus"
    ASTHMA = "asthma"


class _BloodstreamInfectionTopic(Enum):
    MRSA = "MRSA"
    MSSA = "MSSA"
    E_COLI = "E-coli"
    KLEBSIELLA_SPP = "Klebsiella-spp"
    PSEUDOMONAS_AERUGINOSA = "Pseudomonas-aeruginosa"


class _GastrointestinalTopic(Enum):
    C_DIFFICILE = "C-difficile"


class _AntimicrobialResistanceTopic(Enum):
    E_COLI = "E-coli"


class BaseEnum(Enum):
    def return_list(self):
        return [e.value for e in self.value]


class ParentTheme(Enum):
    INFECTIOUS_DISEASE = "infectious_disease"
    EXTREME_EVENT = "extreme_event"
    NON_COMMUNICABLE = "non-communicable"


class ChildTheme(BaseEnum):
    INFECTIOUS_DISEASE = _InfectiousDiseaseChildTheme
    EXTREME_EVENT = _ExtremeEventChildTheme
    NON_COMMUNICABLE = _NonCommunicableChildTheme


class Topic(BaseEnum):
    WEATHER_ALERT = _WeatherAlertTopic
    VACCINE_PREVENTABLE = _VaccinePreventableTopic
    RESPIRATORY = _RespiratoryTopic
    BLOODSTREAM_INFECTION = _BloodstreamInfectionTopic
    GASTROINTESTINAL = _GastrointestinalTopic
    ANTIMICROBIAL_RESISTANCE = _AntimicrobialResistanceTopic
    CONTACT = _ContactTopic
