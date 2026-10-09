from fastapi import APIRouter, Depends

from app.models.log import SecurityLog
from app.core.connections import es, redis_client
from app.core.auth import get_current_user

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.post("")
def ingest_log(log: SecurityLog, 
            current_user: dict = Depends(get_current_user),):
    document = log.model_dump(mode="json")

    # Redis Streams do not accept None values.
    # Remove optional fields that are missing.
    document = {
        key: value
        for key, value in document.items()
        if value is not None
    }

    # Store the log in Elasticsearch
    response = es.index(
        index="security-logs",
        document=document,
    )

    # Publish the log to Redis Stream
    redis_client.xadd(
        "security-events",
        document,
    )

    return {
        "status": "ingested",
        "id": response["_id"],
        "index": response["_index"],
    }