/** Datos que se recuerdan en el dispositivo. Nunca rompe si localStorage no está disponible. */
import type { Role } from "@cuadrillapp/protocol";

export type Profile = { name: string; emoji: string; role: Role };
export type Seat = { code: string; token: string; participantId: string };

const PROFILE_KEY = "cq:profile";
const seatKey = (code: string) => `cq:seat:${code}`;

function read<T>(key: string): T | null {
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

function write(key: string, value: unknown): void {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // modo privado o almacenamiento lleno: seguimos sin recordar
  }
}

function remove(key: string): void {
  try {
    window.localStorage.removeItem(key);
  } catch {
    // nada que hacer
  }
}

export const storage = {
  getProfile: () => read<Profile>(PROFILE_KEY),
  saveProfile: (profile: Profile) => write(PROFILE_KEY, profile),
  getSeat: (code: string) => read<Seat>(seatKey(code)),
  saveSeat: (seat: Seat) => write(seatKey(seat.code), seat),
  clearSeat: (code: string) => remove(seatKey(code)),
};
