import { useEffect, useState } from "react";

import {
  sendLog,
  getAlerts,
  updateAlertStatus,
  logoutUser,
} from "../services/api";

function Dashboard({ onLogout }) {
  const [alerts, setAlerts] = useState([]);
  const [jsonInput, setJsonInput] = useState("");
  const [response, setResponse] = useState("");
  const [error, setError] = useState("");

  const exampleLog = {
    timestamp: new Date().toISOString(),
    source: "firewall",
    source_ip: "10.20.30.100",
    destination_ip: "192.168.1.10",
    destination_port: 22,
    event_type: "failed_login",
    severity: "high",
    message: "Failed SSH login attempt",
  };

  useEffect(() => {
    setJsonInput(JSON.stringify(exampleLog, null, 2));
    loadAlerts();
  }, []);

  async function loadAlerts() {
    try {
      setError("");

      const data = await getAlerts();
      setAlerts(data);
    } catch (error) {
      setError(error.message);
    }
  }

  async function handleSendLog() {
    try {
      setError("");
      setResponse("");

      let parsedLog;

      try {
        parsedLog = JSON.parse(jsonInput);
      } catch {
        setError("Invalid JSON. Please check your JSON format.");
        return;
      }

      const result = await sendLog(parsedLog);

      setResponse(
        JSON.stringify(result, null, 2)
      );

      await loadAlerts();

    } catch (error) {
      setError(error.message);
    }
  }

  function loadExample() {
    setJsonInput(
      JSON.stringify(exampleLog, null, 2)
    );

    setError("");
    setResponse("");
  }

  async function handleStatusChange(alertId, status) {
    try {
      setError("");

      const updatedAlert = await updateAlertStatus(
        alertId,
        status
      );

      setAlerts((previousAlerts) =>
        previousAlerts.map((alert) =>
          alert.id === alertId
            ? updatedAlert
            : alert
        )
      );

    } catch (error) {
      setError(error.message);
    }
  }

  function handleLogout() {
    logoutUser();
    onLogout();
  }

  return (
    <div className="dashboard">

      {/* HEADER */}

      <header className="dashboard-header">

        <div>
          <h1>CyberPulse</h1>

          <p>
            Real-Time Security Log Analytics
          </p>
        </div>

        <button onClick={handleLogout}>
          Logout
        </button>

      </header>


      {/* ERROR */}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}


      {/* JSON LOG INGESTION */}

      <section className="dashboard-card">

        <div className="section-header">

          <div>
            <h2>Security Log Ingestion</h2>

            <p>
              Send security events directly as JSON
            </p>
          </div>

          <button onClick={loadExample}>
            Load Example
          </button>

        </div>


        <textarea
          className="json-editor"
          value={jsonInput}
          onChange={(event) =>
            setJsonInput(event.target.value)
          }
          spellCheck="false"
        />


        <button
          className="primary-button"
          onClick={handleSendLog}
        >
          Send JSON Log
        </button>


        {response && (
          <div className="response-box">

            <h3>API Response</h3>

            <pre>
              {response}
            </pre>

          </div>
        )}

      </section>


      {/* ALERTS */}

      <section className="dashboard-card">

        <div className="section-header">

          <div>
            <h2>Security Alerts</h2>

            <p>
              Threats detected by the CyberPulse
              detection engine
            </p>
          </div>

          <button onClick={loadAlerts}>
            Refresh Alerts
          </button>

        </div>


        {alerts.length === 0 ? (

          <div className="empty-state">
            No security alerts found.
          </div>

        ) : (

          <div className="alerts-container">

            {alerts.map((alert) => (

              <div
                className="alert-card"
                key={alert.id}
              >

                <div className="alert-header">

                  <div>

                    <h3>
                      {alert.threat_type}
                    </h3>

                    <p>
                      Alert #{alert.id}
                    </p>

                  </div>


                  <span
                    className={`severity ${alert.severity}`}
                  >
                    {alert.severity}
                  </span>

                </div>


                <div className="alert-details">

                  <p>
                    <strong>Source IP:</strong>{" "}
                    {alert.source_ip}
                  </p>

                  <p>
                    <strong>Message:</strong>{" "}
                    {alert.message}
                  </p>

                  <p>
                    <strong>Detected:</strong>{" "}
                    {new Date(
                      alert.detected_at
                    ).toLocaleString()}
                  </p>

                </div>


                <div className="ai-analysis">

                  <h4>
                    AI Threat Analysis
                  </h4>

                  <p>
                    {alert.ai_analysis ||
                      "No AI analysis available."}
                  </p>

                </div>


                <div className="alert-footer">

                  <label>
                    Status
                  </label>

                  <select
                    value={alert.status}
                    onChange={(event) =>
                      handleStatusChange(
                        alert.id,
                        event.target.value
                      )
                    }
                  >

                    <option value="open">
                      Open
                    </option>

                    <option value="investigating">
                      Investigating
                    </option>

                    <option value="resolved">
                      Resolved
                    </option>

                  </select>

                </div>

              </div>

            ))}

          </div>

        )}

      </section>

    </div>
  );
}

export default Dashboard;