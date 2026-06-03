"use client";

import { useState } from "react";
import VideoCard from "@/components/VideoCard";
import ChatPanel from "@/components/ChatPanel";
import { Play, Send, Loader2 } from "lucide-react";

interface VideoData {
  video_id: string;
  metadata: {
    title: string;
    views: number;
    likes: number;
    comments: number;
    creator: string;
    upload_date: string;
    duration: number;
    thumbnail?: string;
  };
  engagement_rate: number;
}

export default function Home() {
  const [videoAUrl, setVideoAUrl] = useState("");
  const [videoBUrl, setVideoBUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [processed, setProcessed] = useState(false);
  const [videoA, setVideoA] = useState<VideoData | null>(null);
  const [videoB, setVideoB] = useState<VideoData | null>(null);
  const [error, setError] = useState("");

  const processVideos = async () => {
    if (!videoAUrl || !videoBUrl) {
      setError("Please provide both video URLs");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/process-videos", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_a_url: videoAUrl,
          video_b_url: videoBUrl,
          use_openai: false,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to process videos");
      }

      const data = await response.json();
      setVideoA(data.video_a);
      setVideoB(data.video_b);
      setProcessed(true);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const resetSystem = async () => {
    try {
      await fetch("http://localhost:8000/api/reset", {
        method: "POST",
      });
      setVideoA(null);
      setVideoB(null);
      setProcessed(false);
      setVideoAUrl("");
      setVideoBUrl("");
      setError("");
    } catch (err) {
      console.error("Failed to reset:", err);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Video RAG Chatbot
          </h1>
          <p className="text-gray-400">
            AI-powered video analytics with LangChain & ChromaDB
          </p>
        </div>

        {/* Input Section */}
        {!processed && (
          <div className="max-w-3xl mx-auto mb-8 bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Video A URL (YouTube/Instagram)
                </label>
                <input
                  type="text"
                  value={videoAUrl}
                  onChange={(e) => setVideoAUrl(e.target.value)}
                  placeholder="https://youtube.com/watch?v=..."
                  className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Video B URL (YouTube/Instagram)
                </label>
                <input
                  type="text"
                  value={videoBUrl}
                  onChange={(e) => setVideoBUrl(e.target.value)}
                  placeholder="https://youtube.com/watch?v=..."
                  className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-900/50 border border-red-700 rounded-lg text-red-300 text-sm">
                {error}
              </div>
            )}

            <button
              onClick={processVideos}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Processing Videos...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Process Videos
                </>
              )}
            </button>
          </div>
        )}

        {/* Video Cards */}
        {processed && videoA && videoB && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <VideoCard video={videoA} label="Video A" />
              <VideoCard video={videoB} label="Video B" />
            </div>

            {/* Reset Button */}
            <div className="text-center mb-8">
              <button
                onClick={resetSystem}
                className="bg-gray-700 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Reset & Analyze New Videos
              </button>
            </div>

            {/* Chat Panel */}
            <ChatPanel />
          </>
        )}
      </div>
    </main>
  );
}
