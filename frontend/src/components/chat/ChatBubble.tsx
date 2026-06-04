import type { Message } from "../../types";

export function ChatBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  return (
    <div className={`bubble-wrap bubble-wrap--${message.role}`}>
      {!isUser && <div className="avatar">AI</div>}
      <div className={`bubble bubble--${message.role}`}>
        <p>{message.content}</p>
      </div>
      {isUser && <div className="avatar avatar--user">U</div>}
    </div>
  );
}
