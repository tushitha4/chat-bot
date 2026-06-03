from typing import Dict, Any


class EngagementCalculator:
    @staticmethod
    def calculate_engagement_rate(metadata: Dict[str, Any]) -> float:
        """Calculate engagement rate = (likes + comments) / views * 100"""
        try:
            views = metadata.get("views", 0)
            likes = metadata.get("likes", 0)
            comments = metadata.get("comments", 0)
            
            if views == 0:
                return 0.0
            
            engagement_rate = ((likes + comments) / views) * 100
            return round(engagement_rate, 2)
        except Exception:
            return 0.0
    
    @staticmethod
    def compare_videos(video_a: Dict[str, Any], video_b: Dict[str, Any]) -> Dict[str, Any]:
        """Compare engagement metrics between two videos."""
        rate_a = EngagementCalculator.calculate_engagement_rate(video_a.get("metadata", {}))
        rate_b = EngagementCalculator.calculate_engagement_rate(video_b.get("metadata", {}))
        
        return {
            "video_a_engagement_rate": rate_a,
            "video_b_engagement_rate": rate_b,
            "difference": round(rate_a - rate_b, 2),
            "winner": "A" if rate_a > rate_b else "B" if rate_b > rate_a else "Tie"
        }
