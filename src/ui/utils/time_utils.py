"""Time formatting utilities."""

from datetime import datetime, timezone
from typing import Optional


def format_relative_time(dt: Optional[datetime]) -> str:
    """Format datetime as a human-readable relative time string.

    Args:
        dt: Datetime to format (should be timezone-aware).

    Returns:
        Relative time string like "Just now", "5 min ago", "2 hours ago",
        "Yesterday", "3 days ago", or "Jan 5" for older dates.
    """
    if not dt:
        return "Never"

    # Ensure we're comparing timezone-aware datetimes
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 0:
        return "Just now"
    if seconds < 60:
        return "Just now"
    if seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} min ago"
    if seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    if diff.days == 1:
        return "Yesterday"
    if diff.days < 7:
        return f"{diff.days} days ago"
    if diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"

    # For older dates, show the actual date
    return dt.strftime("%b %d")
