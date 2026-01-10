"""Tests for time utility functions."""

from datetime import datetime, timedelta, timezone

import pytest

from src.ui.utils.time_utils import format_relative_time


class TestFormatRelativeTime:
    """Tests for format_relative_time function."""

    def test_none_input_returns_never(self):
        """Test that None input returns 'Never'."""
        assert format_relative_time(None) == "Never"

    def test_just_now_for_recent_time(self):
        """Test that very recent time returns 'Just now'."""
        now = datetime.now(timezone.utc)
        assert format_relative_time(now) == "Just now"
        assert format_relative_time(now - timedelta(seconds=30)) == "Just now"

    def test_minutes_ago(self):
        """Test minutes ago formatting."""
        now = datetime.now(timezone.utc)
        assert format_relative_time(now - timedelta(minutes=1)) == "1 min ago"
        assert format_relative_time(now - timedelta(minutes=5)) == "5 min ago"
        assert format_relative_time(now - timedelta(minutes=59)) == "59 min ago"

    def test_hours_ago(self):
        """Test hours ago formatting."""
        now = datetime.now(timezone.utc)
        assert format_relative_time(now - timedelta(hours=1)) == "1 hour ago"
        assert format_relative_time(now - timedelta(hours=2)) == "2 hours ago"
        assert format_relative_time(now - timedelta(hours=23)) == "23 hours ago"

    def test_yesterday(self):
        """Test yesterday formatting."""
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        assert format_relative_time(yesterday) == "Yesterday"

    def test_days_ago(self):
        """Test days ago formatting."""
        now = datetime.now(timezone.utc)
        assert format_relative_time(now - timedelta(days=2)) == "2 days ago"
        assert format_relative_time(now - timedelta(days=6)) == "6 days ago"

    def test_weeks_ago(self):
        """Test weeks ago formatting."""
        now = datetime.now(timezone.utc)
        assert format_relative_time(now - timedelta(days=7)) == "1 week ago"
        assert format_relative_time(now - timedelta(days=14)) == "2 weeks ago"
        assert format_relative_time(now - timedelta(days=28)) == "4 weeks ago"

    def test_older_dates_show_date(self):
        """Test that older dates show the actual date."""
        now = datetime.now(timezone.utc)
        old_date = now - timedelta(days=45)
        result = format_relative_time(old_date)
        # Should contain month abbreviation like "Jan", "Feb", etc.
        assert len(result) > 0
        assert result != "Never"

    def test_naive_datetime_handled(self):
        """Test that naive datetime is handled correctly."""
        naive_dt = datetime.now() - timedelta(hours=2)
        result = format_relative_time(naive_dt)
        assert "hour" in result

    def test_future_time_returns_just_now(self):
        """Test that future time returns 'Just now'."""
        future = datetime.now(timezone.utc) + timedelta(hours=1)
        assert format_relative_time(future) == "Just now"
