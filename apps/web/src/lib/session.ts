/** Session actions that combine the server, the device and the store. */
import type { JoinResult } from "@cuadrillapp/protocol";
import { useStore } from "../store";
import { send, setActiveRoom } from "./socket";
import { storage } from "./storage";

export function rememberSeat(data: JoinResult): void {
  storage.saveSeat({ code: data.code, token: data.token, participantId: data.participantId });
  setActiveRoom(data.code);
}

export async function leaveRoom(code: string): Promise<void> {
  await send("room:leave", {});
  forgetRoom(code);
}

/** Forget the room on this device (after leaving, being kicked or the room closing). */
export function forgetRoom(code: string): void {
  storage.clearSeat(code);
  setActiveRoom(null);
  useStore.getState().leaveRoom();
}
