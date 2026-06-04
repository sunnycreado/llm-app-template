import { useCallback, useRef, useState } from "react";

export function useStream() {
  const [tokens, setTokens] = useState("");
  const [streaming, setStreaming] = useState(false);
  const sourceRef = useRef<EventSource | null>(null);

  const start = useCallback((url: string) => {
    sourceRef.current?.close();
    setTokens("");
    setStreaming(true);

    const es = new EventSource(url);
    sourceRef.current = es;

    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        setTokens((prev) => prev + (data.token ?? ""));
      } catch {}
    };

    es.onerror = () => {
      es.close();
      setStreaming(false);
    };
  }, []);

  const stop = useCallback(() => {
    sourceRef.current?.close();
    setStreaming(false);
  }, []);

  return { tokens, streaming, start, stop };
}
