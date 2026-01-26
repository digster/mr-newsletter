"""Summary card component for displaying AI-generated email summaries."""

from collections.abc import Callable
from datetime import datetime

import flet as ft

from src.ui.themes import BorderRadius, Colors, Spacing, Typography


class SummaryCard(ft.Container):
    """Collapsible card for displaying AI-generated email summaries.

    Has three states:
    - Empty: Shows "Generate AI Summary" button
    - Loading: Shows progress ring with "Generating summary..."
    - Summary: Shows collapsible card with summary content
    """

    def __init__(
        self,
        summary: str | None = None,
        model: str | None = None,
        summarized_at: datetime | None = None,
        on_generate: Callable | None = None,
        on_regenerate: Callable | None = None,
        colors: type[Colors.Light] | type[Colors.Dark] | None = None,
        is_enabled: bool = True,
    ):
        """Initialize summary card.

        Args:
            summary: Existing summary text (if any).
            model: Model name that generated the summary.
            summarized_at: When the summary was generated.
            on_generate: Callback for generating a new summary.
            on_regenerate: Callback for regenerating the summary.
            colors: Theme colors to use.
            is_enabled: Whether LLM is enabled (shows different empty state if disabled).
        """
        self.summary = summary
        self.model = model
        self.summarized_at = summarized_at
        self._on_generate = on_generate
        self._on_regenerate = on_regenerate
        self._colors = colors or Colors.Light
        self._is_enabled = is_enabled
        self._is_loading = False
        self._is_collapsed = False

        super().__init__(
            content=self._build_content(),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )

    def _build_content(self) -> ft.Control:
        """Build the appropriate content based on state."""
        try:
            if self._is_loading:
                return self._build_loading_state()
            elif self.summary is not None:  # Use `is not None` - empty string "" is falsy but valid!
                return self._build_summary_state()
            else:
                return self._build_empty_state()
        except Exception as e:
            import logging

            logging.error(f"SummaryCard build error: {e}", exc_info=True)
            # Return empty container on error to prevent Column from breaking
            return ft.Container()

    def _build_empty_state(self) -> ft.Control:
        """Build empty state with generate button."""
        c = self._colors

        if not self._is_enabled:
            # Show disabled state hint
            return ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.AUTO_AWESOME_OUTLINED,
                            size=16,
                            color=c.TEXT_TERTIARY,
                        ),
                        ft.Container(width=Spacing.XS),
                        ft.Text(
                            "AI Summarization disabled",
                            size=Typography.CAPTION_SIZE,
                            color=c.TEXT_TERTIARY,
                            italic=True,
                        ),
                        ft.Container(width=Spacing.XS),
                        ft.Text(
                            "Enable in Settings",
                            size=Typography.CAPTION_SIZE,
                            color=c.ACCENT,
                            weight=ft.FontWeight.W_500,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(vertical=Spacing.SM),
            )

        # When enabled: return empty container (no hint text)
        # The sparkle button in the toolbar handles summary generation
        return ft.Container()

    def _build_loading_state(self) -> ft.Control:
        """Build loading state with progress indicator."""
        c = self._colors

        return ft.Container(
            content=ft.Row(
                [
                    ft.ProgressRing(
                        width=16,
                        height=16,
                        stroke_width=2,
                        color=c.ACCENT,
                    ),
                    ft.Container(width=Spacing.SM),
                    ft.Text(
                        "Generating summary...",
                        size=Typography.BODY_SMALL_SIZE,
                        color=c.TEXT_SECONDARY,
                        italic=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=Spacing.MD),
        )

    def _build_summary_state(self) -> ft.Control:
        """Build summary display state with collapsible content."""
        c = self._colors

        # Format the summarized_at timestamp
        time_str = ""
        if self.summarized_at:
            time_str = self.summarized_at.strftime("%b %d, %H:%M")

        # Header row with collapse/expand and regenerate controls
        header = ft.Row(
            [
                # Sparkle icon and title
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.AUTO_AWESOME,
                            size=16,
                            color=c.ACCENT,
                        ),
                        ft.Container(width=Spacing.XS),
                        ft.Text(
                            "AI Summary",
                            size=Typography.BODY_SMALL_SIZE,
                            weight=ft.FontWeight.W_600,
                            color=c.TEXT_PRIMARY,
                        ),
                    ],
                    spacing=0,
                ),
                ft.Container(expand=True),
                # Collapse/expand toggle
                ft.IconButton(
                    icon=ft.Icons.EXPAND_LESS if not self._is_collapsed else ft.Icons.EXPAND_MORE,
                    icon_size=18,
                    icon_color=c.TEXT_SECONDARY,
                    tooltip="Collapse" if not self._is_collapsed else "Expand",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                        padding=Spacing.XXS,
                    ),
                    on_click=self._toggle_collapse,
                ),
                # Regenerate button
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    icon_size=16,
                    icon_color=c.TEXT_SECONDARY,
                    tooltip="Regenerate summary",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                        padding=Spacing.XXS,
                    ),
                    on_click=self._handle_regenerate,
                ),
            ],
        )

        # Summary content (hidden when collapsed)
        content_container = ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=Spacing.SM),
                    # Summary text
                    ft.Text(
                        self.summary,
                        size=Typography.BODY_SIZE,
                        color=c.TEXT_SECONDARY,
                    ),
                    ft.Container(height=Spacing.SM),
                    # Metadata row
                    ft.Row(
                        [
                            ft.Text(
                                f"Generated by {self.model or 'AI'}"
                                + (f" \u2022 {time_str}" if time_str else ""),
                                size=Typography.CAPTION_SIZE,
                                color=c.TEXT_TERTIARY,
                                italic=True,
                            ),
                        ],
                    ),
                ],
                spacing=0,
            ),
            visible=not self._is_collapsed,
            animate_opacity=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )

        return ft.Container(
            content=ft.Column(
                [
                    header,
                    content_container,
                ],
                spacing=0,
            ),
            padding=Spacing.MD,
            border_radius=BorderRadius.MD,
            border=ft.border.all(1, c.BORDER_DEFAULT),
            bgcolor=c.BG_TERTIARY,
        )

    def _handle_generate(self, e: ft.ControlEvent) -> None:
        """Handle generate button click."""
        if self._on_generate:
            self._on_generate(e)

    def _handle_regenerate(self, e: ft.ControlEvent) -> None:
        """Handle regenerate button click."""
        if self._on_regenerate:
            self._on_regenerate(e)

    def _toggle_collapse(self, e: ft.ControlEvent) -> None:
        """Toggle collapsed state."""
        self._is_collapsed = not self._is_collapsed
        self._safe_update_content()

    def _safe_update_content(self) -> None:
        """Safely update the control's content.

        Flet throws an exception if content is modified or update() is called
        on an unattached control. This method handles both cases gracefully.
        """
        try:
            self.content = self._build_content()
            if self.page is not None:
                self.update()
        except Exception as e:
            # Log at debug level - "control not attached" is expected during initial render
            import logging

            logging.getLogger(__name__).debug(f"SummaryCard update skipped: {e}")

    def set_loading(self, loading: bool) -> None:
        """Set loading state.

        Args:
            loading: Whether to show loading state.
        """
        self._is_loading = loading
        self._safe_update_content()

    def set_summary(
        self,
        summary: str | None,
        model: str | None = None,
        summarized_at: datetime | None = None,
    ) -> None:
        """Update summary content.

        Args:
            summary: Summary text.
            model: Model name that generated the summary.
            summarized_at: When the summary was generated.
        """
        self.summary = summary
        self.model = model
        self.summarized_at = summarized_at
        self._is_loading = False
        self._is_collapsed = False
        self._safe_update_content()

    def set_enabled(self, enabled: bool) -> None:
        """Update enabled state.

        Args:
            enabled: Whether LLM is enabled.
        """
        self._is_enabled = enabled
        self._safe_update_content()

    def clear(self) -> None:
        """Clear the summary and return to empty state."""
        self.summary = None
        self.model = None
        self.summarized_at = None
        self._is_loading = False
        self._is_collapsed = False
        self._safe_update_content()
