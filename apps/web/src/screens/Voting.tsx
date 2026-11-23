import type { ParticipantView, RoomSnapshot } from "@cuadrillapp/protocol";
import { BarChart3, Check, Eye } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Avatar } from "../components/Avatar";
import { ParticipantRow } from "../components/Participants";
import { RoomHeader } from "../components/RoomHeader";
import { ScoreControl } from "../components/ScoreControl";
import { Button, Card, ConfirmSheet, IconButton, Sheet } from "../components/ui";
import { copy } from "../copy";
import { cx } from "../lib/format";
import { act } from "../lib/socket";

type Pending = Record<string, number | null>;

export function Voting({ snapshot }: { snapshot: RoomSnapshot }) {
  const meId = snapshot.me.participantId;
  const isAdmin = snapshot.me.isAdmin;
  const manual = snapshot.participants.filter((p) => p.isManual);
  const [asId, setAsId] = useState<string | null>(null);
  const [revealing, setRevealing] = useState(false);
  const [showProgress, setShowProgress] = useState(false);
  const scores = useScores(snapshot, asId);

  // Si el participante representado desaparece o dejo de ser admin, vuelvo a votar como yo.
  useEffect(() => {
    if (asId && (!isAdmin || !manual.some((p) => p.id === asId))) setAsId(null);
  }, [asId, isAdmin, manual]);

  const voterId = asId ?? meId;
  const voter = snapshot.participants.find((p) => p.id === voterId);
  const progress = asId ? voter?.progress : snapshot.me.progress;
  const candidates = snapshot.participants.filter(
    (p) => p.role === "candidate" && p.id !== voterId,
  );

  return (
    <main className="safe-area mx-auto flex min-h-dvh max-w-lg flex-col gap-4 pb-32">
      <RoomHeader
        snapshot={snapshot}
        extra={
          isAdmin && (
            <IconButton
              label={copy.progress}
              icon={BarChart3}
              tone="mint"
              onClick={() => setShowProgress(true)}
            />
          )
        }
      />

      <DoneStrip participants={snapshot.participants} />

      {isAdmin && manual.length > 0 && (
        <div
          className="flex flex-wrap items-center gap-2"
          role="radiogroup"
          aria-label={copy.voteAs}
        >
          <span className="font-semibold">{copy.voteAs}</span>
          {[null, ...manual].map((p) => (
            <button
              key={p?.id ?? "me"}
              type="button"
              role="radio"
              aria-checked={asId === (p?.id ?? null)}
              onClick={() => setAsId(p?.id ?? null)}
              className={cx(
                "rounded-full border-[3px] border-ink px-3 py-1 text-lg font-semibold text-ink",
                asId === (p?.id ?? null) ? "bg-sun shadow-hard-sm" : "bg-paper/80",
              )}
            >
              {p ? `${p.emoji} ${p.name}` : `🙋 ${copy.myself}`}
            </button>
          ))}
        </div>
      )}

      {candidates.length === 0 && (
        <Card>
          <p className="text-center text-xl font-semibold">{copy.nobodyToVote}</p>
        </Card>
      )}

      {candidates.map((candidate, index) => (
        <Card key={candidate.id} className={index % 2 ? "rotate-[0.5deg]" : "-rotate-[0.5deg]"}>
          <div className="mb-3 flex items-center gap-3">
            <Avatar emoji={candidate.emoji} seed={candidate.id} size="md" />
            <h2 className="truncate text-2xl font-bold">{candidate.name}</h2>
          </div>
          <div className="grid gap-4">
            {snapshot.categories.map((category) => (
              <div key={category.id}>
                <p className="text-lg font-semibold">
                  <span aria-hidden>{category.emoji}</span> {category.name}
                </p>
                <ScoreControl
                  label={`${category.name} · ${candidate.name}`}
                  value={scores.get(candidate.id, category.id)}
                  onChange={(quarters) => scores.set(candidate.id, category.id, quarters)}
                />
              </div>
            ))}
          </div>
        </Card>
      ))}

      <footer className="fixed inset-x-0 bottom-0 z-30 mx-auto bg-linear-to-t from-plum from-55% to-transparent pt-8 flex max-w-lg gap-3 px-4 pb-[max(env(safe-area-inset-bottom),16px)]">
        {progress && (
          <span className="flex items-center rounded-2xl border-[3px] border-ink bg-paper px-3 text-lg font-bold text-ink shadow-hard tabular-nums">
            {progress.given}/{progress.total}
          </span>
        )}
        <Button
          className="flex-1"
          tone={voter?.done ? "paper" : "mint"}
          icon={Check}
          aria-pressed={voter?.done ?? false}
          onClick={() =>
            void act("voter:done", { done: !voter?.done, asParticipantId: asId ?? undefined })
          }
        >
          {voter?.done ? copy.notDone : copy.done}
        </Button>
        {isAdmin && (
          <Button tone="pink" icon={Eye} onClick={() => setRevealing(true)}>
            {copy.reveal}
          </Button>
        )}
      </footer>

      <ConfirmSheet
        open={revealing}
        title={copy.revealConfirm}
        tone="sun"
        onClose={() => setRevealing(false)}
        onConfirm={() => void act("voting:reveal", {})}
      />

      <Sheet
        open={showProgress}
        onClose={() => setShowProgress(false)}
        title={`📊 ${copy.progress}`}
      >
        <ul className="grid max-h-[60dvh] gap-1 overflow-y-auto">
          {snapshot.participants.map((p) => (
            <ParticipantRow
              key={p.id}
              participant={p}
              isMe={p.id === meId}
              trailing={
                <span className="font-bold tabular-nums">
                  {p.done ? "✅ " : ""}
                  {p.progress ? `${p.progress.given}/${p.progress.total}` : ""}
                </span>
              }
            />
          ))}
        </ul>
      </Sheet>
    </main>
  );
}

function DoneStrip({ participants }: { participants: ParticipantView[] }) {
  return (
    <ul className="flex flex-wrap gap-2" aria-label={copy.done}>
      {participants.map((p) => (
        <li key={p.id} className="relative" title={p.name}>
          <Avatar emoji={p.emoji} seed={p.id} size="sm" dimmed={!p.done} />
          {p.done && (
            <span
              role="img"
              aria-label={`${p.name} ${copy.done}`}
              className="absolute -bottom-1 -right-1 grid size-5 place-items-center rounded-full border-2 border-ink bg-mint text-xs"
            >
              ✓
            </span>
          )}
        </li>
      ))}
    </ul>
  );
}

/** Notas del votante actual con actualización optimista y envío agrupado. */
function useScores(snapshot: RoomSnapshot, asId: string | null) {
  const [pending, setPending] = useState<Pending>({});
  const timers = useRef(new Map<string, number>());
  const sequence = useRef(new Map<string, number>());
  const voterId = asId ?? snapshot.me.participantId;
  const source = asId ? snapshot.proxyScores.filter((s) => s.voterId === asId) : snapshot.myScores;
  const server = new Map(source.map((s) => [`${s.candidateId}:${s.categoryId}`, s.quarters]));

  useEffect(() => {
    const pendingTimers = timers.current;
    return () => {
      for (const timer of pendingTimers.values()) window.clearTimeout(timer);
    };
  }, []);

  return {
    get(candidateId: string, categoryId: string): number | null {
      const key = `${voterId}:${candidateId}:${categoryId}`;
      if (key in pending) return pending[key] ?? null;
      return server.get(`${candidateId}:${categoryId}`) ?? null;
    },
    set(candidateId: string, categoryId: string, quarters: number | null) {
      const key = `${voterId}:${candidateId}:${categoryId}`;
      const seq = (sequence.current.get(key) ?? 0) + 1;
      sequence.current.set(key, seq);
      setPending((p) => ({ ...p, [key]: quarters }));
      window.clearTimeout(timers.current.get(key));
      timers.current.set(
        key,
        window.setTimeout(async () => {
          await act("score:set", {
            candidateId,
            categoryId,
            quarters,
            asParticipantId: asId ?? undefined,
          });
          if (sequence.current.get(key) === seq) {
            setPending(({ [key]: _, ...rest }) => rest);
          }
        }, 150),
      );
    },
  };
}
