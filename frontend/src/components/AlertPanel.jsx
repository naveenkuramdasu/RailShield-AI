function AlertPanel({ data, isCritical }) {
  return (
    <section
      className={`alert-panel ${
        isCritical ? "critical-alert" : ""
      }`}
    >
      <div>
        <span>LIVE SAFETY STATUS</span>

        <h2>
          {data.train_status || "MONITORING"}
        </h2>
      </div>

      <div
        className={`risk-badge ${
          data.risk_level?.toLowerCase() || "low"
        }`}
      >
        {data.risk_level || "LOW"} RISK
      </div>
    </section>
  );
}

export default AlertPanel;