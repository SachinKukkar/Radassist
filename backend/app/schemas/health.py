from typing import Literal

from pydantic import BaseModel, Field


class LivenessResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str


class ReadinessResponse(BaseModel):
    status: Literal["ok", "degraded"] = "ok"
    checks: dict[str, str] = Field(default_factory=dict)
