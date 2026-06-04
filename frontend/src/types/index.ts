export type Role = "user" | "assistant" | "system";

export type Message = {
  id: string;
  role: Role;
  content: string;
  createdAt?: number;
};

export type Session = {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
};

export type ChatResponse = {
  message: { role: Role; content: string };
  session_id: string | null;
};

export type CompletionResponse = {
  text: string;
  model: string;
};
