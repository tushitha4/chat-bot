import { Eye, Heart, MessageCircle, Clock, User } from "lucide-react";

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

interface VideoCardProps {
  video: VideoData;
  label: string;
}

export default function VideoCard({ video, label }: VideoCardProps) {
  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
    if (num >= 1000) return (num / 1000).toFixed(1) + "K";
    return num.toString();
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return "N/A";
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString();
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="bg-gray-800/50 backdrop-blur rounded-xl border border-gray-700 overflow-hidden">
      {/* Label */}
      <div className="bg-blue-600 px-4 py-2">
        <span className="text-white font-semibold">{label}</span>
      </div>

      {/* Thumbnail */}
      {video.metadata.thumbnail && (
        <div className="relative aspect-video bg-gray-900">
          <img
            src={video.metadata.thumbnail}
            alt={video.metadata.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-1 rounded text-white text-xs">
            {formatDuration(video.metadata.duration)}
          </div>
        </div>
      )}

      {/* Content */}
      <div className="p-4">
        <h3 className="text-white font-semibold text-lg mb-2 line-clamp-2">
          {video.metadata.title}
        </h3>

        <div className="flex items-center gap-2 text-gray-400 text-sm mb-3">
          <User className="w-4 h-4" />
          <span>{video.metadata.creator}</span>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="bg-gray-900/50 rounded-lg p-3 text-center">
            <Eye className="w-5 h-5 text-blue-400 mx-auto mb-1" />
            <div className="text-white font-semibold">{formatNumber(video.metadata.views)}</div>
            <div className="text-gray-500 text-xs">Views</div>
          </div>
          <div className="bg-gray-900/50 rounded-lg p-3 text-center">
            <Heart className="w-5 h-5 text-red-400 mx-auto mb-1" />
            <div className="text-white font-semibold">{formatNumber(video.metadata.likes)}</div>
            <div className="text-gray-500 text-xs">Likes</div>
          </div>
          <div className="bg-gray-900/50 rounded-lg p-3 text-center">
            <MessageCircle className="w-5 h-5 text-green-400 mx-auto mb-1" />
            <div className="text-white font-semibold">{formatNumber(video.metadata.comments)}</div>
            <div className="text-gray-500 text-xs">Comments</div>
          </div>
        </div>

        {/* Engagement Rate */}
        <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-lg p-3 border border-blue-500/30">
          <div className="flex items-center justify-between">
            <span className="text-gray-300 text-sm">Engagement Rate</span>
            <span className="text-2xl font-bold text-blue-400">
              {video.engagement_rate.toFixed(2)}%
            </span>
          </div>
        </div>

        {/* Additional Info */}
        <div className="mt-3 pt-3 border-t border-gray-700 flex items-center justify-between text-gray-500 text-xs">
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            <span>{formatDate(video.metadata.upload_date)}</span>
          </div>
          <span>ID: {video.video_id}</span>
        </div>
      </div>
    </div>
  );
}
