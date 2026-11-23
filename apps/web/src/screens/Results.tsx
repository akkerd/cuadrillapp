import type { RankEntryView, RoomSnapshot } from "@cuadrillapp/protocol";
import { RotateCcw, Undo2 } from "lucide-react";
import { motion, useReducedMotion } from "motion/react";
import { useEffect, useState } from "react";
import { Avatar } from "../components/Avatar";
import { RoomHeader } from "../components/RoomHeader";
import { Button, Card, ConfirmSheet } from "../components/ui";
import { copy } from "../copy";
import { cx, formatPoints } from "../lib/format";
import { act } from "../lib/socket";

const PODIUM = [
  { place: 2, height: "h-28", tone: "bg-paper", delay: 1.2, medal: "🥈" },
  { place: 1, height: "h-40", tone: "bg-sun", delay: 2.2, medal: "🥇" },
  { place: 3, height: "h-20", tone: "bg-tangerine", delay: 0.4, medal: "🥉" },
] as const;

export function Results({ snapshot }: { snapshot: RoomSnapshot }) {
  const results = snapshot.results;
  const [tab, setTab] = useState<string>("overall");
  const [again, setAgain] = useState(false);
  if (!results) return null;
  const entries =
    tab === "overall"
      ? results.overall
      : (results.byCategory.find((c) => c.categoryId === tab)?.entries ?? results.overall);

  return (
    <main className="safe-area mx-auto flex min-h-dvh max-w-lg flex-col gap-4 pb-32">
      <RoomHeader snapshot={snapshot} />
      <Podium entries={results.overall} />

      <div className="flex gap-2 overflow-x-auto pb-1" role="tablist">
        {[
          { id: "overall", label: `🏆 ${copy.overall}` },
          ...results.byCategory.map((c) => ({ id: c.categoryId, label: `${c.emoji} ${c.name}` })),
        ].map((t) => (
          <button
            key={t.id}
            type="button"
            role="tab"
            aria-selected={tab === t.id}
            onClick={() => setTab(t.id)}
            className={cx(
              "shrink-0 rounded-full border-[3px] border-ink px-4 py-1.5 text-lg font-semibold text-ink",
              tab === t.id ? "bg-sun shadow-hard-sm" : "bg-paper/80",
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      <Card>
        <ol className="grid gap-2" aria-label={copy.overall}>
          {entries.map((entry) => (
            <li key={entry.candidateId} className="flex items-center gap-3">
              <span className="w-8 text-center text-2xl font-bold tabular-nums">
                {medal(entry.position)}
              </span>
              <Avatar emoji={entry.emoji} seed={entry.candidateId} size="sm" />
              <span className="min-w-0 flex-1 truncate text-lg font-semibold">{entry.name}</span>
              <span className="text-right">
                <span className="block text-xl font-bold tabular-nums" data-testid="result-score">
                  {entry.score === null ? copy.noVotes : formatPoints(entry.score)}
                </span>
                <span className="block text-sm text-ink/60">{copy.votes(entry.count)}</span>
              </span>
            </li>
          ))}
        </ol>
      </Card>

      {snapshot.me.isAdmin && (
        <footer className="fixed inset-x-0 bottom-0 z-30 mx-auto bg-linear-to-t from-plum from-55% to-transparent pt-8 grid max-w-lg grid-cols-2 gap-3 px-4 pb-[max(env(safe-area-inset-bottom),16px)]">
          <Button tone="paper" icon={Undo2} onClick={() => void act("voting:reopen", {})}>
            {copy.reopen}
          </Button>
          <Button tone="mint" icon={RotateCcw} onClick={() => setAgain(true)}>
            {copy.again}
          </Button>
        </footer>
      )}
      <ConfirmSheet
        open={again}
        title={copy.againConfirm}
        onClose={() => setAgain(false)}
        onConfirm={() => void act("round:new", {})}
      />
    </main>
  );
}

function medal(position: number | null): string {
  if (position === null) return "·";
  return ["🥇", "🥈", "🥉"][position - 1] ?? String(position);
}

function Podium({ entries }: { entries: RankEntryView[] }) {
  const reduce = useReducedMotion() ?? false;
  const ranked = entries.filter((e) => e.position !== null).slice(0, 3);

  useEffect(() => {
    if (reduce || ranked.length === 0) return;
    const timer = window.setTimeout(async () => {
      const { default: confetti } = await import("canvas-confetti");
      void confetti({
        particleCount: 160,
        spread: 90,
        origin: { y: 0.55 },
        colors: ["#FFD23F", "#FF5FA2", "#22C9B7", "#FF8A3D", "#FFF9EE"],
        disableForReducedMotion: true,
      });
    }, 2500);
    return () => window.clearTimeout(timer);
  }, [reduce, ranked.length]);

  return (
    <section className="grid grid-cols-3 items-end gap-2 pt-4" aria-label="Podio">
      {PODIUM.map(({ place, height, tone, delay, medal: icon }) => {
        const entry = ranked[place - 1];
        return (
          <motion.div
            key={place}
            className="flex flex-col items-center gap-1"
            initial={reduce ? false : { y: 80, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: reduce ? 0 : delay, type: "spring", stiffness: 220, damping: 14 }}
          >
            {entry && (
              <>
                <Avatar
                  emoji={entry.emoji}
                  seed={entry.candidateId}
                  size={place === 1 ? "lg" : "md"}
                />
                <span className="max-w-full truncate text-lg font-bold">{entry.name}</span>
                <span className="text-sm font-semibold tabular-nums">
                  {entry.score === null ? "" : formatPoints(entry.score)}
                </span>
              </>
            )}
            <div
              className={cx(
                "grid w-full place-items-center rounded-t-2xl border-[3px] border-b-0 border-ink text-4xl text-ink",
                height,
                tone,
              )}
            >
              <span role="img" aria-label={`Puesto ${place}`}>
                {icon}
              </span>
            </div>
          </motion.div>
        );
      })}
    </section>
  );
}
