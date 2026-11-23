import { LIMITS, type Role } from "@cuadrillapp/protocol";
import { Dices } from "lucide-react";
import { type FormEvent, useState } from "react";
import { copy } from "../copy";
import { cx } from "../lib/format";
import type { Profile } from "../lib/storage";
import { Avatar } from "./Avatar";
import { EmojiGrid, randomEmoji } from "./EmojiGrid";
import { Button, IconButton } from "./ui";

export function RoleToggle({ value, onChange }: { value: Role; onChange: (role: Role) => void }) {
  return (
    <div className="grid grid-cols-2 gap-2" role="radiogroup" aria-label="Rol">
      {(["candidate", "voter"] as const).map((role) => (
        <button
          key={role}
          type="button"
          role="radio"
          aria-checked={value === role}
          onClick={() => onChange(role)}
          className={cx(
            "flex min-h-12 items-center justify-center gap-2 rounded-2xl border-[3px] border-ink text-lg font-semibold",
            value === role ? "bg-mint shadow-hard-sm" : "bg-white/70",
          )}
        >
          <span aria-hidden>{copy.roleHint[role]}</span>
          {copy.role[role]}
        </button>
      ))}
    </div>
  );
}

export function ProfileForm({
  initial,
  submitLabel,
  submitEmoji = "🚀",
  showRole = true,
  onSubmit,
}: {
  initial: Profile;
  submitLabel: string;
  submitEmoji?: string;
  showRole?: boolean;
  onSubmit: (profile: Profile) => Promise<void> | void;
}) {
  const [emoji, setEmoji] = useState(initial.emoji);
  const [name, setName] = useState(initial.name);
  const [role, setRole] = useState<Role>(initial.role);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!name.trim() || busy) return;
    setBusy(true);
    try {
      await onSubmit({ name: name.trim(), emoji, role });
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="flex flex-col gap-4" onSubmit={submit}>
      <div className="flex items-center justify-center gap-4">
        <Avatar emoji={emoji} seed={name || emoji} size="xl" className="-rotate-6" />
        <IconButton
          label={copy.random}
          icon={Dices}
          tone="mint"
          size="md"
          onClick={() => setEmoji(randomEmoji(emoji))}
        />
      </div>
      <EmojiGrid value={emoji} onChange={setEmoji} />
      <input
        aria-label={copy.yourName}
        placeholder={copy.yourName}
        value={name}
        maxLength={LIMITS.nameMaxLength}
        autoComplete="nickname"
        enterKeyHint="go"
        onChange={(event) => setName(event.target.value)}
        className="min-h-14 rounded-2xl border-[3px] border-ink bg-white px-4 text-2xl font-semibold text-ink placeholder:text-ink/40"
      />
      {showRole && <RoleToggle value={role} onChange={setRole} />}
      <Button type="submit" size="lg" emoji={submitEmoji} disabled={!name.trim() || busy}>
        {submitLabel}
      </Button>
    </form>
  );
}
