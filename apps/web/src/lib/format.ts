import { CODE_ALPHABET, LIMITS } from "@cuadrillapp/protocol";

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
