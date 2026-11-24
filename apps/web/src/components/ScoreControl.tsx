import { LIMITS } from "@cuadrillapp/protocol";
import { Minus, Plus, X } from "lucide-react";
import { copy } from "../copy";
import { clampQuarters, formatQuarters, scoreFace } from "../lib/format";
import { IconButton } from "./ui";

/** Score from 0 to 10 in 0.25 steps (internally quarters 0..40). */
export function ScoreControl({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number | null;
  onChange: (quarters: number | null) => void;
}) {
  const empty = value === null;
  const shown = value ?? LIMITS.maxQuarters / 2;
  return (
    <fieldset className="m-0 flex min-w-0 flex-col gap-1 border-0 p-0" aria-label={label}>
      <div className="flex items-center gap-2">
        <span className="text-3xl" aria-hidden>
          {scoreFace(value)}
        </span>
        <output className="min-w-[4.5ch] text-3xl font-bold tabular-nums" data-testid="score-value">
          {empty ? copy.noScore : formatQuarters(value)}
        </output>
        <div className="ml-auto flex gap-2">
          <IconButton
            label={copy.less}
            icon={Minus}
            tone="pink"
            disabled={empty || value === 0}
            onClick={() => onChange(clampQuarters((value ?? 0) - 1))}
          />
          <IconButton
            label={copy.more}
            icon={Plus}
            tone="mint"
            disabled={value === LIMITS.maxQuarters}
            onClick={() => onChange(clampQuarters(empty ? shown : value + 1))}
          />
          <IconButton
            label={copy.clear}
            icon={X}
            tone="paper"
            disabled={empty}
            onClick={() => onChange(null)}
          />
        </div>
      </div>
      <input
        type="range"
        className="score-range"
        data-empty={empty}
        min={0}
        max={LIMITS.maxQuarters}
        step={1}
        value={shown}
        aria-label={label}
        aria-valuetext={empty ? copy.noScore : formatQuarters(shown)}
        onChange={(event) => onChange(clampQuarters(Number(event.target.value)))}
      />
    </fieldset>
  );
}
