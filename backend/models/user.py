from datetime import datetime
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, GetJsonSchemaHandler
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Any,
    ) -> core_schema.CoreSchema:
        """
        Defines how Pydantic should handle the ObjectId type for validation and serialization.
        """

        def validate(value: str) -> ObjectId:
            if not ObjectId.is_valid(value):
                raise ValueError(f"Invalid ObjectId: {value}")
            return ObjectId(value)

        from_json_schema = core_schema.chain_schema(
            [core_schema.str_schema(), core_schema.no_info_plain_validator_function(validate)]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_json_schema,
            python_schema=core_schema.union_schema(
                [core_schema.is_instance_schema(ObjectId), from_json_schema]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        """
        Defines how the `PyObjectId` type should be represented in the JSON Schema.
        Compatability function for FastAPI autodoc generation.
        """
        # In the JSON schema (e.g., OpenAPI docs), represent ObjectId as a string.
        return handler(core_schema.str_schema())


class UserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    googleId: str
    email: str
    username: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": "high_entropy_id",
                "googleId": "12345678901234567890",
                "email": "user@example.com",
                "username": "user123",
                "createdAt": "2025-10-28T12:00:00Z",
                "updatedAt": "2025-10-28T12:00:00Z",
            }
        },
    )
