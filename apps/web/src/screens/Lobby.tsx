import type { RoomSnapshot } from "@cuadrillapp/protocol";
import { PlayersCard } from "../components/Participants";
import { RoomHeader } from "../components/RoomHeader";
import { ShareCard } from "../components/ShareCard";

export function Lobby({ snapshot }: { snapshot: RoomSnapshot }) {
  return (
    <main className="safe-area mx-auto flex min-h-dvh max-w-lg flex-col gap-4 pb-44">
      <RoomHeader snapshot={snapshot} />
      <ShareCard code={snapshot.code} />
      <PlayersCard snapshot={snapshot} />
    </main>
  );
}
