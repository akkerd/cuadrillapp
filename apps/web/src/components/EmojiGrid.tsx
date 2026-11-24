import { EMOJIS } from "@cuadrillapp/protocol";
import { cx } from "../lib/format";

export function EmojiGrid({
  value,
  onChange,
}: {
  value: string;
  onChange: (emoji: string) => void;
}) {
  return (
    <div className="grid max-h-56 grid-cols-6 gap-2 overflow-y-auto p-1" role="radiogroup">
      {EMOJIS.map((emoji) => (
        <button
          key={emoji}
          type="button"
          role="radio"
          aria-checked={emoji === value}
          aria-label={emoji}
          onClick={() => onChange(emoji)}
          className={cx(
            "grid aspect-square place-items-center rounded-2xl border-[3px] text-3xl transition-transform active:scale-90",
            emoji === value ? "border-ink bg-sun shadow-hard-sm" : "border-transparent bg-white/60",
          )}
        >
          {emoji}
        </button>
      ))}
    </div>
  );
}

export function randomEmoji(except?: string): string {
  const options = EMOJIS.filter((e) => e !== except);
  return options[Math.floor(Math.random() * options.length)] ?? "🦄";
}
