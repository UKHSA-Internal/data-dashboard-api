from enum import Enum


class _InfectiousDiseaseChildTheme(Enum):
    VACCINE_PREVENTABLE = "vaccine_preventable"
    RESPIRATORY = "respiratory"
    BLOODSTREAM_INFECTION = "bloodstream_infection"
    BLOODBORNE = "bloodborne"
    GASTROINTESTINAL = "gastrointestinal"
    ANTIMICROBIAL_RESISTANCE = "antimicrobial_resistance"
    CONTACT = "contact"
    CHILDHOOD_ILLNESS = "childhood_illness"
    INVASIVE_BACTERIAL_INFECTIONS = "invasive_bacterial_infections"


class _ExtremeEventChildTheme(Enum):
    WEATHER_ALERT = "weather_alert"


class _ImmunisationsChildTheme(Enum):
    CHILDHOOD_VACCINES = "childhood-vaccines"


class _NonCommunicableChildTheme(Enum):
    RESPIRATORY = "respiratory"


class _ClimateAndEnvironmentChildTheme(Enum):
    VECTORS = "vectors"
    CHEMICAL_EXPOSURE = "chemical_exposure"
    SEASONAL_ENVIRONMENTAL = "seasonal_environmental"


class _VectorsTopic(Enum):
    TICKS = "ticks"


class _ChemicalExposureTopic(Enum):
    LEAD = "Lead"


class _SeasonalEnvironmentalTopic(Enum):
    HEAT_OR_SUNSTROKE = "heat-or-sunstroke"
    HEAT_OR_SUNBURN = "heat-or-sunburn"


class _VaccinePreventableTopic(Enum):
    MEASLES = "Measles"


class _ContactTopic(Enum):
    MPOX_CLADE_1B = "mpox-clade-1b"


class _ChildhoodIllnessTopic(Enum):
    SCARLET_FEVER = "Scarlet-fever"


class _BloodbourneTopic(Enum):
    HEPATITIS_C = "Hepatitis-C"


class _WeatherAlertTopic(Enum):
    HEAT_ALERT = "Heat-alert"
    COLD_ALERT = "Cold-alert"


class _ChildhoodVaccinesTopic(Enum):
    MMR1 = "MMR1"


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
    UPPER_RESPIRATORY_TRACT_INFECTION = "upper-respiratory-tract-infection"
    LOWER_RESPIRATORY_TRACT_INFECTION = "lower-respiratory-tract-infection"


class _InvasiveBacterialInfectionsTopic(Enum):
    IGAS = "iGAS"


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
    S_PNEUMONIAE = "S-pneumoniae"
    P_AERUGINOSA = "P-aeruginosa"
    K_PNEUMONIAE = "K-pneumoniae"
    E_FAECIUM = "E-faecium"
    E_FAECALIS = "E-faecalis"


class BaseEnum(Enum):
    def return_list(self):
        return [e.value for e in self.value]


class ParentTheme(Enum):
    INFECTIOUS_DISEASE = "infectious_disease"
    EXTREME_EVENT = "extreme_event"
    NON_COMMUNICABLE = "non-communicable"
    CLIMATE_AND_ENVIRONMENT = "climate_and_environment"
    IMMUNISATIONS = "immunisations"


class ChildTheme(BaseEnum):
    INFECTIOUS_DISEASE = _InfectiousDiseaseChildTheme
    EXTREME_EVENT = _ExtremeEventChildTheme
    NON_COMMUNICABLE = _NonCommunicableChildTheme
    CLIMATE_AND_ENVIRONMENT = _ClimateAndEnvironmentChildTheme
    CHILDHOOD_ILLNESS = _ChildhoodIllnessTopic
    IMMUNISATIONS = _ImmunisationsChildTheme


class Topic(BaseEnum):
    WEATHER_ALERT = _WeatherAlertTopic
    VACCINE_PREVENTABLE = _VaccinePreventableTopic
    RESPIRATORY = _RespiratoryTopic
    BLOODSTREAM_INFECTION = _BloodstreamInfectionTopic
    BLOODBORNE = _BloodbourneTopic
    GASTROINTESTINAL = _GastrointestinalTopic
    ANTIMICROBIAL_RESISTANCE = _AntimicrobialResistanceTopic
    CONTACT = _ContactTopic
    VECTORS = _VectorsTopic
    INVASIVE_BACTERIAL_INFECTIONS = _InvasiveBacterialInfectionsTopic
    CHILDHOOD_ILLNESS = _ChildhoodIllnessTopic
    CHEMICAL_EXPOSURE = _ChemicalExposureTopic
    SEASONAL_ENVIRONMENTAL = _SeasonalEnvironmentalTopic
    CHILDHOOD_VACCINES = _ChildhoodVaccinesTopic
