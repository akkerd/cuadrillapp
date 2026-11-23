"""Configuración común de los modelos del protocolo (JSON en camelCase)."""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Incoming(BaseModel):
    """Datos que envía el cliente: estrictos, sin campos extra, inmutables."""

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
    """Datos que envía el servidor."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
        frozen=True,
        json_schema_serialization_defaults_required=True,
    )
