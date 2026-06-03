"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2, Trash2 } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Array<{
    video_id: string;
    chunk_id: string;
    content: string;
  }>;
}

export default function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! I'm your video analytics assistant. Ask me anything about the two videos you've uploaded, such as:\n\n• Why did Video A get more engagement than Video B?\n• What's the engagement rate of each?\n• Compare the hooks in the first 5 seconds.\n• Who's the creator of Video B and what's their follower count?\n• Suggest improvements for B based on what worked in A.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat/sync", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: userMessage }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = async () => {
    try {
      await fetch("http://localhost:8000/api/clear-memory", {
        method: "POST",
      });
      setMessages([
        {
          role: "assistant",
          content:
            "Memory cleared. I'm ready for new questions about the videos!",
        },
      ]);
    } catch (error) {
      console.error("Failed to clear memory:", error);
    }
  };

  return (
    <div className="bg-gray-800/50 backdrop-blur rounded-xl border border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="w-6 h-6 text-white" />
          <h2 className="text-white font-semibold text-lg">Video Analytics Chat</h2>
        </div>
        <button
          onClick={clearChat}
          className="text-white/80 hover:text-white transition-colors"
          title="Clear chat memory"
        >
          <Trash2 className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="h-96 overflow-y-auto p-6 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex gap-3 ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {message.role === "assistant" && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-700 text-gray-100"
              }`}
            >
              <div className="whitespace-pre-wrap text-sm">{message.content}</div>
              {message.sources && message.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-600">
                  <div className="text-xs text-gray-400 mb-2">Sources:</div>
                  {message.sources.map((source, idx) => (
                    <div
                      key={idx}
                      className="text-xs bg-gray-800 rounded px-2 py-1 mb-1"
                    >
                      <span className="text-blue-400 font-semibold">
                        [{source.video_id}, {source.chunk_id}]
                      </span>
                      <span className="text-gray-400 ml-2">
                        {source.content}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            {message.role === "user" && (
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                <User className="w-5 h-5 text-white" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center flex-shrink-0">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="bg-gray-700 rounded-2xl px-4 py-3">
              <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about the videos..."
            className="flex-1 px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
