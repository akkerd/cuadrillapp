"""Exporta el contrato del protocolo para el frontend.

Uso: `python -m cuadrillapp.protocol.export <dir de packages/protocol>`

Escribe:
- `schema.json`: JSON Schema de comandos, respuestas y eventos (lo convierte a TS
  `json-schema-to-typescript` en `src/generated.ts`).
- `src/events.ts`: mapa tipado de eventos, códigos de error y literales.
- `src/constants.ts`: límites y catálogos del juego.
"""

import json
import sys
from pathlib import Path
from typing import Any, get_args

from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaMode, models_json_schema

from cuadrillapp import constants as k
from cuadrillapp.domain.errors import ErrorCode
from cuadrillapp.domain.models import Phase, Role, StartRequirement
from cuadrillapp.protocol.registry import COMMANDS, SERVER_EVENTS

BANNER = "// Generado por `make gen` desde apps/server. No editar a mano.\n"


class _NoFieldTitles(GenerateJsonSchema):
    """Sin `title` por campo: json-schema-to-typescript crearía un alias por cada uno."""

    def field_title_should_be_set(self, schema: Any) -> bool:
        return False


def build_schema() -> dict[str, Any]:
    entries: list[tuple[type[BaseModel], JsonSchemaMode]] = []
    seen: set[tuple[type[BaseModel], str]] = set()

    def add(model: type[BaseModel], mode: JsonSchemaMode) -> None:
        if (model, mode) not in seen:
            seen.add((model, mode))
            entries.append((model, mode))

    for command, result in COMMANDS.values():
        add(command, "validation")
        if result is not None:
            add(result, "serialization")
    for event in SERVER_EVENTS.values():
        add(event, "serialization")

    _, schema = models_json_schema(
        entries, title="CuadrillappProtocol", schema_generator=_NoFieldTitles
    )
    schema["type"] = "object"
    schema["additionalProperties"] = False
    return schema


def _union(values: tuple[object, ...]) -> str:
    return " | ".join(json.dumps(v) for v in values)


def build_events_ts() -> str:
    lines = [
        BANNER,
        'import type * as P from "./generated";',
        "",
        f"export type Role = {_union(get_args(Role))};",
        f"export type Phase = {_union(get_args(Phase))};",
        f"export type StartRequirement = {_union(get_args(StartRequirement))};",
        f"export type ErrorCode = {_union(get_args(ErrorCode))};",
        'export type ClientErrorCode = "TIMEOUT" | "DISCONNECTED";',
        "export type AnyErrorCode = ErrorCode | ClientErrorCode;",
        "",
        "export type Ack<T> = { ok: true; data: T } | { ok: false; error: AnyErrorCode };",
        "",
        "export interface ClientCommands {",
    ]
    for event, (command, result) in COMMANDS.items():
        data = f"P.{result.__name__}" if result is not None else "null"
        lines.append(f'  "{event}": {{ payload: P.{command.__name__}; data: {data} }};')
    lines += ["}", "", "export interface ServerEvents {"]
    for event, model in SERVER_EVENTS.items():
        lines.append(f'  "{event}": P.{model.__name__};')
    lines += [
        "}",
        "",
        f"export const ERROR_CODES: readonly ErrorCode[] = [{', '.join(json.dumps(e) for e in get_args(ErrorCode))}];",  # noqa: E501
        "",
    ]
    return "\n".join(lines)


def _dump(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def build_constants_ts() -> str:
    limits = {
        "maxParticipants": k.MAX_PARTICIPANTS,
        "maxCategories": k.MAX_CATEGORIES,
        "nameMaxLength": k.NAME_MAX_LENGTH,
        "titleMaxLength": k.TITLE_MAX_LENGTH,
        "categoryNameMaxLength": k.CATEGORY_NAME_MAX_LENGTH,
        "codeLength": k.CODE_LENGTH,
        "maxQuarters": k.MAX_QUARTERS,
        "quartersPerPoint": k.QUARTERS_PER_POINT,
    }
    suggestions = [{"emoji": e, "name": n} for e, n in k.CATEGORY_SUGGESTIONS]
    return "\n".join(
        [
            BANNER,
            f"export const LIMITS = {_dump(limits)} as const;",
            "",
            f"export const DEFAULT_TITLE = {json.dumps(k.DEFAULT_TITLE)};",
            f"export const CODE_ALPHABET = {json.dumps(k.CODE_ALPHABET)};",
            "",
            f"export const EMOJIS: readonly string[] = {_dump(list(k.EMOJIS))};",
            "",
            f"export const CATEGORY_SUGGESTIONS: readonly {{ emoji: string; name: string }}[] = "
            f"{_dump(suggestions)};",
            "",
        ]
    )


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        raise SystemExit("usage: python -m cuadrillapp.protocol.export <packages/protocol>")
    root = Path(argv[1])
    (root / "src").mkdir(parents=True, exist_ok=True)
    schema = json.dumps(build_schema(), ensure_ascii=False, indent=2, sort_keys=True)
    (root / "schema.json").write_text(schema + "\n", encoding="utf-8")
    (root / "src" / "events.ts").write_text(build_events_ts(), encoding="utf-8")
    (root / "src" / "constants.ts").write_text(build_constants_ts(), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv)
