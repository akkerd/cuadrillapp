/** Conexión en tiempo real: comandos tipados con ack y reincorporación automática. */
import type { Ack, ClientCommands, ServerEvents } from "@cuadrillapp/protocol";
import { io, type Socket } from "socket.io-client";
import { errorText } from "../copy";
import { useStore } from "../store";
import { storage } from "./storage";

type Listeners = { [E in keyof ServerEvents]: (data: ServerEvents[E]) => void };

export const socket: Socket<Listeners> = io({
  autoConnect: false,
  reconnectionDelay: 500,
  reconnectionDelayMax: 4000,
});

let activeCode: string | null = null;

export async function send<E extends keyof ClientCommands>(
  event: E,
  payload: ClientCommands[E]["payload"],
): Promise<Ack<ClientCommands[E]["data"]>> {
  // Si aún no hay conexión (servidor arrancando), Socket.IO encola y esperamos más.
  const timeout = socket.connected ? 8000 : 60000;
  try {
    const untyped = socket as unknown as Socket;
    return (await untyped.timeout(timeout).emitWithAck(event, payload)) as Ack<
      ClientCommands[E]["data"]
    >;
  } catch {
    return { ok: false, error: socket.connected ? "TIMEOUT" : "DISCONNECTED" };
  }
}

/** Envía y muestra el error como aviso corto si falla. */
export async function act<E extends keyof ClientCommands>(
  event: E,
  payload: ClientCommands[E]["payload"],
): Promise<ClientCommands[E]["data"] | undefined> {
  const result = await send(event, payload);
  if (!result.ok) {
    useStore.getState().toast(errorText[result.error], "error");
    return undefined;
  }
  return result.data;
}

const rejoining = new Map<string, Promise<boolean>>();

/** Recupera la plaza guardada en este dispositivo. Agrupa llamadas simultáneas. */
export function rejoin(code: string): Promise<boolean> {
  const inFlight = rejoining.get(code);
  if (inFlight) return inFlight;
  const attempt = (async () => {
    const seat = storage.getSeat(code);
    if (!seat) return false;
    const result = await send("room:rejoin", { code, token: seat.token });
    if (result.ok) return true;
    if (result.error === "ROOM_NOT_FOUND" || result.error === "BAD_TOKEN") {
      storage.clearSeat(code);
      useStore.getState().setExit("closed", code);
    }
    return false;
  })().finally(() => rejoining.delete(code));
  rejoining.set(code, attempt);
  return attempt;
}

export function setActiveRoom(code: string | null): void {
  activeCode = code;
}

let started = false;

export function startConnection(): void {
  if (started) return;
  started = true;
  const store = useStore.getState();
  socket.on("connect", () => {
    useStore.getState().setConnection("online");
    if (activeCode && storage.getSeat(activeCode)) void rejoin(activeCode);
  });
  socket.on("disconnect", () => useStore.getState().setConnection("offline"));
  socket.on("connect_error", () => useStore.getState().setConnection("offline"));
  socket.on("room:state", (snapshot) => useStore.getState().applySnapshot(snapshot));
  socket.on("room:kicked", ({ code }) => {
    storage.clearSeat(code);
    useStore.getState().setExit("kicked", code);
  });
  socket.on("room:replaced", ({ code }) => useStore.getState().setExit("replaced", code));
  store.setConnection("connecting");
  socket.connect();
}
