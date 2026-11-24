"""Shared configuration for protocol models (camelCase JSON)."""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Incoming(BaseModel):
    """Data sent by the client: strict, no extra fields, immutable."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
        extra="forbid",
        frozen=True,
        strict=True,
    )


class Outgoing(BaseModel):
    """Data sent by the server."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
        frozen=True,
        json_schema_serialization_defaults_required=True,
    )
