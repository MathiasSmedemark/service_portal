import { createRequestId } from "./requestId";

const API_BASE_URL = import.meta.env?.VITE_API_BASE_URL || "/api/v1";

function buildUrl(path) {
  const base = API_BASE_URL.replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${base}${normalizedPath}`;
}

export async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});

  if (!headers.has("X-Request-Id")) {
    headers.set("X-Request-Id", createRequestId());
  }

  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  let body = options.body;
  if (
    body &&
    typeof body === "object" &&
    !(typeof FormData !== "undefined" && body instanceof FormData) &&
    !(typeof URLSearchParams !== "undefined" && body instanceof URLSearchParams) &&
    !(typeof Blob !== "undefined" && body instanceof Blob)
  ) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(body);
  }

  const response = await fetch(buildUrl(path), {
    ...options,
    headers,
    body
  });

  const contentType = response.headers?.get("content-type") || "";
  const isJson = contentType.includes("application/json");

  if (!response.ok) {
    let message = response.statusText || "Request failed";
    if (isJson) {
      try {
        const payload = await response.json();
        message = payload?.error?.message || payload?.message || message;
      } catch (error) {
        message = message || "Request failed";
      }
    } else {
      try {
        const text = await response.text();
        if (text) {
          message = text;
        }
      } catch (error) {
        message = message || "Request failed";
      }
    }
    throw new Error(message);
  }

  if (isJson) {
    return response.json();
  }

  return response.text();
}
