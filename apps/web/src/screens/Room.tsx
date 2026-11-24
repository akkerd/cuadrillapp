import type { PeekResult } from "@cuadrillapp/protocol";
import { Home as HomeIcon } from "lucide-react";
import { motion } from "motion/react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { ProfileForm } from "../components/ProfileForm";
import { Button, Card } from "../components/ui";
import { copy, errorText } from "../copy";
import { normalizeCode } from "../lib/format";
import { forgetRoom, rememberSeat } from "../lib/session";
import { act, rejoin, send, setActiveRoom } from "../lib/socket";
import { storage } from "../lib/storage";
import { useStore } from "../store";
import { defaultProfile, Screen } from "./Create";
import { Lobby } from "./Lobby";
import { Results } from "./Results";
import { Voting } from "./Voting";

export function RoomScreen() {
  const navigate = useNavigate();
  const code = normalizeCode(useParams().code ?? "");
  const snapshot = useStore((s) => (s.snapshot?.code === code ? s.snapshot : null));
  const exit = useStore((s) => (s.exit?.code === code ? s.exit : null));
  const online = useStore((s) => s.connection === "online");
  const [peek, setPeek] = useState<PeekResult | "missing" | null>(null);
  const hasSeat = storage.getSeat(code) !== null;
  const inRoom = snapshot !== null;

  useEffect(() => {
    setActiveRoom(code);
    return () => setActiveRoom(null);
  }, [code]);

  useEffect(() => {
    if (!online || inRoom || exit) return;
    if (hasSeat) {
      void rejoin(code);
      return;
    }
    void send("room:peek", { code }).then((result) => setPeek(result.ok ? result.data : "missing"));
  }, [online, inRoom, exit, hasSeat, code]);

  const goHome = () => {
    forgetRoom(code);
    navigate("/");
  };

  if (exit) return <Gone text={copy.gone[exit.reason]} onHome={goHome} />;
  if (snapshot?.phase === "lobby") return <Lobby snapshot={snapshot} />;
  if (snapshot?.phase === "voting") return <Voting snapshot={snapshot} />;
  if (snapshot?.phase === "results") return <Results snapshot={snapshot} />;
  if (peek === "missing") return <Gone text={errorText.ROOM_NOT_FOUND} onHome={goHome} />;
  if (hasSeat || peek === null) return <Loading />;

  return (
    <Screen title={`🎪 ${peek.title}`} onBack={() => navigate("/")}>
      <Card>
        <ProfileForm
          initial={defaultProfile()}
          submitLabel={copy.go}
          onSubmit={async (profile) => {
            storage.saveProfile(profile);
            const data = await act("room:join", { ...profile, code });
            if (data) rememberSeat(data);
          }}
        />
      </Card>
    </Screen>
  );
}

function Loading() {
  return (
    <main className="grid min-h-dvh place-items-center" aria-busy="true">
      <motion.span
        className="text-7xl"
        aria-hidden
        animate={{ rotate: 360 }}
        transition={{ repeat: Number.POSITIVE_INFINITY, duration: 1.2, ease: "linear" }}
      >
        🌀
      </motion.span>
    </main>
  );
}

export function Gone({ text, onHome }: { text: string; onHome: () => void }) {
  return (
    <main className="safe-area mx-auto flex min-h-dvh max-w-lg flex-col items-center justify-center gap-8 text-center">
      <p className="rotate-[-3deg] rounded-3xl border-[3px] border-ink bg-paper px-6 py-4 text-4xl font-bold text-ink shadow-hard-lg">
        {text}
      </p>
      <Button size="lg" icon={HomeIcon} onClick={onHome}>
        {copy.home}
      </Button>
    </main>
  );
}
