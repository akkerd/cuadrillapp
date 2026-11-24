import type { RoomSnapshot } from "@cuadrillapp/protocol";
import { create } from "zustand";

export type Connection = "connecting" | "online" | "offline";
export type ExitReason = "kicked" | "closed" | "replaced";
export type Toast = { id: number; text: string; tone: "info" | "error" };

type State = {
  connection: Connection;
  everConnected: boolean;
  snapshot: RoomSnapshot | null;
  exit: { reason: ExitReason; code: string } | null;
  toasts: Toast[];
  setConnection: (connection: Connection) => void;
  applySnapshot: (snapshot: RoomSnapshot) => void;
  leaveRoom: () => void;
  setExit: (reason: ExitReason, code: string) => void;
  toast: (text: string, tone?: Toast["tone"]) => void;
  dismiss: (id: number) => void;
};

let nextToast = 1;

export const useStore = create<State>()((set) => ({
  connection: "connecting",
  everConnected: false,
  snapshot: null,
  exit: null,
  toasts: [],
  setConnection: (connection) =>
    set((s) => ({ connection, everConnected: s.everConnected || connection === "online" })),
  applySnapshot: (snapshot) =>
    set((s) => {
      const current = s.snapshot;
      // Concurrent emits may arrive out of order: the highest version wins.
      if (current && current.code === snapshot.code && snapshot.version < current.version) {
        return {};
      }
      return { snapshot, exit: s.exit?.code === snapshot.code ? null : s.exit };
    }),
  leaveRoom: () => set({ snapshot: null, exit: null }),
  setExit: (reason, code) =>
    set((s) => ({
      exit: { reason, code },
      snapshot: s.snapshot?.code === code ? null : s.snapshot,
    })),
  toast: (text, tone = "info") => {
    const id = nextToast++;
    set((s) => ({ toasts: [...s.toasts.slice(-2), { id, text, tone }] }));
    window.setTimeout(() => useStore.getState().dismiss(id), 2600);
  },
  dismiss: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}));
