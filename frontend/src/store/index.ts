import { create } from "zustand";
import type { Message, Session } from "../types";

type ChatStore = {
  sessions: Session[];
  activeSessionId: string | null;
  isLoading: boolean;

  createSession: () => string;
  setActiveSession: (id: string) => void;
  addMessage: (sessionId: string, message: Message) => void;
  setLoading: (v: boolean) => void;
  activeMessages: () => Message[];
};

export const useChatStore = create<ChatStore>((set, get) => ({
  sessions: [],
  activeSessionId: null,
  isLoading: false,

  createSession: () => {
    const id = crypto.randomUUID();
    const session: Session = {
      id,
      title: "New chat",
      messages: [],
      createdAt: Date.now(),
    };
    set((s) => ({ sessions: [...s.sessions, session], activeSessionId: id }));
    return id;
  },

  setActiveSession: (id) => set({ activeSessionId: id }),

  addMessage: (sessionId, message) =>
    set((s) => ({
      sessions: s.sessions.map((sess) =>
        sess.id === sessionId
          ? { ...sess, messages: [...sess.messages, message] }
          : sess
      ),
    })),

  setLoading: (v) => set({ isLoading: v }),

  activeMessages: () => {
    const { sessions, activeSessionId } = get();
    return sessions.find((s) => s.id === activeSessionId)?.messages ?? [];
  },
}));
