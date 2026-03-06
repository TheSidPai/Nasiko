import { useState, useRef, useEffect } from "react";
import { sendToAgent } from "../../services/api";
import { SUGGESTED_PROMPTS } from "../../constants";
import styles from "./ChatPage.module.css";

const INITIAL_MESSAGE = {
  role: "agent",
  text: "Hi! I'm TalentFlow. I can help with recruiting, policy questions, internal talent matching, and burnout risk. What do you need?",
};

export default function ChatPage() {
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(text) {
    const msg = text || input.trim();
    if (!msg || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: msg }]);
    setLoading(true);
    try {
      const reply = await sendToAgent(msg);
      setMessages((prev) => [...prev, { role: "agent", text: reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "agent", text: "⚠️ Could not reach the agent. Make sure the backend is running on port 5000." },
      ]);
    }
    setLoading(false);
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className={styles.page}>
      {/* Messages */}
      <div className={styles.messages}>
        {/* Suggested prompts (shown only at start) */}
        {messages.length === 1 && (
          <div>
            <div className={styles.suggestLabel}>SUGGESTED PROMPTS</div>
            <div className={styles.suggestWrap}>
              {SUGGESTED_PROMPTS.map((s) => (
                <button key={s} className={styles.suggestBtn} onClick={() => send(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`${styles.row} ${m.role === "user" ? styles.rowUser : styles.rowAgent}`}>
            <div className={`${styles.bubble} ${m.role === "user" ? styles.bubbleUser : styles.bubbleAgent}`}>
              {m.text}
            </div>
          </div>
        ))}

        {loading && (
          <div className={styles.typing}>
            <div className={styles.typingInner}>
              <div className={styles.dot} />
              <div className={styles.dot} />
              <div className={styles.dot} />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className={styles.inputBar}>
        <div className={styles.inputInner}>
          <textarea
            className={styles.textarea}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about leave policy, screen a resume, check burnout risk..."
            rows={1}
          />
          <button
            className={styles.sendBtn}
            onClick={() => send()}
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
