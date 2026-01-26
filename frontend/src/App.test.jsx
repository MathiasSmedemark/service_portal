import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { expect, it } from "vitest";
import App from "./App.jsx";

it("renders the navigation shell", () => {
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>
  );

  expect(screen.getByText("Status")).toBeTruthy();
  expect(screen.getByText("Tickets")).toBeTruthy();
});
