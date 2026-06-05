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

  /**
   * Streaming chat — uses fetch with ReadableStream.
   * EventSource cannot POST a body, so we use fetch + stream reader instead.
   *
   * Usage:
   *   const reader = await api.chatStream(messages)
   *   while (true) {
   *     const { done, value } = await reader.read()
   *     if (done) break
   *     const text = new TextDecoder().decode(value)
   *     // parse SSE lines: "data: {...}\n\n"
   *   }
   */
  chatStream: async (messages: Message[]): Promise<ReadableStreamDefaultReader<Uint8Array>> => {
    const res = await fetch(`${BASE}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages }),
    });
    if (!res.ok || !res.body) throw new Error(`Stream failed: HTTP ${res.status}`);
    return res.body.getReader();
  },
};
