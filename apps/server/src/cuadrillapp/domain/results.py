"""Cálculo de resultados con fracciones exactas."""

from collections.abc import Iterable
from fractions import Fraction

from cuadrillapp.constants import QUARTERS_PER_POINT
from cuadrillapp.domain.models import (
    CategoryResult,
    Participant,
    RankEntry,
    Results,
    Room,
)

type Scored = tuple[Participant, Fraction | None, int]


def rank(items: Iterable[Scored]) -> tuple[RankEntry, ...]:
    """Ordena de mayor a menor; los empates comparten posición (1, 1, 3).

    Quien no tiene nota queda al final sin posición. El orden de llegada desempata
    solo la presentación, nunca la posición.
    """
    items = list(items)
    scored = sorted(
        (item for item in items if item[1] is not None),
        key=lambda item: item[1] or Fraction(0),
        reverse=True,
    )
    entries: list[RankEntry] = []
    previous: Fraction | None = None
    position = 0
    for index, (participant, score, count) in enumerate(scored, start=1):
        if score != previous:
            position = index
            previous = score
        entries.append(_entry(participant, score, count, position))
    entries.extend(_entry(p, None, count, None) for p, score, count in items if score is None)
    return tuple(entries)


def _entry(p: Participant, score: Fraction | None, count: int, position: int | None) -> RankEntry:
    return RankEntry(p.id, p.name, p.emoji, score, count, position)


def compute_results(room: Room) -> Results:
    candidates = room.candidates()
    category_means: dict[str, list[Fraction]] = {c.id: [] for c in candidates}
    totals: dict[str, int] = {c.id: 0 for c in candidates}
    by_category: list[CategoryResult] = []

    for category in room.categories:
        rows: list[Scored] = []
        for candidate in candidates:
            values = [
                quarters
                for (_voter, candidate_id, category_id), quarters in room.scores.items()
                if candidate_id == candidate.id and category_id == category.id
            ]
            mean = Fraction(sum(values), QUARTERS_PER_POINT * len(values)) if values else None
            if mean is not None:
                category_means[candidate.id].append(mean)
            totals[candidate.id] += len(values)
            rows.append((candidate, mean, len(values)))
        by_category.append(CategoryResult(category.id, category.emoji, category.name, rank(rows)))

    overall: list[Scored] = []
    for candidate in candidates:
        means = category_means[candidate.id]
        final = sum(means, Fraction(0)) / len(means) if means else None
        overall.append((candidate, final, totals[candidate.id]))

    return Results(overall=rank(overall), by_category=tuple(by_category))
