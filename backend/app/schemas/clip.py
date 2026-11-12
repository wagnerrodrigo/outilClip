from typing import ClassVar, Self

from pydantic import BaseModel, Field, model_validator


class ClipCandidate(BaseModel):
    title: str
    start: float = Field(ge=0)
    end: float = Field(ge=0)
    score: float = Field(ge=0, le=10)
    reason: str

    # Hard sanity bound only: the usable range comes from Settings
    # (CLIP_MIN_SEC / CLIP_MAX_SEC) and is enforced when parsing candidates.
    MAX_DURATION_SEC: ClassVar[float] = 1800.0

    @model_validator(mode="after")
    def validate_duration(self) -> Self:
        duration = self.end - self.start
        if duration <= 0:
            raise ValueError("end must be greater than start")
        if duration > self.MAX_DURATION_SEC:
            raise ValueError(
                f"clip duration {duration:.1f}s exceeds {self.MAX_DURATION_SEC:.0f}s"
            )
        return self


class ClipSelectionRequest(BaseModel):
    transcript: list
    scenes: list
    duration_sec: float
    language: str = "en"
    num_clips: int = Field(default=10, ge=1, le=20)
    min_clip_sec: float = Field(default=30, ge=1, le=1800)
    max_clip_sec: float = Field(default=90, ge=1, le=1800)

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.max_clip_sec < self.min_clip_sec:
            raise ValueError("max_clip_sec must be greater than or equal to min_clip_sec")
        return self


class ClipRecordResponse(BaseModel):
    id: str
    index: int
    title: str
    start_sec: float
    end_sec: float
    score: float
    reason: str
    status: str
    output_path: str | None = None
    thumbnail_path: str | None = None
