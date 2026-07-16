from datetime import datetime


# ==================================================
# IN-MEMORY EVENT STORAGE
# ==================================================

event_history = []

# Maximum number of events to keep
MAX_EVENTS = 100


# ==================================================
# ADD NEW EVENT
# ==================================================

def add_event(
    event_type: str,
    message: str,
    risk_level: str = "INFO"
):
    """
    Add a new railway safety event
    to the event history.
    """

    event = {
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "event_type": event_type,
        "risk_level": risk_level,
        "message": message
    }

    # Add newest event at the beginning
    event_history.insert(0, event)

    # Keep only the latest MAX_EVENTS
    if len(event_history) > MAX_EVENTS:
        event_history.pop()

    return event


# ==================================================
# GET ALL EVENTS
# ==================================================

def get_events():
    """
    Return all recorded events.
    """

    return event_history


# ==================================================
# CLEAR ALL EVENTS
# ==================================================

def clear_events():
    """
    Clear all recorded events before
    starting a fresh simulation.
    """

    event_history.clear()