import type { ParticipantView, RoomSnapshot } from "@cuadrillapp/protocol";
import { Crown, UserPlus, WifiOff } from "lucide-react";
import { useState } from "react";
import { copy } from "../copy";
import { act } from "../lib/socket";
import { Avatar } from "./Avatar";
import { randomEmoji } from "./EmojiGrid";
import { ProfileForm, RoleToggle } from "./ProfileForm";
import { Button, Card, CardTitle, ConfirmSheet, Sheet } from "./ui";

export function ParticipantRow({
  participant: p,
  isMe,
  onClick,
  trailing,
}: {
  participant: ParticipantView;
  isMe: boolean;
  onClick?: () => void;
  trailing?: React.ReactNode;
}) {
  const offline = !p.connected && !p.isManual;
  const content = (
    <>
      <Avatar emoji={p.emoji} seed={p.id} dimmed={offline} />
      <span className="min-w-0 flex-1 truncate text-left text-lg font-semibold">
        {p.name}
        {isMe && <span className="text-ink/70"> · {copy.you}</span>}
      </span>
      {p.isAdmin && <Crown aria-label={copy.admin} className="text-tangerine" strokeWidth={2.75} />}
      {p.role === "voter" && (
        <span role="img" aria-label={copy.role.voter}>
          🗳️
        </span>
      )}
      {p.isManual && (
        <span role="img" aria-label={copy.noPhone}>
          📵
        </span>
      )}
      {offline && <WifiOff aria-label={copy.offline} className="text-bubblegum" />}
      {trailing}
    </>
  );
  return (
    <li>
      {onClick ? (
        <button
          type="button"
          onClick={onClick}
          className="flex w-full items-center gap-3 rounded-2xl p-1.5 active:bg-ink/10"
        >
          {content}
        </button>
      ) : (
        <div className="flex w-full items-center gap-3 p-1.5">{content}</div>
      )}
    </li>
  );
}

export function PlayersCard({ snapshot }: { snapshot: RoomSnapshot }) {
  const [targetId, setTargetId] = useState<string | null>(null);
  const [adding, setAdding] = useState(false);
  const isAdmin = snapshot.me.isAdmin;
  const meId = snapshot.me.participantId;
  const target = snapshot.participants.find((p) => p.id === targetId) ?? null;

  return (
    <Card>
      <CardTitle emoji="👥">
        {copy.players}
        <span className="ml-auto rounded-full border-2 border-ink bg-sun px-2 text-base">
          {snapshot.participants.length}
        </span>
      </CardTitle>
      <ul className="grid gap-1">
        {snapshot.participants.map((p) => (
          <ParticipantRow
            key={p.id}
            participant={p}
            isMe={p.id === meId}
            onClick={isAdmin || p.id === meId ? () => setTargetId(p.id) : undefined}
          />
        ))}
      </ul>
      {isAdmin && (
        <Button className="mt-3 w-full" tone="mint" icon={UserPlus} onClick={() => setAdding(true)}>
          {copy.addPerson} 📵
        </Button>
      )}

      <Sheet open={adding} onClose={() => setAdding(false)} title={copy.addPersonTitle}>
        <ProfileForm
          initial={{ name: "", emoji: randomEmoji(), role: "candidate" }}
          submitLabel={copy.addPerson}
          submitEmoji="➕"
          onSubmit={async (profile) => {
            if ((await act("manual:add", profile)) !== undefined) setAdding(false);
          }}
        />
      </Sheet>

      {target && (
        <ParticipantSheet snapshot={snapshot} target={target} onClose={() => setTargetId(null)} />
      )}
    </Card>
  );
}

function ParticipantSheet({
  snapshot,
  target,
  onClose,
}: {
  snapshot: RoomSnapshot;
  target: ParticipantView;
  onClose: () => void;
}) {
  const [kicking, setKicking] = useState(false);
  const isMe = target.id === snapshot.me.participantId;
  const isAdmin = snapshot.me.isAdmin;
  const inLobby = snapshot.phase === "lobby";
  const canEditProfile = isMe || (isAdmin && target.isManual);
  const participantId = isMe ? undefined : target.id;

  return (
    <Sheet open onClose={onClose} title={`${target.emoji} ${target.name}`}>
      <div className="flex max-h-[70dvh] flex-col gap-4 overflow-y-auto">
        {canEditProfile ? (
          <ProfileForm
            initial={{ name: target.name, emoji: target.emoji, role: target.role }}
            submitLabel={copy.save}
            submitEmoji="💾"
            showRole={inLobby}
            onSubmit={async (profile) => {
              const ok = await act("participant:update", {
                participantId,
                name: profile.name,
                emoji: profile.emoji,
                role: inLobby ? profile.role : undefined,
              });
              if (ok !== undefined) onClose();
            }}
          />
        ) : (
          inLobby && (
            <RoleToggle
              value={target.role}
              onChange={(role) => void act("participant:update", { participantId, role })}
            />
          )
        )}
        {isAdmin && !target.isManual && (
          <Button
            tone="sun"
            icon={Crown}
            onClick={async () => {
              const ok = await act("admin:set", {
                participantId: target.id,
                isAdmin: !target.isAdmin,
              });
              if (ok !== undefined) onClose();
            }}
          >
            {target.isAdmin ? copy.removeAdmin : copy.makeAdmin}
          </Button>
        )}
        {isAdmin && !isMe && (
          <Button tone="pink" emoji="👋" onClick={() => setKicking(true)}>
            {copy.kick}
          </Button>
        )}
      </div>
      <ConfirmSheet
        open={kicking}
        title={copy.kickConfirm}
        onClose={() => setKicking(false)}
        onConfirm={async () => {
          if ((await act("participant:kick", { participantId: target.id })) !== undefined)
            onClose();
        }}
      />
    </Sheet>
  );
}
