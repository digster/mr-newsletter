"""Sidebar navigation component with newsletter list."""

from typing import TYPE_CHECKING, Callable, Optional, Union

import flet as ft

from src.ui.themes import BorderRadius, Colors, Spacing, Typography, get_colors

if TYPE_CHECKING:
    pass


class NavItem(ft.Container):
    """Navigation item with icon and label."""

    def __init__(
        self,
        icon: str,
        icon_filled: str,
        label: str,
        route: str,
        is_active: bool = False,
        on_click: Optional[Callable] = None,
        badge_count: Optional[int] = None,
        colors: Optional[Union[type[Colors.Light], type[Colors.Dark]]] = None,
    ):
        self.route = route
        self.is_active = is_active
        self._on_click = on_click
        self._colors = colors or Colors.Light

        # Build badge if needed
        badge = None
        if badge_count and badge_count > 0:
            badge = ft.Container(
                content=ft.Text(
                    str(badge_count) if badge_count < 100 else "99+",
                    size=11,
                    color="#FFFFFF",
                    weight=ft.FontWeight.W_500,
                ),
                bgcolor=self._colors.ACCENT,
                border_radius=BorderRadius.FULL,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
            )

        super().__init__(
            content=ft.Row(
                [
                    ft.Icon(
                        icon_filled if is_active else icon,
                        size=20,
                        color=self._colors.TEXT_PRIMARY
                        if is_active
                        else self._colors.TEXT_SECONDARY,
                    ),
                    ft.Container(width=Spacing.SM),
                    ft.Text(
                        label,
                        size=Typography.BODY_SIZE,
                        weight=ft.FontWeight.W_500
                        if is_active
                        else ft.FontWeight.W_400,
                        color=self._colors.TEXT_PRIMARY
                        if is_active
                        else self._colors.TEXT_SECONDARY,
                        expand=True,
                    ),
                    badge if badge else ft.Container(),
                ],
            ),
            padding=ft.padding.symmetric(horizontal=Spacing.SM, vertical=Spacing.XS),
            border_radius=BorderRadius.SM,
            bgcolor=self._colors.BG_TERTIARY if is_active else None,
            on_click=self._handle_click,
            on_hover=self._on_hover,
        )

    def _handle_click(self, e: ft.ControlEvent) -> None:
        if self._on_click:
            self._on_click(self.route)

    def _on_hover(self, e: ft.HoverEvent) -> None:
        if not self.is_active:
            self.bgcolor = self._colors.HOVER if e.data == "true" else None
            self.update()


class NewsletterNavItem(ft.Container):
    """Newsletter navigation item with colored background."""

    def __init__(
        self,
        newsletter_id: int,
        name: str,
        color: str,
        color_secondary: Optional[str] = None,
        unread_count: int = 0,
        is_active: bool = False,
        on_click: Optional[Callable] = None,
    ):
        self.newsletter_id = newsletter_id
        self.is_active = is_active
        self._on_click = on_click
        self._color = color
        self._color_secondary = color_secondary

        # Determine background (gradient or solid)
        if color_secondary:
            bg_gradient = ft.LinearGradient(
                begin=ft.Alignment(-1, -1),  # top-left
                end=ft.Alignment(1, 1),      # bottom-right
                colors=[color, color_secondary],
            )
            bg_color = None
        else:
            bg_gradient = None
            bg_color = color

        # Store for hover state management
        self._bg_gradient = bg_gradient
        self._bg_color = bg_color

        super().__init__(
            content=ft.Row(
                [
                    # Name (white text for contrast on colored bg)
                    ft.Text(
                        name,
                        size=Typography.BODY_SMALL_SIZE,
                        weight=ft.FontWeight.W_500,
                        color="#FFFFFF",
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True,
                    ),
                    # Unread count (white text)
                    ft.Container(
                        content=ft.Text(
                            str(unread_count),
                            size=Typography.CAPTION_SIZE,
                            color="#FFFFFF",
                            weight=ft.FontWeight.W_600,
                        ),
                        bgcolor="rgba(255, 255, 255, 0.25)",
                        border_radius=BorderRadius.FULL,
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    )
                    if unread_count > 0
                    else ft.Container(),
                ],
            ),
            padding=ft.padding.symmetric(horizontal=Spacing.SM, vertical=6),
            border_radius=BorderRadius.SM,
            bgcolor=bg_color,
            gradient=bg_gradient,
            border=ft.border.all(2, "#FFFFFF") if is_active else None,
            on_click=self._handle_click,
            on_hover=self._on_hover,
        )

    def _handle_click(self, e: ft.ControlEvent) -> None:
        if self._on_click:
            self._on_click(f"/newsletter/{self.newsletter_id}")

    def _on_hover(self, e: ft.HoverEvent) -> None:
        if not self.is_active:
            if e.data == "true":
                # Add subtle border on hover
                self.border = ft.border.all(1, "rgba(255, 255, 255, 0.5)")
            else:
                self.border = None
            self.update()


class Sidebar(ft.Container):
    """Persistent sidebar navigation component."""

    WIDTH = 240

    def __init__(
        self,
        current_route: str,
        newsletters: Optional[list] = None,
        on_navigate: Optional[Callable] = None,
        user_email: Optional[str] = None,
        page: Optional[ft.Page] = None,
    ):
        self.current_route = current_route
        self.newsletters = newsletters or []
        self.on_navigate = on_navigate
        self.user_email = user_email
        self._colors = get_colors(page) if page else Colors.Light

        super().__init__(
            content=self._build_content(),
            width=self.WIDTH,
            bgcolor=self._colors.BG_PRIMARY,
            border=ft.border.only(right=ft.BorderSide(1, self._colors.BORDER_DEFAULT)),
            padding=ft.padding.symmetric(vertical=Spacing.MD, horizontal=Spacing.SM),
        )

    def _build_content(self) -> ft.Control:
        """Build sidebar content."""
        return ft.Column(
            [
                # Logo/Brand
                self._build_header(),
                ft.Container(height=Spacing.LG),
                # Primary nav
                NavItem(
                    icon=ft.Icons.HOME_OUTLINED,
                    icon_filled=ft.Icons.HOME,
                    label="Home",
                    route="/home",
                    is_active=self.current_route == "/home",
                    on_click=self.on_navigate,
                    colors=self._colors,
                ),
                ft.Container(height=Spacing.LG),
                # Newsletters section
                self._build_newsletters_section(),
                # Spacer
                ft.Container(expand=True),
                # Footer nav
                ft.Divider(height=1, color=self._colors.BORDER_SUBTLE),
                ft.Container(height=Spacing.SM),
                NavItem(
                    icon=ft.Icons.FOLDER_OUTLINED,
                    icon_filled=ft.Icons.FOLDER,
                    label="Manage",
                    route="/newsletters",
                    is_active=self.current_route == "/newsletters",
                    on_click=self.on_navigate,
                    colors=self._colors,
                ),
                NavItem(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    icon_filled=ft.Icons.SETTINGS,
                    label="Settings",
                    route="/settings",
                    is_active=self.current_route == "/settings",
                    on_click=self.on_navigate,
                    colors=self._colors,
                ),
            ],
            expand=True,
            spacing=2,
        )

    def _build_header(self) -> ft.Control:
        """Build logo/header area."""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.MARK_EMAIL_READ,
                        size=24,
                        color=self._colors.ACCENT,
                    ),
                    ft.Container(width=Spacing.XS),
                    ft.Text(
                        "Newsletter",
                        size=Typography.H4_SIZE,
                        weight=ft.FontWeight.W_600,
                        color=self._colors.TEXT_PRIMARY,
                    ),
                ],
            ),
            padding=ft.padding.symmetric(horizontal=Spacing.XS, vertical=Spacing.XS),
        )

    def _build_newsletters_section(self) -> ft.Control:
        """Build newsletters list section."""
        if not self.newsletters:
            return ft.Container()

        newsletter_items = []
        for nl in self.newsletters:
            is_active = self.current_route == f"/newsletter/{nl.id}"
            newsletter_items.append(
                NewsletterNavItem(
                    newsletter_id=nl.id,
                    name=nl.name,
                    color=nl.color or self._colors.ACCENT,
                    color_secondary=nl.color_secondary,
                    unread_count=nl.unread_count,
                    is_active=is_active,
                    on_click=self.on_navigate,
                )
            )

        return ft.Column(
            [
                # Section header
                ft.Container(
                    content=ft.Text(
                        "NEWSLETTERS",
                        size=11,
                        weight=ft.FontWeight.W_500,
                        color=self._colors.TEXT_TERTIARY,
                    ),
                    padding=ft.padding.only(left=Spacing.SM, bottom=Spacing.XS),
                ),
                # Newsletter list (scrollable if many)
                ft.Column(
                    newsletter_items,
                    spacing=2,
                    scroll=ft.ScrollMode.AUTO if len(newsletter_items) > 8 else None,
                ),
            ],
            spacing=0,
        )

    def update_newsletters(self, newsletters: list) -> None:
        """Update the newsletters list."""
        self.newsletters = newsletters
        self.content = self._build_content()
        self.update()

    def update_route(self, route: str) -> None:
        """Update the current route."""
        self.current_route = route
        self.content = self._build_content()
        self.update()
