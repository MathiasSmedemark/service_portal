import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { apiFetch } from "./client";

const originalFetch = global.fetch;

beforeEach(() => {
  global.fetch = vi.fn();
});

afterEach(() => {
  global.fetch = originalFetch;
  vi.restoreAllMocks();
});

it("adds a request id header", async () => {
  global.fetch.mockResolvedValue({
    ok: true,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => ({ status: "ok" })
  });

  await apiFetch("/healthz");

  const options = global.fetch.mock.calls[0][1];
  expect(options.headers.get("X-Request-Id")).toBeTruthy();
});

it("throws with API error message", async () => {
  global.fetch.mockResolvedValue({
    ok: false,
    status: 500,
    statusText: "Server error",
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => ({ error: { message: "Boom" } })
  });

  await expect(apiFetch("/healthz")).rejects.toThrow("Boom");
});
