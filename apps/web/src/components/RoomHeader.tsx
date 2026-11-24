import type { RoomSnapshot } from "@cuadrillapp/protocol";
import { LIMITS } from "@cuadrillapp/protocol";
import { LogOut, Pencil } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router";
import { copy } from "../copy";
import { leaveRoom } from "../lib/session";
import { act } from "../lib/socket";
import { Button, ConfirmSheet, IconButton, Sheet } from "./ui";

export function RoomHeader({
  snapshot,
  extra,
}: {
  snapshot: RoomSnapshot;
  extra?: React.ReactNode;
}) {
  const navigate = useNavigate();
  const [editing, setEditing] = useState(false);
  const [leaving, setLeaving] = useState(false);
  const [title, setTitle] = useState(snapshot.title);
  const isAdmin = snapshot.me.isAdmin;

  return (
    <header className="flex items-center gap-2">
      <div className="min-w-0 flex-1">
        <span className="inline-block rounded-xl border-2 border-ink bg-sun px-2 text-sm font-bold tracking-[0.2em] text-ink">
          🔑 {snapshot.code}
        </span>
        <h1 className="flex items-center gap-2 truncate text-3xl font-bold">
          <span className="truncate">{snapshot.title}</span>
          {isAdmin && (
            <button
              type="button"
              aria-label={copy.editTitle}
              className="shrink-0 rounded-lg p-1 active:scale-90"
              onClick={() => {
                setTitle(snapshot.title);
                setEditing(true);
              }}
            >
              <Pencil aria-hidden size={20} strokeWidth={2.75} />
            </button>
          )}
        </h1>
      </div>
      {extra}
      <IconButton label={copy.leave} icon={LogOut} tone="paper" onClick={() => setLeaving(true)} />

      <Sheet open={editing} onClose={() => setEditing(false)} title={copy.editTitle}>
        <form
          className="flex flex-col gap-3"
          onSubmit={async (event) => {
            event.preventDefault();
            if ((await act("room:title", { title })) !== undefined) setEditing(false);
          }}
        >
          <input
            aria-label={copy.editTitle}
            value={title}
            maxLength={LIMITS.titleMaxLength}
            onChange={(event) => setTitle(event.target.value)}
            className="min-h-14 rounded-2xl border-[3px] border-ink bg-white px-4 text-2xl font-semibold"
          />
          <Button type="submit" emoji="💾" disabled={!title.trim()}>
            {copy.save}
          </Button>
        </form>
      </Sheet>

      <ConfirmSheet
        open={leaving}
        title={copy.leaveConfirm}
        onClose={() => setLeaving(false)}
        onConfirm={async () => {
          await leaveRoom(snapshot.code);
          navigate("/");
        }}
      />
    </header>
  );
}
