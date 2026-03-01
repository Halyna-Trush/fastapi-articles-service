from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ArticleCreate(BaseModel):
    """
    Payload used to create a new article.
    """

    title: str = Field(
        ...,
        description="Article title",
    )
    content: str = Field(
        ...,
        description="Article content",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Hello FastAPI",
                "content": "My first article content",
            }
        }
    )


class ArticleRead(BaseModel):
    """
    Article returned by API.
    """

    id: int
    title: str
    content: str
    owner_id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Hello FastAPI",
                "content": "My first article content",
                "owner_id": 1,
            }
        },
    )


class ArticleReplace(BaseModel):
    """
    Full update (PUT).
    """

    title: str = Field(
        ...,
        description="New article title",
    )
    content: str = Field(
        ...,
        description="New article content",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated title",
                "content": "Updated content",
            }
        }
    )


class ArticleUpdate(BaseModel):
    """
    Partial update (PATCH).
    """

    title: Optional[str] = Field(
        default=None,
        description="Update article title",
    )
    content: Optional[str] = Field(
        default=None,
        description="Update article content",
    )