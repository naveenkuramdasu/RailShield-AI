from models import RiskInput


def calculate_risk(data: RiskInput):
    # --------------------------------------------------
    # 1. Calculate distance between train and track threat
    # --------------------------------------------------
    distance = abs(
        data.hazard_location_km - data.train_location_km
    )

    score = 0.0

    # --------------------------------------------------
    # 2. Threat confidence - Maximum 30 points
    # --------------------------------------------------
    score += data.hazard_confidence * 30

    # --------------------------------------------------
    # 3. Sensor agreement - Maximum 20 points
    # --------------------------------------------------
    score += data.sensor_agreement * 20

    # --------------------------------------------------
    # 4. Train proximity - Maximum 30 points
    # --------------------------------------------------
    if distance < 0.5:
        score += 30
    elif distance < 1.0:
        score += 25
    elif distance < 3.0:
        score += 15
    elif distance < 5.0:
        score += 5

    # --------------------------------------------------
    # 5. Train speed - Maximum 10 points
    # --------------------------------------------------
    if data.train_speed_kmph >= 100:
        score += 10
    elif data.train_speed_kmph >= 60:
        score += 7
    elif data.train_speed_kmph > 0:
        score += 3

    # --------------------------------------------------
    # 6. Train direction - Maximum 10 points
    # --------------------------------------------------
    if data.train_toward_hazard:
        score += 10

    # Keep final score between 0 and 100
    score = min(round(score), 100)

    # --------------------------------------------------
    # 7. Calculate Time To Threat (TTH)
    # --------------------------------------------------
    if data.train_toward_hazard and data.train_speed_kmph > 1.0:
        time_to_hazard_seconds = (
            distance / data.train_speed_kmph
        ) * 3600
    else:
        time_to_hazard_seconds = None

    # --------------------------------------------------
    # 8. Estimate stopping distance
    #
    # Prototype assumption:
    # reaction delay = 5 seconds
    # average braking deceleration = 0.6 m/s²
    #
    # NOTE:
    # This is a simulation estimate, not an operational
    # railway braking model.
    # --------------------------------------------------
    speed_mps = data.train_speed_kmph / 3.6

    reaction_time_seconds = 5.0
    assumed_deceleration_mps2 = 0.6

    reaction_distance_m = speed_mps * reaction_time_seconds

    if speed_mps > 0:
        braking_distance_m = (
            speed_mps ** 2
        ) / (2 * assumed_deceleration_mps2)
    else:
        braking_distance_m = 0.0

    estimated_stopping_distance_km = (
        reaction_distance_m + braking_distance_m
    ) / 1000

    # --------------------------------------------------
    # 9. Calculate safety margin
    # --------------------------------------------------
    safety_margin_km = (
        distance - estimated_stopping_distance_km
    )

    # --------------------------------------------------
    # 10. Determine stopping status
    # --------------------------------------------------
    if not data.train_toward_hazard:
        stopping_status = "NOT_APPROACHING"

    elif safety_margin_km <= 0:
        stopping_status = "INSUFFICIENT_MARGIN"

    elif safety_margin_km < 0.5:
        stopping_status = "LIMITED_MARGIN"

    else:
        stopping_status = "SAFE_MARGIN"

    # --------------------------------------------------
    # 11. Determine risk level and recommended action
    # --------------------------------------------------
    if (
        data.train_toward_hazard
        and stopping_status == "INSUFFICIENT_MARGIN"
    ):
        risk_level = "CRITICAL"
        action = (
            "Immediate operator alert - "
            "estimated stopping margin is insufficient"
        )

    elif score >= 80:
        risk_level = "CRITICAL"
        action = "Immediate operator attention"

    elif score >= 60:
        risk_level = "HIGH"
        action = "High priority monitoring and verification"

    elif score >= 30:
        risk_level = "MEDIUM"
        action = "Monitor the detected track threat"

    else:
        risk_level = "LOW"
        action = "Continue monitoring"

    # --------------------------------------------------
    # 12. Final response
    # --------------------------------------------------
    return {
        "train_distance_km": round(distance, 3),

        "time_to_hazard_seconds": (
            round(time_to_hazard_seconds, 1)
            if time_to_hazard_seconds is not None
            else None
        ),

        "estimated_stopping_distance_km": round(
            estimated_stopping_distance_km, 3
        ),

        "safety_margin_km": round(
            safety_margin_km, 3
        ),

        "stopping_status": stopping_status,

        "risk_score": score,
        "risk_level": risk_level,
        "recommended_action": action
    }