import {
  CATEGORY_SUGGESTIONS,
  type CategoryView,
  LIMITS,
  type RoomSnapshot,
} from "@cuadrillapp/protocol";
import { ChevronDown, ChevronUp, Pencil, Plus, Trash2 } from "lucide-react";
import { type FormEvent, useState } from "react";
import { copy } from "../copy";
import { act } from "../lib/socket";
import { Button, Card, CardTitle, IconButton, Sheet } from "./ui";

export function CategoriesCard({ snapshot }: { snapshot: RoomSnapshot }) {
  const editable = snapshot.me.isAdmin && snapshot.phase === "lobby";
  const [editing, setEditing] = useState<CategoryView | null>(null);
  const names = new Set(snapshot.categories.map((c) => c.name.toLowerCase()));
  const suggestions = CATEGORY_SUGGESTIONS.filter((s) => !names.has(s.name.toLowerCase()));
  const full = snapshot.categories.length >= LIMITS.maxCategories;

  return (
    <Card className="-rotate-[0.4deg]">
      <CardTitle emoji="🏷️">{copy.categories}</CardTitle>
      <ul className="grid gap-2">
        {snapshot.categories.map((category, index) => (
          <li
            key={category.id}
            className="flex items-center gap-2 rounded-2xl border-[3px] border-ink bg-white px-3 py-2"
          >
            <span className="text-2xl" aria-hidden>
              {category.emoji}
            </span>
            <span className="min-w-0 flex-1 truncate text-lg font-semibold">{category.name}</span>
            {editable && (
              <>
                <IconButton
                  label={`Subir ${category.name}`}
                  icon={ChevronUp}
                  tone="paper"
                  disabled={index === 0}
                  onClick={() =>
                    void act("category:move", { categoryId: category.id, direction: -1 })
                  }
                />
                <IconButton
                  label={`Bajar ${category.name}`}
                  icon={ChevronDown}
                  tone="paper"
                  disabled={index === snapshot.categories.length - 1}
                  onClick={() =>
                    void act("category:move", { categoryId: category.id, direction: 1 })
                  }
                />
                <IconButton
                  label={`Editar ${category.name}`}
                  icon={Pencil}
                  tone="sun"
                  onClick={() => setEditing(category)}
                />
                <IconButton
                  label={`Borrar ${category.name}`}
                  icon={Trash2}
                  tone="pink"
                  onClick={() => void act("category:delete", { categoryId: category.id })}
                />
              </>
            )}
          </li>
        ))}
      </ul>

      {editable && !full && (
        <>
          {suggestions.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {suggestions.map((s) => (
                <Button
                  key={s.name}
                  size="sm"
                  tone="mint"
                  emoji={s.emoji}
                  onClick={() => void act("category:add", s)}
                >
                  {s.name}
                </Button>
              ))}
            </div>
          )}
          <CategoryForm
            submitIcon
            onSubmit={async (emoji, name) =>
              (await act("category:add", { emoji, name })) !== undefined
            }
          />
        </>
      )}

      <Sheet open={editing !== null} onClose={() => setEditing(null)} title={copy.categories}>
        {editing && (
          <CategoryForm
            initialEmoji={editing.emoji}
            initialName={editing.name}
            onSubmit={async (emoji, name) => {
              const ok =
                (await act("category:update", { categoryId: editing.id, emoji, name })) !==
                undefined;
              if (ok) setEditing(null);
              return ok;
            }}
          />
        )}
      </Sheet>
    </Card>
  );
}

function CategoryForm({
  initialEmoji = "⭐",
  initialName = "",
  submitIcon = false,
  onSubmit,
}: {
  initialEmoji?: string;
  initialName?: string;
  submitIcon?: boolean;
  onSubmit: (emoji: string, name: string) => Promise<boolean>;
}) {
  const [emoji, setEmoji] = useState(initialEmoji);
  const [name, setName] = useState(initialName);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!name.trim() || !emoji.trim()) return;
    if ((await onSubmit(emoji.trim(), name.trim())) && submitIcon) {
      setName("");
      setEmoji("⭐");
    }
  }

  return (
    <form className="mt-3 flex gap-2" onSubmit={submit}>
      <input
        aria-label="Emoji"
        value={emoji}
        maxLength={8}
        onChange={(event) => setEmoji(event.target.value)}
        className="min-h-12 w-16 rounded-2xl border-[3px] border-ink bg-white text-center text-2xl"
      />
      <input
        aria-label={copy.categoryName}
        placeholder={copy.categoryName}
        value={name}
        maxLength={LIMITS.categoryNameMaxLength}
        onChange={(event) => setName(event.target.value)}
        className="min-h-12 min-w-0 flex-1 rounded-2xl border-[3px] border-ink bg-white px-3 text-lg font-semibold"
      />
      {submitIcon ? (
        <IconButton
          type="submit"
          label={copy.addCategory}
          icon={Plus}
          tone="sun"
          disabled={!name.trim()}
        />
      ) : (
        <Button type="submit" emoji="💾" disabled={!name.trim()}>
          {copy.save}
        </Button>
      )}
    </form>
  );
}
