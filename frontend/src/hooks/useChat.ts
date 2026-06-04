import { useCallback } from "react";
import { api } from "../services/api";
import { useChatStore } from "../store";
import type { Message } from "../types";

export function useChat() {
  const { activeSessionId, createSession, addMessage, setLoading, isLoading, activeMessages } =
    useChatStore();

  const send = useCallback(
    async (text: string) => {
      const sessionId = activeSessionId ?? createSession();

      const userMsg: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
        createdAt: Date.now(),
      };

      addMessage(sessionId, userMsg);
      setLoading(true);

      try {
        const allMessages = [...activeMessages(), userMsg];
        const res = await api.chat(allMessages, sessionId);

        const assistantMsg: Message = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: res.message.content,
          createdAt: Date.now(),
        };

        addMessage(sessionId, assistantMsg);
      } catch (err) {
        addMessage(sessionId, {
          id: crypto.randomUUID(),
          role: "assistant",
          content: err instanceof Error ? err.message : "Something went wrong.",
          createdAt: Date.now(),
        });
      } finally {
        setLoading(false);
      }
    },
    [activeSessionId, activeMessages, addMessage, createSession, setLoading]
  );

  return { send, isLoading, messages: activeMessages() };
}
