import { useEffect, useRef, useState } from "react";
import "./App.css";

function App() {
  // ==================================================
  // STATE
  // ==================================================
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState([]);
  const [simulationRunning, setSimulationRunning] =
    useState(false);

  const alarmRef = useRef(null);

  // ==================================================
  // FETCH LIVE STATUS FROM BACKEND
  // ==================================================
  useEffect(() => {
    const fetchLiveStatus = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/live-status"
        );

        if (!response.ok) {
          throw new Error(
            "Backend response failed"
          );
        }

        const result =
          await response.json();

        setData(result);
        setConnected(true);
      } catch (error) {
        console.error(
          "Backend connection error:",
          error
        );

        setConnected(false);
      }
    };

    fetchLiveStatus();

    const interval = setInterval(
      fetchLiveStatus,
      1000
    );

    return () => {
      clearInterval(interval);
    };
  }, []);

  // ==================================================
  // FETCH SAFETY EVENT HISTORY
  // ==================================================
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/events"
        );

        if (!response.ok) {
          throw new Error(
            "Event API response failed"
          );
        }

        const result =
          await response.json();

        setEvents(
          result.events || []
        );
      } catch (error) {
        console.error(
          "Event history fetch error:",
          error
        );
      }
    };

    fetchEvents();

    const interval = setInterval(
      fetchEvents,
      1000
    );

    return () => {
      clearInterval(interval);
    };
  }, []);

  // ==================================================
  // CRITICAL RISK ALARM
  // ==================================================
  useEffect(() => {
    if (
      !data ||
      !alarmRef.current
    ) {
      return;
    }

    const alarm =
      alarmRef.current;

    const isCriticalCondition =
      data.risk_level ===
        "CRITICAL" ||
      data.braking_mode ===
        "EMERGENCY_BRAKING" ||
      data.train_status ===
        "THREAT_REACHED";

    const isStoppedSafely =
      data.train_status ===
      "STOPPED_SAFELY";

    if (
      isCriticalCondition &&
      !isStoppedSafely
    ) {
      alarm.loop = true;
      alarm.volume = 1;

      if (alarm.paused) {
        alarm.currentTime = 0;

        alarm
          .play()
          .then(() => {
            console.log(
              "CRITICAL ALARM PLAYING"
            );
          })
          .catch((error) => {
            console.log(
              "Browser blocked automatic alarm:",
              error
            );
          });
      }
    } else {
      if (!alarm.paused) {
        alarm.pause();
      }

      alarm.currentTime = 0;

      console.log(
        "Alarm stopped - system safe"
      );
    }
  }, [
    data?.risk_level,
    data?.braking_mode,
    data?.train_status
  ]);

  // ==================================================
  // RUN NEW SIMULATION
  // ==================================================
  const runNewSimulation =
    async () => {
      try {
        setSimulationRunning(true);

        // Stop old alarm before new run
        if (alarmRef.current) {
          alarmRef.current.pause();
          alarmRef.current.currentTime =
            0;
        }

        const response =
          await fetch(
            "http://127.0.0.1:8000/run-simulation",
            {
              method: "POST"
            }
          );

        if (!response.ok) {
          throw new Error(
            "Failed to start simulation"
          );
        }

        const result =
          await response.json();

        console.log(
          "Simulation started:",
          result
        );
      } catch (error) {
        console.error(
          "Simulation start error:",
          error
        );

        alert(
          "Could not start simulation. Check backend."
        );

        setSimulationRunning(
          false
        );
      }
    };

  // ==================================================
  // UPDATE SIMULATION RUNNING STATE
  // ==================================================
  useEffect(() => {
    if (!data) {
      return;
    }

    const activeStates = [
      "MONITORING",
      "BRAKING"
    ];

    if (
      activeStates.includes(
        data.train_status
      )
    ) {
      setSimulationRunning(
        true
      );
    }

    if (
      data.train_status ===
        "STOPPED_SAFELY" ||
      data.train_status ===
        "THREAT_REACHED"
    ) {
      setSimulationRunning(
        false
      );
    }
  }, [data?.train_status]);

  // ==================================================
  // LOADING SCREEN
  // ==================================================
  if (!data) {
    return (
      <div className="loading-screen">
        <h1>
          RailShield AI
        </h1>

        <p>
          Connecting to railway safety
          system...
        </p>
      </div>
    );
  }

  // ==================================================
  // SYSTEM STATES
  // ==================================================
  const isStoppedSafely =
    data.train_status ===
    "STOPPED_SAFELY";

  const isCritical =
    data.risk_level ===
    "CRITICAL";

  // ==================================================
  // MAIN DASHBOARD
  // ==================================================
  return (
    <div className="dashboard">

      {/* ==============================================
          CRITICAL ALARM AUDIO
      ============================================== */}
      <audio
        ref={alarmRef}
        src="/critical-alarm.mp3"
        preload="auto"
      />

      {/* ==============================================
          HEADER
      ============================================== */}
      <header className="header">

        <div>
          <h1>
            RailShield AI
          </h1>

          <p>
            Intelligent Railway Track
            Threat Detection & Early
            Warning System
          </p>
        </div>

        <div
          className={
            connected
              ? "connection online"
              : "connection offline"
          }
        >
          {connected
            ? "● SYSTEM ONLINE"
            : "● SYSTEM OFFLINE"}
        </div>

      </header>

      {/* ==============================================
          RUN NEW SIMULATION BUTTON
      ============================================== */}
      <section className="simulation-controls">

        <button
          className="run-simulation-button"
          onClick={
            runNewSimulation
          }
          disabled={
            simulationRunning
          }
        >
          {simulationRunning
            ? "⏳ SIMULATION RUNNING..."
            : "▶ RUN NEW SIMULATION"}
        </button>

      </section>

      {/* ==============================================
          COLLISION PREVENTED SUCCESS BANNER
      ============================================== */}
      {isStoppedSafely && (

        <section className="success-banner">

          <div className="success-icon">
            ✓
          </div>

          <div>

            <span>
              RAILSHIELD AI SAFETY
              RESPONSE
            </span>

            <h2>
              COLLISION PREVENTED
            </h2>

            <p>
              TRAIN STOPPED SAFELY
              BEFORE TRACK THREAT
            </p>

          </div>

        </section>

      )}

      {/* ==============================================
          LIVE SAFETY STATUS
      ============================================== */}
      <section
        className={`alert-panel ${
          isCritical
            ? "critical-alert"
            : ""
        }`}
      >

        <div>

          <span>
            LIVE SAFETY STATUS
          </span>

          <h2>
            {data.train_status ||
              "MONITORING"}
          </h2>

        </div>

        <div
          className={`risk-badge ${
            data.risk_level
              ?.toLowerCase() ||
            "low"
          }`}
        >
          {data.risk_level ||
            "LOW"}{" "}
          RISK
        </div>

      </section>

      {/* ==============================================
          LIVE TRACK VISUALIZATION
      ============================================== */}
      <section className="track-visualization">

        <div className="track-header">

          <div>

            <span>
              LIVE TRACK MONITORING
            </span>

            <h3>
              Railway Corridor
              Simulation
            </h3>

          </div>

          <div className="track-distance">

            Threat at KM{" "}

            {data.threat_location_km
              ?.toFixed(2) ||
              "0.00"}

          </div>

        </div>

        <div className="railway-scene">

          <div className="rail-track">

            {/* Railway Lines */}
            <div
              className=
                "rail-line rail-line-top"
            ></div>

            <div
              className=
                "rail-line rail-line-bottom"
            ></div>

            {/* Railway Sleepers */}
            <div className="sleepers">

              {Array.from({
                length: 20
              }).map(
                (_, index) => (

                  <span
                    key={index}
                  ></span>

                )
              )}

            </div>

            {/* Train */}
            <div
              className={`train-marker ${
                data.train_status ===
                "BRAKING"
                  ? "train-braking"
                  : ""
              }`}
              style={{
                left: `${Math.min(
                  Math.max(
                    (
                      data.train_location_km /
                      Math.max(
                        data.threat_location_km ||
                          1,
                        1
                      )
                    ) * 85,
                    2
                  ),
                  82
                )}%`
              }}
            >

              <div className="train-icon">
                🚆
              </div>

              <div className="marker-label">

                KM{" "}

                {data.train_location_km
                  ?.toFixed(2) ||
                  "0.00"}

              </div>

            </div>

            {/* Threat */}
            <div className="threat-marker">

              <div
                className={`threat-icon ${
                  isCritical
                    ? "threat-critical"
                    : ""
                }`}
              >
                ⚠
              </div>

              <div className="marker-label">
                THREAT
              </div>

            </div>

          </div>

          {/* TRACK STATUS */}
          <div className="track-status-row">

            <div>

              <span>
                CURRENT SPEED
              </span>

              <strong>

                {data.train_speed_kmph
                  ?.toFixed(1) ||
                  "0.0"}{" "}
                km/h

              </strong>

            </div>

            <div>

              <span>
                REMAINING DISTANCE
              </span>

              <strong>

                {data.distance_to_threat_km
                  ?.toFixed(3) ||
                  "0.000"}{" "}
                km

              </strong>

            </div>

            <div>

              <span>
                TRAIN MODE
              </span>

              <strong>
                {data.braking_mode ||
                  "MONITORING"}
              </strong>

            </div>

          </div>

        </div>

      </section>

      {/* ==============================================
          DATA CARDS
      ============================================== */}
      <main className="grid">

        <div className="card">

          <span>
            TRAIN SPEED
          </span>

          <h2>
            {data.train_speed_kmph
              ?.toFixed(1) ||
              "0.0"}
          </h2>

          <p>
            km/h
          </p>

        </div>

        <div className="card">

          <span>
            DISTANCE TO THREAT
          </span>

          <h2>
            {data.distance_to_threat_km
              ?.toFixed(3) ||
              "0.000"}
          </h2>

          <p>
            km
          </p>

        </div>

        <div className="card">

          <span>
            TIME TO THREAT
          </span>

          <h2>

            {data.time_to_threat_seconds !=
            null
              ? data.time_to_threat_seconds
                  .toFixed(1)
              : data.train_speed_kmph <= 1
              ? "STOPPED"
              : "N/A"}

          </h2>

          <p>

            {data.time_to_threat_seconds !=
            null
              ? "seconds"
              : data.train_speed_kmph <= 1
              ? "train secured"
              : "not approaching"}

          </p>

        </div>

        <div className="card">

          <span>
            RISK SCORE
          </span>

          <h2>
            {data.risk_score ?? 0}
          </h2>

          <p>
            / 100
          </p>

        </div>

        <div className="card">

          <span>
            STOPPING DISTANCE
          </span>

          <h2>
            {data.stopping_distance_km
              ?.toFixed(3) ||
              "0.000"}
          </h2>

          <p>
            km
          </p>

        </div>

        <div className="card">

          <span>
            SAFETY MARGIN
          </span>

          <h2>
            {data.safety_margin_km
              ?.toFixed(3) ||
              "0.000"}
          </h2>

          <p>
            km
          </p>

        </div>

      </main>

      {/* ==============================================
          CONTROL PANEL
      ============================================== */}
      <section className="control-panel">

        <div>

          <span>
            BRAKING MODE
          </span>

          <h3>
            {data.braking_mode ||
              "NORMAL"}
          </h3>

        </div>

        <div>

          <span>
            RECOMMENDED ACTION
          </span>

          <h3>
            {data.recommended_action ||
              "Continue monitoring"}
          </h3>

        </div>

      </section>

      {/* ==============================================
          SAFETY EVENT TIMELINE
      ============================================== */}
      <section className="event-timeline">

        <div className="event-timeline-header">

          <div>

            <span>
              SYSTEM EVENT HISTORY
            </span>

            <h2>
              Safety Event Timeline
            </h2>

          </div>

          <div className="event-count">
            {events.length} EVENTS
          </div>

        </div>

        <div className="event-list">

          {events.length === 0 ? (

            <div className="no-events">
              No safety events recorded
              yet.
            </div>

          ) : (

            events.map(
              (event, index) => (

                <div
                  key={`${event.timestamp}-${index}`}
                  className={`event-item ${
                    event.risk_level
                      ?.toLowerCase() ||
                    "info"
                  }`}
                >

                  {/* Timeline Indicator */}
                  <div className="event-indicator">

                    <div className="event-dot">
                    </div>

                    {index !==
                      events.length -
                        1 && (

                      <div className="event-line">
                      </div>

                    )}

                  </div>

                  {/* Event Content */}
                  <div className="event-content">

                    <div className="event-top-row">

                      <div className="event-type">

                        {event.event_type
                          ?.replaceAll(
                            "_",
                            " "
                          )}

                      </div>

                      <div
                        className={`event-risk ${
                          event.risk_level
                            ?.toLowerCase() ||
                          "info"
                        }`}
                      >

                        {event.risk_level ||
                          "INFO"}

                      </div>

                    </div>

                    <p>
                      {event.message}
                    </p>

                    <div className="event-time">
                      {event.timestamp}
                    </div>

                  </div>

                </div>

              )
            )

          )}

        </div>

      </section>

      {/* ==============================================
          FOOTER
      ============================================== */}
      <footer>

        RailShield AI • Real-Time
        Railway Safety Intelligence
        Prototype

      </footer>

    </div>
  );
}

export default App;