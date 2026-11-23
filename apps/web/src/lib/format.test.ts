import { ERROR_CODES } from "@cuadrillapp/protocol";
import { describe, expect, it } from "vitest";
import { errorText } from "../copy";
import { clampQuarters, formatQuarters, isValidCode, normalizeCode, scoreFace } from "./format";

describe("format", () => {
  it("formats quarters with a decimal comma", () => {
    expect(formatQuarters(29)).toBe("7,25");
    expect(formatQuarters(40)).toBe("10,00");
  });

  it("clamps to the 0..40 scale", () => {
    expect(clampQuarters(-3)).toBe(0);
    expect(clampQuarters(41)).toBe(40);
  });

  it("normalizes room codes", () => {
    expect(normalizeCode(" abc23 ")).toBe("ABC23");
    expect(isValidCode("ABC23")).toBe(true);
    expect(isValidCode("ABC0I")).toBe(false);
  });

  it("picks a face for each score", () => {
    expect(scoreFace(null)).toBe("🤔");
    expect(scoreFace(0)).toBe("😭");
    expect(scoreFace(40)).toBe("🤩");
  });
});

describe("error texts", () => {
  it("covers every server error code with a short message", () => {
    for (const code of ERROR_CODES) {
      expect(errorText[code]).toBeTruthy();
      expect(errorText[code].split(" ").length).toBeLessThanOrEqual(4);
    }
  });
});
