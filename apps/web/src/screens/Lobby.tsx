import type { RoomSnapshot } from "@cuadrillapp/protocol";
import { Play } from "lucide-react";
import { motion } from "motion/react";
import { CategoriesCard } from "../components/Categories";
import { PlayersCard } from "../components/Participants";
import { RoomHeader } from "../components/RoomHeader";
import { ShareCard } from "../components/ShareCard";
import { Button } from "../components/ui";
import { copy } from "../copy";
import { act } from "../lib/socket";

export function Lobby({ snapshot }: { snapshot: RoomSnapshot }) {
  const { ready, missing } = snapshot.startCheck;
  return (
    <main className="safe-area mx-auto flex min-h-dvh max-w-lg flex-col gap-4 pb-44">
      <RoomHeader snapshot={snapshot} />
      <ShareCard code={snapshot.code} />
      <PlayersCard snapshot={snapshot} />
      <CategoriesCard snapshot={snapshot} />

      <footer className="fixed inset-x-0 bottom-0 z-30 mx-auto bg-linear-to-t from-plum from-55% to-transparent pt-8 max-w-lg px-4 pb-[max(env(safe-area-inset-bottom),16px)]">
        {snapshot.me.isAdmin ? (
          <div className="flex flex-col gap-2">
            {!ready && (
              <ul className="flex flex-wrap justify-center gap-2" aria-label="Falta">
                {missing.map((item) => (
                  <li
                    key={item}
                    className="rounded-full border-2 border-ink bg-paper px-3 py-0.5 text-sm font-semibold text-ink"
                  >
                    {copy.missing[item]}
                  </li>
                ))}
              </ul>
            )}
            <Button
              size="lg"
              icon={Play}
              disabled={!ready}
              className="w-full"
              onClick={() => void act("voting:start", {})}
            >
              {copy.vote}
            </Button>
          </div>
        ) : (
          <p className="flex items-center justify-center gap-2 rounded-2xl border-[3px] border-ink bg-paper py-3 text-lg font-semibold text-ink shadow-hard">
            <motion.span
              aria-hidden
              animate={{ rotate: [0, -12, 12, 0] }}
              transition={{ repeat: Number.POSITIVE_INFINITY, duration: 1.6 }}
            >
              ⏳
            </motion.span>
            {copy.waitingAdmin}
          </p>
        )}
      </footer>
    </main>
  );
}
