from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Selection(StrictModel):
    unit_id: str = Field(min_length=1, max_length=200)
    start: int | None = Field(default=None, ge=0)
    end: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_span(self):
        if (self.start is None) != (self.end is None):
            raise ValueError("Provide both start and end or neither")
        if self.start is not None and self.start >= self.end:
            raise ValueError("Selection must have start < end")
        return self


class Query(StrictModel):
    question: str = Field(min_length=1, max_length=4000)
    mode: Literal["STRICT_SOURCE", "LESSON_EXPANDED"] = "STRICT_SOURCE"
    snapshot_id: str = Field(min_length=1, max_length=100)
    lesson_id: str | None = Field(default=None, max_length=100)
    selections: list[Selection] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def validate_scope(self):
        if not self.question.strip():
            raise ValueError("Question cannot be blank")
        if self.mode == "STRICT_SOURCE" and not self.selections:
            raise ValueError("STRICT_SOURCE requires at least one source selection")
        if self.mode == "LESSON_EXPANDED" and not self.lesson_id:
            raise ValueError("LESSON_EXPANDED requires lesson_id")
        if len({x.unit_id for x in self.selections}) != len(self.selections):
            raise ValueError("Duplicate source selections")
        return self


class RouteDecision(StrictModel):
    status: Literal["CLEAR", "AMBIGUOUS", "OUT_OF_SCOPE"]
    reason: str


class EvidenceLink(StrictModel):
    evidence_id: str
    quote: str = Field(min_length=1)


class Claim(StrictModel):
    text: str = Field(min_length=1)
    evidence: list[EvidenceLink] = Field(min_length=1)


class GroundingDecision(StrictModel):
    supported: bool
    reason: str
    evidence_ids: list[str]


class Draft(StrictModel):
    claims: list[Claim] = Field(min_length=1, max_length=12)


class Validation(StrictModel):
    supported: bool
    complete: bool
    reason: str


class Ranking(StrictModel):
    evidence_ids: list[str]
