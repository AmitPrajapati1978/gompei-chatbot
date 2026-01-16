import { useState } from "react";
import "./App.css";
import bgImage from "./assets/DSC_4712_PRINT.jpg";


type Message = {
  role: "user" | "bot";
  text: string;
};

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setInput("");

    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userText }),
      });

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { role: "bot", text: data.answer || "No response found." },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Error contacting server ❌" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (

    <div
  className="page"
  style={{ backgroundImage: `url(${bgImage})` }}
>
      <div className="chat-card">
        <header className="chat-header">
          Gompei Chatbot <span>🐐</span>
        </header>

        <div className="chat-body">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`bubble ${m.role === "user" ? "user" : "bot"}`}
            >
              {m.text}
            </div>
          ))}

          {loading && <div className="bubble bot typing">Thinking…</div>}
        </div>

        <div className="chat-input">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask something about WPI…"
          />
          <button onClick={sendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;
