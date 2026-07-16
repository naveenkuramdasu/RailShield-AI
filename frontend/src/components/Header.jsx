function Header({ connected }) {
  return (
    <header className="header">
      <div>
        <h1>🚆 RailShield AI</h1>

        <p>
          Intelligent Railway Track Threat Detection &
          Early Warning System
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
  );
}

export default Header;