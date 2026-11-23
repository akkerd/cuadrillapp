import { fireEvent, render, screen } from "@testing-library/react";
import { useState } from "react";
import { describe, expect, it } from "vitest";
import { ScoreControl } from "./ScoreControl";

function Harness({ initial }: { initial: number | null }) {
  const [value, setValue] = useState<number | null>(initial);
  return <ScoreControl label="Gracioso" value={value} onChange={setValue} />;
}

describe("ScoreControl", () => {
  it("adds and subtracts 0,25", () => {
    render(<Harness initial={28} />);
    expect(screen.getByTestId("score-value")).toHaveTextContent("7,00");
    fireEvent.click(screen.getByRole("button", { name: "Sumar 0,25" }));
    expect(screen.getByTestId("score-value")).toHaveTextContent("7,25");
    fireEvent.click(screen.getByRole("button", { name: "Restar 0,25" }));
    fireEvent.click(screen.getByRole("button", { name: "Restar 0,25" }));
    expect(screen.getByTestId("score-value")).toHaveTextContent("6,75");
  });

  it("starts empty and can be cleared", () => {
    render(<Harness initial={null} />);
    expect(screen.getByTestId("score-value")).toHaveTextContent("—");
    fireEvent.change(screen.getByRole("slider"), { target: { value: "36" } });
    expect(screen.getByTestId("score-value")).toHaveTextContent("9,00");
    fireEvent.click(screen.getByRole("button", { name: "Borrar nota" }));
    expect(screen.getByTestId("score-value")).toHaveTextContent("—");
  });

  it("does not go above 10", () => {
    render(<Harness initial={40} />);
    expect(screen.getByRole("button", { name: "Sumar 0,25" })).toBeDisabled();
  });
});
