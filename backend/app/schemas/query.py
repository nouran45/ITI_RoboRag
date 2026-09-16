from pydantic import BaseModel, Field, ConfigDict


class QueryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User question about the robotics course documents",
    )


class SourceItem(BaseModel):
    source: str
    page: int
    distance: float | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceItem]