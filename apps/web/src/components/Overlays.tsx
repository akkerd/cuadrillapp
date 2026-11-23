import { useRegisterSW } from "virtual:pwa-register/react";
import { RefreshCw } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import { copy } from "../copy";
import { useStore } from "../store";
import { Button } from "./ui";

/** Arranque en frío: el servidor gratuito puede tardar en despertar. */
export function WakingOverlay() {
  const waiting = useStore((s) => !s.everConnected && s.connection !== "online");
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    if (!waiting) {
      setVisible(false);
      return;
    }
    const timer = window.setTimeout(() => setVisible(true), 1200);
    return () => window.clearTimeout(timer);
  }, [waiting]);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          className="fixed inset-0 z-50 grid place-items-center bg-grape/95"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          role="status"
        >
          <div className="flex flex-col items-center gap-4">
            <motion.span
              className="text-8xl"
              aria-hidden
              animate={{ y: [0, -18, 0] }}
              transition={{ repeat: Number.POSITIVE_INFINITY, duration: 1.4 }}
            >
              😴
            </motion.span>
            <p className="text-3xl font-bold">{copy.waking}</p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export function ConnectionBanner() {
  const lost = useStore((s) => s.everConnected && s.connection !== "online");
  return (
    <AnimatePresence>
      {lost && (
        <motion.div
          role="status"
          className="fixed inset-x-0 top-0 z-50 flex justify-center pt-[max(env(safe-area-inset-top),8px)]"
          initial={{ y: -60 }}
          animate={{ y: 0 }}
          exit={{ y: -60 }}
        >
          <span className="rounded-2xl border-[3px] border-ink bg-bubblegum px-4 py-1.5 text-lg font-bold text-ink shadow-hard">
            📡 {copy.connectionLost}
          </span>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/** Nunca recarga sola: el usuario decide cuándo actualizar. */
export function UpdatePrompt() {
  const {
    needRefresh: [needRefresh],
    updateServiceWorker,
  } = useRegisterSW();
  if (!needRefresh) return null;
  return (
    <div className="fixed inset-x-0 top-0 z-50 flex justify-center pt-[max(env(safe-area-inset-top),8px)]">
      <div className="flex items-center gap-3 rounded-2xl border-[3px] border-ink bg-paper px-3 py-2 text-ink shadow-hard">
        <span className="font-semibold">{copy.newVersion}</span>
        <Button size="sm" icon={RefreshCw} onClick={() => void updateServiceWorker(true)}>
          {copy.update}
        </Button>
      </div>
    </div>
  );
}
