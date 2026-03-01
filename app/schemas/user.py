from pydantic import BaseModel, ConfigDict, Field


class UserRead(BaseModel):
    """
    Public user representation returned by API.
    """

    id: int = Field(example=1)
    email: str = Field(example="admin@example.com")
    role: str = Field(example="admin")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "admin@example.com",
                "role": "admin",
            }
        },
    )


class UserRoleUpdate(BaseModel):
    """
    Payload used by admin to update user role.
    """

    role: str = Field(
        example="editor",
        description="New role for user: user | editor | admin",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "editor"
            }
        }
    )