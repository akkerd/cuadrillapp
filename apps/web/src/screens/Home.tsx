import { motion } from "motion/react";
import { copy } from "../copy";

const STICKERS = ["🦄", "🌮", "🐸", "🤠", "👽"];

export function Home() {
  return (
    <main className="safe-area mx-auto flex min-h-dvh max-w-lg flex-col">
      <div className="flex flex-1 flex-col items-center justify-center gap-6 py-8 text-center">
        <div className="flex gap-1 text-5xl" aria-hidden>
          {STICKERS.map((emoji, index) => (
            <motion.span
              key={emoji}
              initial={{ y: -40, opacity: 0, rotate: 0 }}
              animate={{ y: 0, opacity: 1, rotate: index % 2 ? 10 : -10 }}
              transition={{ delay: index * 0.08, type: "spring", stiffness: 300, damping: 12 }}
            >
              {emoji}
            </motion.span>
          ))}
        </div>
        <h1 className="-rotate-2 rounded-3xl border-[3px] border-ink bg-sun px-6 py-3 text-5xl font-bold text-ink shadow-hard-lg">
          {copy.app}
        </h1>
        <p className="text-2xl font-medium">{copy.tagline}</p>
      </div>
    </main>
  );
}
