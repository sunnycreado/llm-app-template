import type { ChatResponse, CompletionResponse, Message } from "../types";

const BASE = "/api";

async function request<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: body ? "POST" : "GET",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  health: () => request<{ status: string }>("/health"),

  chat: (messages: Message[], session_id?: string) =>
    request<ChatResponse>("/chat", { messages, session_id }),

  complete: (prompt: string) =>
    request<CompletionResponse>("/completions", { prompt }),

  chatStream: (messages: Message[]): EventSource => {
    // SSE — caller listens to onmessage
    return new EventSource(`${BASE}/chat/stream`);
  },
};
