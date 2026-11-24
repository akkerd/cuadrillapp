import { ERROR_CODES } from "@cuadrillapp/protocol";
import { describe, expect, it } from "vitest";
import { errorText } from "../copy";
import { isValidCode, normalizeCode } from "./format";

describe("format", () => {
  it("normalizes room codes", () => {
    expect(normalizeCode(" abc23 ")).toBe("ABC23");
    expect(isValidCode("ABC23")).toBe(true);
    expect(isValidCode("ABC0I")).toBe(false);
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
