import yt_dlp
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi
from typing import Dict, Any, Optional
import instaloader
import re


class TranscriptExtractor:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
    
    def extract_youtube_transcript(self, url: str) -> Dict[str, Any]:
        """Extract transcript and metadata from YouTube video."""
        try:
            # Extract video ID
            video_id = self._extract_youtube_id(url)
            if not video_id:
                return {"error": "Invalid YouTube URL"}
            
            # Get transcript
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript = " ".join([t['text'] for t in transcript_list])
            except Exception as e:
                transcript = f"Transcript not available: {str(e)}"
            
            # Get metadata using yt-dlp
            metadata = self._get_youtube_metadata(url)
            
            return {
                "video_id": video_id,
                "transcript": transcript,
                "metadata": metadata,
                "source": "youtube"
            }
        except Exception as e:
            return {"error": f"Failed to extract YouTube transcript: {str(e)}"}
    
    def extract_instagram_transcript(self, url: str) -> Dict[str, Any]:
        """Extract transcript and metadata from Instagram Reel."""
        try:
            # Instagram doesn't provide transcripts natively
            # We'll extract metadata and note that transcript needs manual input or ASR
            metadata = self._get_instagram_metadata(url)
            
            return {
                "video_id": metadata.get("shortcode", "unknown"),
                "transcript": "Instagram Reels do not have native transcripts. Please use Whisper or AssemblyAI for transcription.",
                "metadata": metadata,
                "source": "instagram"
            }
        except Exception as e:
            return {"error": f"Failed to extract Instagram data: {str(e)}"}
    
    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/shorts\/([^&\n?#]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _get_youtube_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from YouTube video."""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    "title": info.get("title", ""),
                    "views": info.get("view_count", 0),
                    "likes": info.get("like_count", 0),
                    "comments": info.get("comment_count", 0),
                    "creator": info.get("uploader", ""),
                    "uploader_id": info.get("uploader_id", ""),
                    "upload_date": info.get("upload_date", ""),
                    "duration": info.get("duration", 0),
                    "description": info.get("description", ""),
                    "tags": info.get("tags", []),
                    "thumbnail": info.get("thumbnail", "")
                }
        except Exception as e:
            return {"error": f"Failed to get metadata: {str(e)}"}
    
    def _get_instagram_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from Instagram Reel."""
        try:
            L = instaloader.Instaloader()
            shortcode = self._extract_instagram_shortcode(url)
            
            if not shortcode:
                return {"error": "Invalid Instagram URL"}
            
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            return {
                "shortcode": shortcode,
                "title": post.caption or "Instagram Reel",
                "views": post.video_view_count if hasattr(post, 'video_view_count') else 0,
                "likes": post.likes,
                "comments": post.comments,
                "creator": post.owner_username,
                "follower_count": post.owner_followers if hasattr(post, 'owner_followers') else 0,
                "upload_date": post.date_local.isoformat() if post.date_local else "",
                "duration": post.video_duration if hasattr(post, 'video_duration') else 0,
                "caption": post.caption or "",
                "thumbnail": post.url if hasattr(post, 'url') else ""
            }
        except Exception as e:
            return {"error": f"Failed to get Instagram metadata: {str(e)}"}
    
    def _extract_instagram_shortcode(self, url: str) -> Optional[str]:
        """Extract Instagram shortcode from URL."""
        patterns = [
            r'instagram\.com\/reel\/([^\/\?]+)',
            r'instagram\.com\/p\/([^\/\?]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
