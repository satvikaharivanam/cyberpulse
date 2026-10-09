from fastapi import APIRouter, Depends
from typing import Literal

from app.core.connections import get_pg_connection
from app.core.auth import get_current_user


router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("")
def get_alerts(current_user: dict = Depends(get_current_user)):
    """
    Return all alerts from PostgreSQL.

    AI analysis is already generated and stored when
    the alert is created by the detection engine.
    """

    with get_pg_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    threat_type,
                    severity,
                    source_ip,
                    message,
                    detected_at,
                    status,
                    ai_analysis
                FROM alerts
                ORDER BY detected_at DESC
                """
            )

            rows = cursor.fetchall()

    alerts = []

    for row in rows:
        alerts.append(
            {
                "id": row[0],
                "threat_type": row[1],
                "severity": row[2],
                "source_ip": row[3],
                "message": row[4],
                "detected_at": row[5],
                "status": row[6],
                "ai_analysis": row[7],
            }
        )

    return alerts


@router.patch("/{alert_id}")
def update_alert_status(
    alert_id: int,
    status: Literal["open", "investigating", "resolved"],
    current_user: dict = Depends(get_current_user),
):
    """
    Update the status of an existing alert.
    """

    with get_pg_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE alerts
                SET status = %s
                WHERE id = %s
                RETURNING
                    id,
                    threat_type,
                    severity,
                    source_ip,
                    message,
                    detected_at,
                    status,
                    ai_analysis
                """,
                (status, alert_id),
            )

            row = cursor.fetchone()

        conn.commit()

    if row is None:
        return {
            "error": "Alert not found"
        }

    return {
        "id": row[0],
        "threat_type": row[1],
        "severity": row[2],
        "source_ip": row[3],
        "message": row[4],
        "detected_at": row[5],
        "status": row[6],
        "ai_analysis": row[7],
    }