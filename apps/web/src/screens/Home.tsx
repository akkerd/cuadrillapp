import { LIMITS } from "@cuadrillapp/protocol";
import { ArrowRight, DoorOpen, Download, Maximize, Plus } from "lucide-react";
import { motion } from "motion/react";
import { type FormEvent, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router";
import { Button, IconButton, Sheet } from "../components/ui";
import { copy } from "../copy";
import { canFullscreen, toggleFullscreen, useInstall } from "../hooks/device";
import { normalizeCode } from "../lib/format";

const STICKERS = ["🦄", "🌮", "🐸", "🤠", "👽"];

export function Home() {
  const navigate = useNavigate();
  const [joining, setJoining] = useState(false);
  const [code, setCode] = useState("");
  const [iosHelp, setIosHelp] = useState(false);
  const install = useInstall();
  const codeInput = useRef<HTMLInputElement>(null);

  // Foco al abrir el campo: el usuario acaba de pulsar "Unirse".
  useEffect(() => {
    if (joining) codeInput.current?.focus();
  }, [joining]);

  function join(event: FormEvent) {
    event.preventDefault();
    const normalized = normalizeCode(code);
    if (normalized) navigate(`/r/${normalized}`);
  }

  return (
    <main className="safe-area mx-auto flex min-h-dvh max-w-lg flex-col">
      <div className="flex justify-end">
        {canFullscreen() && (
          <IconButton
            label={copy.fullscreen}
            icon={Maximize}
            tone="paper"
            onClick={() => void toggleFullscreen()}
          />
        )}
      </div>

      <div className="flex flex-1 flex-col items-center justify-center gap-6 py-8 text-center">
        <div className="flex gap-1 text-5xl" aria-hidden>
          {STICKERS.map((emoji, index) => (
            <motion.span
              key={emoji}
              initial={{ y: -40, opacity: 0, rotate: 0 }}
              animate={{ y: 0, opacity: 1, rotate: index % 2 ? 10 : -10 }}
              transition={{ delay: index * 0.08, type: "spring", stiffness: 300, damping: 12 }}
            >
              {emoji}
            </motion.span>
          ))}
        </div>
        <h1 className="-rotate-2 rounded-3xl border-[3px] border-ink bg-sun px-6 py-3 text-5xl font-bold text-ink shadow-hard-lg">
          {copy.app}
        </h1>
        <p className="text-2xl font-medium">{copy.tagline}</p>
      </div>

      <div className="grid gap-4">
        <Button size="lg" icon={Plus} onClick={() => navigate("/crear")}>
          {copy.create}
        </Button>
        {joining ? (
          <form className="flex gap-3" onSubmit={join}>
            <input
              aria-label={copy.codePlaceholder}
              placeholder={copy.codePlaceholder}
              value={code}
              ref={codeInput}
              autoCapitalize="characters"
              autoCorrect="off"
              spellCheck={false}
              enterKeyHint="go"
              maxLength={LIMITS.codeLength + 6}
              onChange={(event) => setCode(event.target.value)}
              className="min-h-16 w-full min-w-0 rounded-2xl border-[3px] border-ink bg-paper px-4 text-center text-3xl font-bold uppercase tracking-[0.3em] text-ink placeholder:tracking-normal placeholder:text-ink/40"
            />
            <IconButton
              type="submit"
              label={copy.enter}
              icon={ArrowRight}
              tone="mint"
              size="lg"
              disabled={!code.trim()}
            />
          </form>
        ) : (
          <Button size="lg" tone="mint" icon={DoorOpen} onClick={() => setJoining(true)}>
            {copy.join}
          </Button>
        )}
        {install.mode && (
          <Button
            tone="paper"
            icon={Download}
            onClick={() => (install.mode === "ios" ? setIosHelp(true) : void install.install())}
          >
            {copy.install}
          </Button>
        )}
      </div>

      <Sheet open={iosHelp} onClose={() => setIosHelp(false)} title={copy.iosInstall.title}>
        <ol className="grid gap-3 text-xl font-semibold">
          <li className="flex items-center gap-3">
            <span className="grid size-12 place-items-center rounded-full border-[3px] border-ink bg-sun">
              1
            </span>
            <span aria-hidden>⬆️</span> {copy.iosInstall.step1}
          </li>
          <li className="flex items-center gap-3">
            <span className="grid size-12 place-items-center rounded-full border-[3px] border-ink bg-mint">
              2
            </span>
            <span aria-hidden>➕</span> {copy.iosInstall.step2}
          </li>
        </ol>
      </Sheet>
    </main>
  );
}
