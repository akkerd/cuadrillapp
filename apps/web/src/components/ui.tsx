import type { LucideIcon } from "lucide-react";
import { X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import type { ButtonHTMLAttributes, ReactNode } from "react";
import { copy } from "../copy";
import { cx } from "../lib/format";
import { useStore } from "../store";

export type Tone = "sun" | "pink" | "mint" | "orange" | "paper" | "ink";

const tones: Record<Tone, string> = {
  sun: "bg-sun text-ink",
  pink: "bg-bubblegum text-ink",
  mint: "bg-mint text-ink",
  orange: "bg-tangerine text-ink",
  paper: "bg-paper text-ink",
  ink: "bg-ink text-paper",
};

const sizes = {
  sm: "min-h-11 px-3 text-base gap-1.5",
  md: "min-h-13 px-5 text-lg gap-2",
  lg: "min-h-16 px-6 text-2xl gap-3",
};

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  tone?: Tone;
  size?: keyof typeof sizes;
  icon?: LucideIcon;
  emoji?: string;
};

/** Botón "pegatina": borde de tinta y sombra dura que se hunde al pulsar. */
export function Button({
  tone = "sun",
  size = "md",
  icon: Icon,
  emoji,
  className,
  children,
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={cx(
        "inline-flex select-none items-center justify-center rounded-2xl border-[3px] border-ink font-semibold shadow-hard transition-transform active:translate-y-1 active:shadow-none disabled:cursor-not-allowed disabled:opacity-55 disabled:active:translate-y-0 disabled:active:shadow-hard",
        sizes[size],
        tones[tone],
        className,
      )}
      {...props}
    >
      {Icon && <Icon aria-hidden size={size === "lg" ? 28 : 22} strokeWidth={2.75} />}
      {emoji && <span aria-hidden>{emoji}</span>}
      {children}
    </button>
  );
}

type IconButtonProps = Omit<ButtonProps, "children"> & { label: string };

export function IconButton({ label, size = "sm", className, ...props }: IconButtonProps) {
  return (
    <Button
      aria-label={label}
      title={label}
      size={size}
      className={cx("aspect-square px-0", className)}
      {...props}
    />
  );
}

export function Card({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <section
      className={cx(
        "rounded-3xl border-[3px] border-ink bg-paper p-4 text-ink shadow-hard-lg",
        className,
      )}
    >
      {children}
    </section>
  );
}

export function CardTitle({ emoji, children }: { emoji: string; children: ReactNode }) {
  return (
    <h2 className="mb-3 flex items-center gap-2 text-xl font-bold">
      <span aria-hidden>{emoji}</span>
      {children}
    </h2>
  );
}

/** Hoja inferior modal. */
export function Sheet({
  open,
  onClose,
  title,
  children,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-40 flex items-end justify-center bg-ink/60"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-label={title}
            className="safe-area w-full max-w-lg rounded-t-[2rem] border-[3px] border-b-0 border-ink bg-paper text-ink"
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            exit={{ y: "100%" }}
            transition={{ type: "spring", damping: 26, stiffness: 320 }}
            onClick={(event) => event.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between gap-3">
              <h2 className="text-2xl font-bold">{title}</h2>
              <IconButton label={copy.close} icon={X} tone="paper" onClick={onClose} />
            </div>
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/** Confirmación de dos botones para acciones con consecuencias. */
export function ConfirmSheet({
  open,
  title,
  onConfirm,
  onClose,
  tone = "pink",
}: {
  open: boolean;
  title: string;
  onConfirm: () => void;
  onClose: () => void;
  tone?: Tone;
}) {
  return (
    <Sheet open={open} onClose={onClose} title={title}>
      <div className="grid grid-cols-2 gap-3">
        <Button tone="paper" onClick={onClose}>
          {copy.cancel}
        </Button>
        <Button
          tone={tone}
          onClick={() => {
            onClose();
            onConfirm();
          }}
        >
          {copy.confirm}
        </Button>
      </div>
    </Sheet>
  );
}

export function Toasts() {
  const toasts = useStore((s) => s.toasts);
  return (
    <div
      aria-live="polite"
      className="pointer-events-none fixed inset-x-0 bottom-0 z-50 flex flex-col items-center gap-2 pb-[max(env(safe-area-inset-bottom),20px)]"
    >
      <AnimatePresence>
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            role={toast.tone === "error" ? "alert" : "status"}
            initial={{ y: 30, opacity: 0, scale: 0.9 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: 20, opacity: 0 }}
            className={cx(
              "rounded-2xl border-[3px] border-ink px-4 py-2 text-lg font-semibold text-ink shadow-hard",
              toast.tone === "error" ? "bg-bubblegum" : "bg-sun",
            )}
          >
            {toast.text}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
