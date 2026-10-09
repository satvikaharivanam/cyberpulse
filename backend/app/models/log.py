from datetime import datetime
from pydantic import BaseModel, Field


class SecurityLog(BaseModel):
    timestamp: datetime
    source: str
    source_ip: str
    destination_ip: str | None = None
    destination_port: int | None = None
    event_type: str
    severity: str = Field(pattern="^(low|medium|high|critical)$")
    message: str

    