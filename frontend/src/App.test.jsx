import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { expect, it } from "vitest";
import App from "./App.jsx";

const routerFutureFlags = {
  v7_startTransition: true,
  v7_relativeSplatPath: true
};

it("renders the navigation shell", () => {
  render(
    <MemoryRouter future={routerFutureFlags}>
      <App />
    </MemoryRouter>
  );

  expect(screen.getByText("Status")).toBeTruthy();
  expect(screen.getByText("Tickets")).toBeTruthy();
});
