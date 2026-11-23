import { cx, toneFor } from "../lib/format";

const sizes = {
  sm: "size-10 text-2xl",
  md: "size-14 text-3xl",
  lg: "size-24 text-6xl",
  xl: "size-32 text-7xl",
};

export function Avatar({
  emoji,
  seed,
  size = "md",
  dimmed = false,
  className,
}: {
  emoji: string;
  seed: string;
  size?: keyof typeof sizes;
  dimmed?: boolean;
  className?: string;
}) {
  return (
    <span
      aria-hidden
      className={cx(
        "grid shrink-0 place-items-center rounded-full border-[3px] border-ink shadow-hard-sm",
        toneFor(seed),
        sizes[size],
        dimmed && "opacity-45 grayscale",
        className,
      )}
    >
      <span className="leading-none">{emoji}</span>
    </span>
  );
}
