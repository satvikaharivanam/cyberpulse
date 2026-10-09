from app.core.connections import redis_client
from app.core.connections import get_pg_connection
from app.services.ai_analyzer import analyze_alert


# Name of the Redis Stream where security logs are stored
STREAM_NAME = "security-events"

# Redis Consumer Group used by the detection engine
GROUP_NAME = "detection-engine"

# Unique name for this detector instance
CONSUMER_NAME = "detector-1"


# Time window for brute-force detection
FAILED_LOGIN_WINDOW = 60

# Number of failed logins required to trigger an alert
FAILED_LOGIN_THRESHOLD = 3


# Time window for port-scan detection
PORT_SCAN_WINDOW = 60

# Number of unique destination ports required
# to trigger a port-scan alert
PORT_SCAN_THRESHOLD = 5


# Time window for unauthorized-access detection
UNAUTHORIZED_ACCESS_WINDOW = 60

# Number of unauthorized attempts required
# to trigger an alert
UNAUTHORIZED_ACCESS_THRESHOLD = 3


def detect_brute_force_behavior(event: dict):
    """
    Detect repeated failed login attempts
    from the same IP within a short time window.
    """

    event_type = event.get("event_type")
    source_ip = event.get("source_ip")
    severity = event.get("severity")

    # Only track failed login events
    if event_type != "failed_login":
        return None

    if not source_ip:
        return None

    # Redis key keeps a separate counter for each source IP
    key = f"failed-logins:{source_ip}"

    # Increase the number of failed logins
    attempts = redis_client.incr(key)

    # Start the 60-second expiration when this IP
    # receives its first failed login
    if attempts == 1:
        redis_client.expire(key, FAILED_LOGIN_WINDOW)

    print(
        f"[BEHAVIOR] {source_ip} has "
        f"{attempts} failed login(s) in the current window"
    )

    # Trigger an alert once the threshold is reached
    if attempts == FAILED_LOGIN_THRESHOLD:
        return {
            "threat_type": "Brute Force Attack",
            "severity": severity,
            "source_ip": source_ip,
            "message": (
                f"Multiple failed login attempts detected "
                f"from {source_ip}"
            ),
        }

    return None


def detect_port_scan_behavior(event: dict):
    """
    Detect multiple unique destination ports
    contacted by the same source IP within a short
    time window.
    """

    source_ip = event.get("source_ip")
    destination_port = event.get("destination_port")
    severity = event.get("severity")

    if not source_ip or destination_port is None:
        return None

    # Redis Set stores unique ports for each source IP
    key = f"port-scan:{source_ip}"

    redis_client.sadd(key, destination_port)

    # Keep the set for 60 seconds
    redis_client.expire(key, PORT_SCAN_WINDOW)

    port_count = redis_client.scard(key)

    print(
        f"[PORT SCAN] {source_ip} contacted "
        f"{port_count} unique port(s) in the current window"
    )

    if port_count == PORT_SCAN_THRESHOLD:
        return {
            "threat_type": "Port Scanning",
            "severity": severity,
            "source_ip": source_ip,
            "message": (
                f"Multiple destination ports scanned "
                f"by {source_ip}"
            ),
        }

    return None


def detect_threat(event: dict):
    """
    Analyze one security event and determine
    whether it matches a known threat pattern.
    """

    event_type = event.get("event_type")
    severity = event.get("severity")

    # Rule 1: Detect brute-force attempts
    if event_type == "brute_force_attempt":
        return {
            "threat_type": "Brute Force Attack",
            "severity": severity,
            "source_ip": event.get("source_ip"),
            "message": "Possible brute-force attack detected",
        }

    # Rule 2: Detect port scanning
    if event_type == "port_scan":
        return {
            "threat_type": "Port Scanning",
            "severity": severity,
            "source_ip": event.get("source_ip"),
            "message": "Possible port scanning activity detected",
        }

    # Rule 3: Detect malware
    if event_type == "malware_detected":
        return {
            "threat_type": "Malware Detection",
            "severity": severity,
            "source_ip": event.get("source_ip"),
            "message": "Potential malware activity detected",
        }

    # Rule 4: Detect unauthorized access
    if event_type == "unauthorized_access":
        return {
            "threat_type": "Unauthorized Access",
            "severity": severity,
            "source_ip": event.get("source_ip"),
            "message": "Possible unauthorized access detected",
        }

    # No known threat detected
    return None


def process_events():
    """
    Continuously listen for new security events
    from the Redis Stream.
    """

    print("[DETECTION ENGINE] Started")
    print(f"[DETECTION ENGINE] Listening to '{STREAM_NAME}'...")

    while True:

        # Wait for new events from the Redis Consumer Group
        events = redis_client.xreadgroup(
            groupname=GROUP_NAME,
            consumername=CONSUMER_NAME,
            streams={STREAM_NAME: ">"},
            count=10,
            block=5000,
        )

        # If no event arrived within 5 seconds,
        # go back and wait again.
        if not events:
            continue

        # Redis returns streams and their messages
        for stream_name, messages in events:

            for event_id, event_data in messages:

                print(f"[EVENT] {event_id}")

                # Check for behavior-based threats
                alert = detect_brute_force_behavior(event_data)

                # If no brute-force behavior was detected,
                # check for port-scan behavior.
                if alert is None:
                    alert = detect_port_scan_behavior(event_data)

                # If no behavior-based threat was detected,
                # check the normal event-type rules.
                if alert is None:
                    alert = detect_threat(event_data)

                if alert:
                    print(f"[ALERT] {alert}")

                    # -------------------------------------------------
                    # Generate AI analysis ONCE when the alert is created
                    # -------------------------------------------------
                    print("[AI] Generating alert analysis with Ollama...")

                    ai_analysis = analyze_alert(
                        threat_type=alert["threat_type"],
                        severity=alert["severity"],
                        source_ip=alert["source_ip"],
                        message=alert["message"],
                    )

                    print("[AI] Analysis generated")

                    # -------------------------------------------------
                    # Save alert + AI analysis in PostgreSQL
                    # -------------------------------------------------
                    with get_pg_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute(
                                """
                                INSERT INTO alerts (
                                    threat_type,
                                    severity,
                                    source_ip,
                                    message,
                                    ai_analysis
                                )
                                VALUES (%s, %s, %s, %s, %s)
                                """,
                                (
                                    alert["threat_type"],
                                    alert["severity"],
                                    alert["source_ip"],
                                    alert["message"],
                                    ai_analysis,
                                ),
                            )

                        # Permanently save the transaction
                        conn.commit()

                    print(
                        "[DATABASE] Alert + AI analysis "
                        "saved to PostgreSQL"
                    )

                else:
                    print(f"[INFO] No threat detected: {event_id}")

                # Tell Redis that this event was successfully processed
                redis_client.xack(
                    STREAM_NAME,
                    GROUP_NAME,
                    event_id,
                )