import {
  FaTachometerAlt,
  FaTrain,
  FaRobot,
  FaChartLine,
  FaHistory,
  FaCog,
} from "react-icons/fa";

function Sidebar() {
  return (
    <aside className="sidebar">

      <div className="sidebar-logo">
        🚆
        <h2>RailShield AI</h2>
      </div>

      <nav>

        <button className="sidebar-item active">
          <FaTachometerAlt />
          <span>Dashboard</span>
        </button>

        <button className="sidebar-item">
          <FaTrain />
          <span>Live Monitoring</span>
        </button>

        <button className="sidebar-item">
          <FaRobot />
          <span>AI Detection</span>
        </button>

        <button className="sidebar-item">
          <FaChartLine />
          <span>Analytics</span>
        </button>

        <button className="sidebar-item">
          <FaHistory />
          <span>Timeline</span>
        </button>

        <button className="sidebar-item">
          <FaCog />
          <span>Settings</span>
        </button>

      </nav>

    </aside>
  );
}

export default Sidebar;