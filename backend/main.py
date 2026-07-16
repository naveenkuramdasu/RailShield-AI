import subprocess
import sys

from pathlib import Path
from threading import Lock

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import RiskInput, RiskOutput
from risk_engine import calculate_risk
from system_state import system_state

from event_log import (
    add_event,
    get_events,
    clear_events
)


# ==================================================
# FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="RailShield AI API",
    description=(
        "AI-assisted railway track threat risk "
        "assessment and live safety monitoring "
        "prototype"
    ),
    version="0.3.0"
)


# ==================================================
# CORS CONFIGURATION
# ==================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",

        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)


# ==================================================
# EVENT STATE TRACKING
#
# Used to prevent duplicate events from being
# recorded every second.
# ==================================================

previous_train_status = system_state.get(
    "train_status",
    "MONITORING"
)

previous_risk_level = system_state.get(
    "risk_level",
    "LOW"
)

previous_braking_mode = system_state.get(
    "braking_mode",
    "MONITORING"
)


# ==================================================
# SIMULATION PROCESS TRACKING
# ==================================================

simulation_process = None

simulation_lock = Lock()


# ==================================================
# HOME ENDPOINT
# ==================================================

@app.get("/")
def home():

    return {
        "project": "RailShield AI",
        "status": "Backend is running",
        "version": "0.3.0"
    }


# ==================================================
# RISK ASSESSMENT ENDPOINT
# ==================================================

@app.post(
    "/assess-risk",
    response_model=RiskOutput
)
def assess_risk(
    data: RiskInput
):

    return calculate_risk(
        data
    )


# ==================================================
# GET LIVE STATUS
# ==================================================

@app.get("/live-status")
def get_live_status():

    return system_state


# ==================================================
# UPDATE LIVE STATUS
# ==================================================

@app.post("/update-live-status")
def update_live_status(
    data: dict
):

    global previous_train_status

    global previous_risk_level

    global previous_braking_mode


    # ----------------------------------------------
    # READ NEW SYSTEM STATE
    # ----------------------------------------------

    new_train_status = data.get(
        "train_status",
        previous_train_status
    )

    new_risk_level = data.get(
        "risk_level",
        previous_risk_level
    )

    new_braking_mode = data.get(
        "braking_mode",
        previous_braking_mode
    )


    # ==================================================
    # LOG RISK LEVEL CHANGES
    # ==================================================

    if (
        new_risk_level
        !=
        previous_risk_level
    ):

        # ------------------------------------------
        # CRITICAL RISK
        # ------------------------------------------

        if (
            new_risk_level
            ==
            "CRITICAL"
        ):

            add_event(
                event_type=
                    "CRITICAL_RISK",

                message=(
                    "Critical railway track threat "
                    "detected. Immediate safety "
                    "response initiated."
                ),

                risk_level=
                    "CRITICAL"
            )


        # ------------------------------------------
        # HIGH RISK
        # ------------------------------------------

        elif (
            new_risk_level
            ==
            "HIGH"
        ):

            add_event(
                event_type=
                    "HIGH_RISK",

                message=(
                    "High-risk track condition "
                    "detected. Enhanced monitoring "
                    "activated."
                ),

                risk_level=
                    "HIGH"
            )


        # ------------------------------------------
        # MEDIUM RISK
        # ------------------------------------------

        elif (
            new_risk_level
            ==
            "MEDIUM"
        ):

            add_event(
                event_type=
                    "MEDIUM_RISK",

                message=(
                    "Track threat requires "
                    "continued monitoring and "
                    "verification."
                ),

                risk_level=
                    "MEDIUM"
            )


        # ------------------------------------------
        # LOW RISK
        # ------------------------------------------

        elif (
            new_risk_level
            ==
            "LOW"
        ):

            add_event(
                event_type=
                    "LOW_RISK",

                message=(
                    "Railway safety risk returned "
                    "to a low level."
                ),

                risk_level=
                    "LOW"
            )


    # ==================================================
    # LOG BRAKING MODE CHANGES
    # ==================================================

    if (
        new_braking_mode
        !=
        previous_braking_mode
    ):

        # ------------------------------------------
        # SERVICE BRAKING
        # ------------------------------------------

        if (
            new_braking_mode
            ==
            "SERVICE_BRAKING"
        ):

            add_event(
                event_type=
                    "SERVICE_BRAKING",

                message=(
                    "Service braking activated "
                    "in response to critical risk."
                ),

                risk_level=
                    "CRITICAL"
            )


        # ------------------------------------------
        # EMERGENCY BRAKING
        # ------------------------------------------

        elif (
            new_braking_mode
            ==
            "EMERGENCY_BRAKING"
        ):

            add_event(
                event_type=
                    "EMERGENCY_BRAKING",

                message=(
                    "Emergency braking activated "
                    "due to insufficient stopping "
                    "margin."
                ),

                risk_level=
                    "CRITICAL"
            )


        # ------------------------------------------
        # TRAIN STOPPED
        # ------------------------------------------

        elif (
            new_braking_mode
            ==
            "STOPPED"
        ):

            add_event(
                event_type=
                    "TRAIN_STOPPED",

                message=(
                    "Train braking sequence "
                    "completed."
                ),

                risk_level=
                    "LOW"
            )


    # ==================================================
    # LOG TRAIN STATUS CHANGES
    # ==================================================

    if (
        new_train_status
        !=
        previous_train_status
    ):

        # ------------------------------------------
        # BRAKING
        # ------------------------------------------

        if (
            new_train_status
            ==
            "BRAKING"
        ):

            add_event(
                event_type=
                    "BRAKING",

                message=(
                    "Train braking response "
                    "is active."
                ),

                risk_level=
                    new_risk_level
            )


        # ------------------------------------------
        # STOPPED SAFELY
        # ------------------------------------------

        elif (
            new_train_status
            ==
            "STOPPED_SAFELY"
        ):

            remaining_distance = (
                data.get(
                    "distance_to_threat_km",
                    0.0
                )
            )

            add_event(
                event_type=
                    "COLLISION_PREVENTED",

                message=(
                    "Train stopped safely before "
                    "the detected track threat. "
                    f"Remaining safety distance: "
                    f"{remaining_distance:.3f} km."
                ),

                risk_level=
                    "SAFE"
            )


        # ------------------------------------------
        # THREAT REACHED
        # ------------------------------------------

        elif (
            new_train_status
            ==
            "THREAT_REACHED"
        ):

            add_event(
                event_type=
                    "THREAT_REACHED",

                message=(
                    "Train reached the detected "
                    "track threat location."
                ),

                risk_level=
                    "CRITICAL"
            )


        # ------------------------------------------
        # MONITORING
        # ------------------------------------------

        elif (
            new_train_status
            ==
            "MONITORING"
        ):

            add_event(
                event_type=
                    "MONITORING",

                message=(
                    "RailShield AI is actively "
                    "monitoring railway safety."
                ),

                risk_level=
                    "INFO"
            )


    # ==================================================
    # UPDATE LIVE SYSTEM STATE
    # ==================================================

    system_state.update(
        data
    )


    # ==================================================
    # SAVE CURRENT VALUES
    #
    # Used for duplicate event prevention.
    # ==================================================

    previous_train_status = (
        new_train_status
    )

    previous_risk_level = (
        new_risk_level
    )

    previous_braking_mode = (
        new_braking_mode
    )


    return {
        "message": (
            "Live system state updated "
            "successfully"
        ),

        "system_state":
            system_state
    }


# ==================================================
# GET EVENT HISTORY
# ==================================================

@app.get("/events")
def get_event_history():

    events = get_events()

    return {
        "total_events":
            len(events),

        "events":
            events
    }


# ==================================================
# RUN NEW SIMULATION
# ==================================================

@app.post("/run-simulation")
def run_simulation():

    global simulation_process

    global previous_train_status

    global previous_risk_level

    global previous_braking_mode


    # ----------------------------------------------
    # LOCK SIMULATION START
    #
    # Prevents two browser requests from starting
    # two simulations at exactly the same time.
    # ----------------------------------------------

    with simulation_lock:


        # ==========================================
        # CHECK IF SIMULATION IS ALREADY RUNNING
        # ==========================================

        if (
            simulation_process
            is not None
            and
            simulation_process.poll()
            is None
        ):

            return {
                "status":
                    "already_running",

                "message": (
                    "A simulation is already "
                    "running."
                )
            }


        # ==========================================
        # CLEAR OLD EVENT HISTORY
        # ==========================================

        clear_events()


        # ==========================================
        # RESET LIVE SYSTEM STATE
        # ==========================================

        system_state.clear()

        system_state.update({

            "train_location_km":
                0.0,

            "train_speed_kmph":
                90.0,

            "threat_location_km":
                2.34,

            "distance_to_threat_km":
                2.34,

            "time_to_threat_seconds":
                93.6,

            "risk_score":
                0,

            "risk_level":
                "LOW",

            "recommended_action": (
                "Initializing new simulation"
            ),

            "stopping_distance_km":
                0.0,

            "safety_margin_km":
                2.34,

            "braking_mode":
                "MONITORING",

            "train_status":
                "MONITORING"
        })


        # ==========================================
        # RESET EVENT DUPLICATE TRACKING
        # ==========================================

        previous_train_status = (
            "MONITORING"
        )

        previous_risk_level = (
            "LOW"
        )

        previous_braking_mode = (
            "MONITORING"
        )


        # ==========================================
        # FIND PROJECT DIRECTORY
        #
        # Expected structure:
        #
        # RailShield-AI/
        #
        # ├── backend/
        # │   └── main.py
        #
        # ├── simulator/
        # │   └── simulator.py
        #
        # └── frontend/
        # ==========================================

        backend_directory = (
            Path(__file__)
            .resolve()
            .parent
        )

        project_directory = (
            backend_directory
            .parent
        )

        simulator_path = (
            project_directory
            /
            "simulator"
            /
            "simulator.py"
        )


        # ==========================================
        # CHECK SIMULATOR FILE EXISTS
        # ==========================================

        if (
            not
            simulator_path.exists()
        ):

            return {
                "status":
                    "error",

                "message": (
                    "simulator.py was not found "
                    f"at: {simulator_path}"
                )
            }


        # ==========================================
        # START SIMULATOR PROCESS
        # ==========================================

        try:

            simulation_process = (
                subprocess.Popen(
                    [
                        sys.executable,
                        str(
                            simulator_path
                        )
                    ],

                    cwd=str(
                        project_directory
                    )
                )
            )


        except Exception as error:

            return {
                "status":
                    "error",

                "message": (
                    "Failed to start "
                    "simulation: "
                    f"{error}"
                )
            }


        # ==========================================
        # RECORD SIMULATION START EVENT
        # ==========================================

        add_event(
            event_type=
                "SIMULATION_STARTED",

            message=(
                "New RailShield AI safety "
                "simulation started."
            ),

            risk_level=
                "INFO"
        )


        # ==========================================
        # SUCCESS RESPONSE
        # ==========================================

        return {
            "status":
                "started",

            "message": (
                "RailShield AI simulation "
                "started successfully."
            ),

            "process_id":
                simulation_process.pid
        }