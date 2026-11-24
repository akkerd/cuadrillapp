import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router";
import { randomEmoji } from "../components/EmojiGrid";
import { ProfileForm } from "../components/ProfileForm";
import { Card, IconButton } from "../components/ui";
import { copy } from "../copy";
import { rememberSeat } from "../lib/session";
import { act } from "../lib/socket";
import { type Profile, storage } from "../lib/storage";

export function defaultProfile(): Profile {
  return storage.getProfile() ?? { name: "", emoji: randomEmoji(), role: "candidate" };
}

export function Screen({
  title,
  onBack,
  children,
}: {
  title: string;
  onBack: () => void;
  children: React.ReactNode;
}) {
  return (
    <main className="safe-area mx-auto flex min-h-dvh max-w-lg flex-col gap-4">
      <header className="flex items-center gap-3">
        <IconButton label={copy.back} icon={ArrowLeft} tone="paper" onClick={onBack} />
        <h1 className="truncate text-3xl font-bold">{title}</h1>
      </header>
      {children}
    </main>
  );
}

export function CreateScreen() {
  const navigate = useNavigate();
  return (
    <Screen title={`➕ ${copy.create}`} onBack={() => navigate("/")}>
      <Card>
        <ProfileForm
          initial={defaultProfile()}
          submitLabel={copy.create}
          submitEmoji="🎉"
          onSubmit={async (profile) => {
            storage.saveProfile(profile);
            const data = await act("room:create", profile);
            if (data) {
              rememberSeat(data);
              navigate(`/r/${data.code}`, { replace: true });
            }
          }}
        />
      </Card>
    </Screen>
  );
}
