/** Instalación, pantalla completa y pantalla siempre encendida. */
import { useEffect, useState } from "react";

type InstallPromptEvent = Event & { prompt: () => Promise<void> };

export function isStandalone(): boolean {
  return (
    window.matchMedia?.("(display-mode: standalone)").matches ||
    window.matchMedia?.("(display-mode: fullscreen)").matches ||
    (navigator as Navigator & { standalone?: boolean }).standalone === true
  );
}

export function isIos(): boolean {
  return /iphone|ipad|ipod/i.test(navigator.userAgent);
}

/** Devuelve cómo instalar: prompt nativo (Android), guía (iOS) o nada. */
export function useInstall(): { mode: "prompt" | "ios" | null; install: () => Promise<void> } {
  const [event, setEvent] = useState<InstallPromptEvent | null>(null);
  useEffect(() => {
    const onPrompt = (e: Event) => {
      e.preventDefault();
      setEvent(e as InstallPromptEvent);
    };
    window.addEventListener("beforeinstallprompt", onPrompt);
    return () => window.removeEventListener("beforeinstallprompt", onPrompt);
  }, []);
  if (isStandalone()) return { mode: null, install: async () => {} };
  if (event) {
    return {
      mode: "prompt",
      install: async () => {
        await event.prompt();
        setEvent(null);
      },
    };
  }
  return { mode: isIos() ? "ios" : null, install: async () => {} };
}

export function canFullscreen(): boolean {
  return Boolean(document.fullscreenEnabled) && !isStandalone();
}

export async function toggleFullscreen(): Promise<void> {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await document.documentElement.requestFullscreen({ navigationUI: "hide" });
  } catch {
    // el navegador lo ha rechazado: no es grave
  }
}

/** Mantiene la pantalla encendida mientras `active` sea true. */
export function useWakeLock(active: boolean): void {
  useEffect(() => {
    if (!active || !("wakeLock" in navigator)) return;
    let lock: WakeLockSentinel | null = null;
    let cancelled = false;
    const acquire = async () => {
      try {
        if (document.visibilityState === "visible" && !cancelled) {
          lock = await navigator.wakeLock.request("screen");
        }
      } catch {
        lock = null;
      }
    };
    const onVisible = () => {
      if (document.visibilityState === "visible") void acquire();
    };
    void acquire();
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      cancelled = true;
      document.removeEventListener("visibilitychange", onVisible);
      void lock?.release().catch(() => {});
    };
  }, [active]);
}
