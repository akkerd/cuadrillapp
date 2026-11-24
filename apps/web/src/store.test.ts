import type { RoomSnapshot } from "@cuadrillapp/protocol";
import { beforeEach, describe, expect, it } from "vitest";
import { useStore } from "./store";

function snapshot(version: number, title = "Concurso"): RoomSnapshot {
  return {
    code: "ABC23",
    version,
    title,
    phase: "lobby",
    me: { participantId: "p1", isAdmin: true, progress: { given: 0, total: 0 } },
    participants: [],
    categories: [],
    myScores: [],
    proxyScores: [],
    startCheck: { ready: false, missing: ["categories"] },
  };
}

describe("store", () => {
  beforeEach(() => useStore.setState({ snapshot: null, exit: null }));

  it("ignores snapshots older than the current one", () => {
    useStore.getState().applySnapshot(snapshot(5, "nuevo"));
    useStore.getState().applySnapshot(snapshot(4, "viejo"));
    expect(useStore.getState().snapshot?.title).toBe("nuevo");
  });

  it("clears the room when kicked", () => {
    useStore.getState().applySnapshot(snapshot(1));
    useStore.getState().setExit("kicked", "ABC23");
    expect(useStore.getState().snapshot).toBeNull();
    expect(useStore.getState().exit).toEqual({ reason: "kicked", code: "ABC23" });
  });
});
