from pydantic import BaseModel


class RiskInput(BaseModel):
    hazard_location_km: float
    hazard_confidence: float
    sensor_agreement: float
    train_location_km: float
    train_speed_kmph: float
    train_toward_hazard: bool


class RiskOutput(BaseModel):
    train_distance_km: float
    time_to_hazard_seconds: float | None

    estimated_stopping_distance_km: float
    safety_margin_km: float
    stopping_status: str

    risk_score: int
    risk_level: str
    recommended_action: str