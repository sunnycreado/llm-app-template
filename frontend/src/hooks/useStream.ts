import { useCallback, useRef, useState } from "react";
import { api } from "../services/api";
import type { Message } from "../types";

export function useStream() {
  const [tokens, setTokens] = useState("");
  const [streaming, setStreaming] = useState(false);
  const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null);

  const start = useCallback(async (messages: Message[]) => {
    readerRef.current?.cancel();
    setTokens("");
    setStreaming(true);

    try {
      const reader = await api.chatStream(messages);
      readerRef.current = reader;
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (!line.startsWith("data:")) continue;
          const data = line.slice(5).trim();
          if (data === "[DONE]") break;
          try {
            const parsed = JSON.parse(data);
            if (parsed.token) setTokens((prev) => prev + parsed.token);
          } catch { /* skip malformed lines */ }
        }
      }
    } catch (err) {
      console.error("[useStream] error:", err);
    } finally {
      setStreaming(false);
    }
  }, []);

  const stop = useCallback(() => {
    readerRef.current?.cancel();
    readerRef.current = null;
    setStreaming(false);
  }, []);

  const reset = useCallback(() => {
    setTokens("");
  }, []);

  return { tokens, streaming, start, stop, reset };
}
