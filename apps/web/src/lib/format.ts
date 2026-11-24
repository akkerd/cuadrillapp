import { CODE_ALPHABET, LIMITS } from "@cuadrillapp/protocol";

const scoreFormat = new Intl.NumberFormat("es-ES", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/** 29 quarters → "7,25" */
export function formatQuarters(quarters: number): string {
  return scoreFormat.format(quarters / LIMITS.quartersPerPoint);
}

export function clampQuarters(quarters: number): number {
  return Math.min(LIMITS.maxQuarters, Math.max(0, Math.round(quarters)));
}

/** Emoji shown next to a score. */
export function scoreFace(quarters: number | null): string {
  if (quarters === null) return "🤔";
  const points = quarters / LIMITS.quartersPerPoint;
  if (points < 2) return "😭";
  if (points < 4) return "😕";
  if (points < 6) return "😐";
  if (points < 8) return "🙂";
  if (points < 9.5) return "😄";
  return "🤩";
}

/** " abc23 " → "ABC23" */
export function normalizeCode(raw: string): string {
  return raw.replace(/\s+/g, "").toUpperCase();
}

export function isValidCode(code: string): boolean {
  return code.length === LIMITS.codeLength && [...code].every((ch) => CODE_ALPHABET.includes(ch));
}

export function roomLink(code: string): string {
  return `${window.location.origin}/r/${code}`;
}

export function cx(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

const TONES = ["bg-sun", "bg-bubblegum", "bg-mint", "bg-tangerine", "bg-paper"] as const;

/** Stable avatar colour per participant. */
export function toneFor(id: string): (typeof TONES)[number] {
  let hash = 0;
  for (const ch of id) hash = (hash * 31 + ch.charCodeAt(0)) >>> 0;
  return TONES[hash % TONES.length] ?? "bg-sun";
}
