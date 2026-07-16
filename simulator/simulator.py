import time
import requests

# ==================================================
# API ENDPOINTS
# ==================================================

API_URL = "http://127.0.0.1:8000/assess-risk"
LIVE_STATUS_URL = "http://127.0.0.1:8000/update-live-status"


# ==================================================
# FIXED SIMULATED TRACK THREAT
# ==================================================

HAZARD_LOCATION_KM = 2.34
HAZARD_CONFIDENCE = 0.91
SENSOR_AGREEMENT = 0.85


# ==================================================
# INITIAL TRAIN STATE
# ==================================================

train_location_km = 0.0
train_speed_kmph = 90.0


# ==================================================
# SIMULATION SETTINGS
# ==================================================

SIMULATION_STEP_SECONDS = 2.0

# Prototype braking assumptions
SERVICE_BRAKING_MPS2 = 0.4
EMERGENCY_BRAKING_MPS2 = 0.8

# Prototype stop threshold
STOPPED_SPEED_THRESHOLD_KMPH = 1.0


# ==================================================
# HELPER FUNCTION
# UPDATE LIVE DASHBOARD
# ==================================================

def update_live_status(live_data):

    try:
        response = requests.post(
            LIVE_STATUS_URL,
            json=live_data,
            timeout=5
        )

        response.raise_for_status()

        return True

    except requests.RequestException as error:

        print(
            f"\nLive status update error: {error}"
        )

        return False


# ==================================================
# START SIMULATION
# ==================================================

print(
    "\nRailShield AI - Dynamic Braking Safety Simulator"
)

print("=" * 140)


while train_location_km < HAZARD_LOCATION_KM:

    # ==================================================
    # 1. SEND CURRENT TRAIN STATE TO RISK ENGINE
    # ==================================================

    data = {
        "hazard_location_km": HAZARD_LOCATION_KM,
        "hazard_confidence": HAZARD_CONFIDENCE,
        "sensor_agreement": SENSOR_AGREEMENT,
        "train_location_km": round(
            train_location_km,
            4
        ),
        "train_speed_kmph": round(
            train_speed_kmph,
            2
        ),
        "train_toward_hazard": True
    }

    try:

        response = requests.post(
            API_URL,
            json=data,
            timeout=5
        )

        response.raise_for_status()

        result = response.json()

    except requests.RequestException as error:

        print(
            f"\nBackend connection error: {error}"
        )

        break


    # ==================================================
    # 2. DECIDE BRAKING MODE
    # ==================================================

    stopping_status = result["stopping_status"]

    risk_level = result["risk_level"]


    if stopping_status == "INSUFFICIENT_MARGIN":

        braking_mode = "EMERGENCY_BRAKING"

        deceleration_mps2 = (
            EMERGENCY_BRAKING_MPS2
        )


    elif risk_level == "CRITICAL":

        braking_mode = "SERVICE_BRAKING"

        deceleration_mps2 = (
            SERVICE_BRAKING_MPS2
        )


    else:

        braking_mode = "MONITORING"

        deceleration_mps2 = 0.0


    # ==================================================
    # 3. SEND CURRENT STATE TO LIVE STATUS API
    # ==================================================

    live_data = {

        "train_location_km": round(
            train_location_km,
            4
        ),

        "train_speed_kmph": round(
            train_speed_kmph,
            2
        ),

        "threat_location_km":
            HAZARD_LOCATION_KM,

        "distance_to_threat_km":
            result["train_distance_km"],

        "time_to_threat_seconds":
            result["time_to_hazard_seconds"],

        "risk_score":
            result["risk_score"],

        "risk_level":
            result["risk_level"],

        "recommended_action":
            result["recommended_action"],

        "stopping_distance_km":
            result[
                "estimated_stopping_distance_km"
            ],

        "safety_margin_km":
            result["safety_margin_km"],

        "braking_mode":
            braking_mode,

        "train_status": (
            "BRAKING"
            if braking_mode != "MONITORING"
            else "MONITORING"
        )
    }


    update_live_status(
        live_data
    )


    # ==================================================
    # 4. DISPLAY CURRENT STATE
    # ==================================================

    tth = result["time_to_hazard_seconds"]

    if tth is None:

        tth_display = "N/A"

    else:

        tth_display = f"{tth:.1f} sec"


    print(

        f"Train: {train_location_km:.3f} km | "

        f"Speed: {train_speed_kmph:.1f} km/h | "

        f"Distance: "
        f"{result['train_distance_km']:.3f} km | "

        f"TTH: {tth_display} | "

        f"Stop Dist: "
        f"{result['estimated_stopping_distance_km']:.3f} km | "

        f"Margin: "
        f"{result['safety_margin_km']:.3f} km | "

        f"Status: {stopping_status} | "

        f"Mode: {braking_mode}"

    )


    # ==================================================
    # 5. CONVERT SPEED FROM KM/H TO M/S
    # ==================================================

    current_speed_mps = (
        train_speed_kmph / 3.6
    )


    # ==================================================
    # 6. APPLY BRAKING
    # ==================================================

    new_speed_mps = max(

        current_speed_mps

        - (

            deceleration_mps2

            * SIMULATION_STEP_SECONDS

        ),

        0.0

    )


    # ==================================================
    # 7. CALCULATE DISTANCE TRAVELLED
    # ==================================================

    average_speed_mps = (

        current_speed_mps

        + new_speed_mps

    ) / 2


    distance_moved_m = (

        average_speed_mps

        * SIMULATION_STEP_SECONDS

    )


    distance_moved_km = (

        distance_moved_m / 1000

    )


    # ==================================================
    # 8. UPDATE TRAIN POSITION AND SPEED
    # ==================================================

    train_location_km += (
        distance_moved_km
    )


    train_speed_kmph = (

        new_speed_mps * 3.6

    )


    # ==================================================
    # 9. CHECK WHETHER TRAIN HAS STOPPED
    # ==================================================

    if (
        train_speed_kmph
        <= STOPPED_SPEED_THRESHOLD_KMPH
    ):

        # Force exact stopped speed
        train_speed_kmph = 0.0


        remaining_distance_km = (

            HAZARD_LOCATION_KM

            - train_location_km

        )


        print("=" * 140)


        # ==============================================
        # SAFE STOP
        # ==============================================

        if remaining_distance_km > 0:


            final_live_data = {

                "train_location_km": round(
                    train_location_km,
                    4
                ),

                "train_speed_kmph": 0.0,

                "threat_location_km":
                    HAZARD_LOCATION_KM,

                "distance_to_threat_km": round(
                    remaining_distance_km,
                    3
                ),

                "time_to_threat_seconds":
                    None,

                "risk_score":
                    0,

                "risk_level":
                    "LOW",

                "recommended_action":
                    (
                        "Collision prevented - "
                        "train stopped safely "
                        "before track threat"
                    ),

                "stopping_distance_km":
                    0.0,

                "safety_margin_km": round(
                    remaining_distance_km,
                    3
                ),

                "braking_mode":
                    "STOPPED",

                "train_status":
                    "STOPPED_SAFELY"
            }


            print(
                "Sending final STOPPED_SAFELY "
                "state to backend..."
            )


            final_update_success = (
                update_live_status(
                    final_live_data
                )
            )


            if final_update_success:

                print(
                    "Final STOPPED_SAFELY "
                    "state sent successfully."
                )

            else:

                print(
                    "WARNING: Final stopped "
                    "state could not be sent."
                )


            print("=" * 140)


            print(

                "TRAIN STOPPED SAFELY - "
                "COLLISION PREVENTED"

            )


            print(

                "Remaining safety distance: "

                f"{remaining_distance_km:.3f} km"

            )


        # ==============================================
        # UNSAFE STOP
        # ==============================================

        else:


            final_live_data = {

                "train_location_km": round(
                    train_location_km,
                    4
                ),

                "train_speed_kmph":
                    0.0,

                "threat_location_km":
                    HAZARD_LOCATION_KM,

                "distance_to_threat_km":
                    0.0,

                "time_to_threat_seconds":
                    0.0,

                "risk_score":
                    100,

                "risk_level":
                    "CRITICAL",

                "recommended_action":
                    "Emergency response required",

                "stopping_distance_km":
                    0.0,

                "safety_margin_km": round(
                    remaining_distance_km,
                    3
                ),

                "braking_mode":
                    "EMERGENCY_STOP",

                "train_status":
                    "THREAT_REACHED"
            }


            print(
                "Sending THREAT_REACHED "
                "state to backend..."
            )


            update_live_status(
                final_live_data
            )


            print(

                "TRAIN REACHED THE TRACK THREAT "
                "BEFORE COMPLETE STOP"

            )


        break


    # ==================================================
    # 10. CHECK WHETHER THREAT LOCATION WAS REACHED
    # ==================================================

    if (
        train_location_km
        >= HAZARD_LOCATION_KM
    ):


        final_live_data = {

            "train_location_km": round(
                train_location_km,
                4
            ),

            "train_speed_kmph": round(
                train_speed_kmph,
                2
            ),

            "threat_location_km":
                HAZARD_LOCATION_KM,

            "distance_to_threat_km":
                0.0,

            "time_to_threat_seconds":
                0.0,

            "risk_score":
                100,

            "risk_level":
                "CRITICAL",

            "recommended_action":
                "Emergency response required",

            "stopping_distance_km":
                0.0,

            "safety_margin_km":
                0.0,

            "braking_mode":
                "EMERGENCY",

            "train_status":
                "THREAT_REACHED"
        }


        update_live_status(
            final_live_data
        )


        print("=" * 140)


        print(

            "CRITICAL: TRAIN REACHED "
            "THE TRACK THREAT "
            "BEFORE COMPLETE STOP"

        )


        break


    # ==================================================
    # WAIT BEFORE NEXT SIMULATION UPDATE
    # ==================================================

    time.sleep(1)


# ==================================================
# SIMULATION COMPLETED
# ==================================================

print("=" * 140)

print(
    "Simulation completed."
)