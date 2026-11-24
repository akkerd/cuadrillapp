import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { describe, expect, it } from "vitest";
import { Home } from "./Home";

describe("Home", () => {
  it("shows the app name", () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>,
    );
    expect(screen.getByRole("heading", { name: "Cuadrillapp" })).toBeInTheDocument();
  });
});
