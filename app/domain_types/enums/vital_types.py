from enum import Enum

class VitalType(str, Enum):
    BloodGlucose = "blood-glucose"
    BloodOxygenSaturation = "blood-oxygen-saturation"
    BloodPressure = "blood-pressure"
    BodyTemperature = "body-temperature"
    Pulse = "pulse"
    BodyHeight = "body-height"
    BodyWeight = "body-weight"
