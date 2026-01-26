import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import StatusSummary from "./StatusSummary.jsx";

const baseSummary = {
  platformCount: 0,
  lastUpdated: null
};

describe("StatusSummary", () => {
  it("renders the empty state", () => {
    render(<StatusSummary summary={{ ...baseSummary, state: "empty" }} metrics={[]} />);
    expect(screen.getByText("No status data yet")).toBeTruthy();
  });

  it("renders the healthy state", () => {
    render(<StatusSummary summary={{ ...baseSummary, state: "healthy" }} metrics={[]} />);
    expect(screen.getByText("All systems healthy")).toBeTruthy();
  });

  it("renders the degraded state", () => {
    render(<StatusSummary summary={{ ...baseSummary, state: "degraded" }} metrics={[]} />);
    expect(screen.getByText("Degraded performance")).toBeTruthy();
  });

  it("renders the unknown state", () => {
    render(<StatusSummary summary={{ ...baseSummary, state: "unknown" }} metrics={[]} />);
    expect(screen.getByText("Visibility limited")).toBeTruthy();
  });
});
