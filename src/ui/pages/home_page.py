"""Home page - main dashboard with sidebar navigation."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

import flet as ft

from src.models.newsletter import Newsletter
from src.services.fetch_queue_service import FetchPriority
from src.services.newsletter_service import NewsletterService
from src.ui.components import NewsletterCard, Sidebar
from src.ui.components.newsletter_list_item import NewsletterListItem
from src.ui.components.search_bar import SearchBar
from src.ui.components.sort_dropdown import SortDropdown
from src.ui.components.view_mode_toggle import ViewModeToggle
from src.ui.themes import BorderRadius, Colors, Spacing, Typography

if TYPE_CHECKING:
    from src.app import NewsletterApp


class HomePage(ft.View):
    """Main dashboard showing newsletter overview with sidebar."""

    def __init__(self, app: "NewsletterApp"):
        super().__init__(route="/home", padding=0, spacing=0)
        self.app = app
        self.newsletters: List[Newsletter] = []

        # View state
        self.view_mode = "grid"
        self.search_query = ""
        self.sort_by = "recent"

        # Grid view
        self.newsletters_grid = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=350,
            child_aspect_ratio=1.3,
            spacing=Spacing.MD,
            run_spacing=Spacing.MD,
            padding=0,
        )

        # List view
        self.newsletters_list = ft.ListView(
            expand=True,
            spacing=0,
            padding=0,
        )

        # Search, sort, and view controls
        self.search_bar = SearchBar(
            placeholder="Search newsletters...",
            on_change=self._on_search_change,
        )

        self.sort_dropdown = SortDropdown(
            current_sort=self.sort_by,
            on_change=self._on_sort_change,
        )

        self.view_toggle = ViewModeToggle(
            current_mode=self.view_mode,
            on_change=self._on_view_mode_change,
        )

        self.loading = ft.ProgressRing(
            visible=False,
            width=20,
            height=20,
            stroke_width=2,
            color=Colors.Light.ACCENT,
        )

        self.empty_state = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.INBOX_OUTLINED,
                        size=48,
                        color=Colors.Light.TEXT_TERTIARY,
                    ),
                    ft.Container(height=Spacing.MD),
                    ft.Text(
                        "No newsletters yet",
                        size=Typography.H4_SIZE,
                        weight=ft.FontWeight.W_500,
                        color=Colors.Light.TEXT_SECONDARY,
                    ),
                    ft.Container(height=Spacing.XS),
                    ft.Text(
                        "Add a newsletter to get started",
                        size=Typography.BODY_SIZE,
                        color=Colors.Light.TEXT_TERTIARY,
                    ),
                    ft.Container(height=Spacing.LG),
                    ft.ElevatedButton(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.ADD, size=18, color="#FFFFFF"),
                                ft.Container(width=Spacing.XS),
                                ft.Text("Add Newsletter"),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        bgcolor=Colors.Light.ACCENT,
                        color="#FFFFFF",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                        ),
                        on_click=lambda _: self.app.navigate("/newsletters"),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.alignment.Alignment.CENTER,
            visible=False,
        )

        self.sidebar = Sidebar(
            current_route="/home",
            newsletters=[],
            on_navigate=self._handle_navigate,
        )

        self.controls = [self._build_content()]

        # Load newsletters
        self.app.page.run_task(self._load_newsletters)

    def _build_content(self) -> ft.Control:
        """Build page content with sidebar."""
        return ft.Row(
            [
                # Sidebar
                self.sidebar,
                # Main content
                ft.Container(
                    content=ft.Column(
                        [
                            # Page header
                            ft.Container(
                                content=ft.Column(
                                    [
                                        # Title row
                                        ft.Row(
                                            [
                                                ft.Text(
                                                    "Home",
                                                    size=Typography.H1_SIZE,
                                                    weight=ft.FontWeight.W_600,
                                                    color=Colors.Light.TEXT_PRIMARY,
                                                ),
                                                ft.Container(expand=True),
                                                self.loading,
                                                ft.Container(width=Spacing.SM),
                                                ft.IconButton(
                                                    icon=ft.Icons.REFRESH,
                                                    icon_color=Colors.Light.TEXT_SECONDARY,
                                                    icon_size=20,
                                                    tooltip="Refresh all",
                                                    style=ft.ButtonStyle(
                                                        shape=ft.RoundedRectangleBorder(
                                                            radius=BorderRadius.SM
                                                        ),
                                                    ),
                                                    on_click=lambda e: self.app.page.run_task(
                                                        self._on_refresh_all, e
                                                    ),
                                                ),
                                            ],
                                        ),
                                        ft.Container(height=Spacing.MD),
                                        # Controls row
                                        ft.Row(
                                            [
                                                self.search_bar,
                                                ft.Container(expand=True),
                                                self.sort_dropdown,
                                                ft.Container(width=Spacing.SM),
                                                self.view_toggle,
                                            ],
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                    ],
                                ),
                                padding=ft.padding.only(bottom=Spacing.LG),
                            ),
                            # Content area
                            ft.Container(
                                content=ft.Stack(
                                    [
                                        self.newsletters_grid,
                                        self.newsletters_list,
                                        self.empty_state,
                                    ],
                                    expand=True,
                                ),
                                expand=True,
                            ),
                        ],
                        expand=True,
                    ),
                    padding=Spacing.LG,
                    expand=True,
                    bgcolor=Colors.Light.BG_SECONDARY,
                ),
            ],
            expand=True,
            spacing=0,
        )

    def _handle_navigate(self, route: str) -> None:
        """Handle navigation from sidebar."""
        self.app.navigate(route)

    async def _load_newsletters(self) -> None:
        """Load newsletters from database."""
        self.loading.visible = True
        self.app.page.update()

        try:
            async with self.app.get_session() as session:
                service = NewsletterService(
                    session=session,
                    gmail_service=self.app.gmail_service,
                )
                self.newsletters = list(await service.get_all_newsletters())

            self._render_newsletters()

            if self.newsletters:
                # Update sidebar with newsletters
                self.sidebar.update_newsletters(self.newsletters)

        except Exception as ex:
            self.app.show_snackbar(f"Error loading newsletters: {ex}", error=True)
        finally:
            self.loading.visible = False
            self.app.page.update()

    def _create_newsletter_card(self, newsletter: Newsletter) -> ft.Control:
        """Create a card for a newsletter."""
        return NewsletterCard(
            name=newsletter.name,
            label=newsletter.gmail_label_name,
            unread_count=newsletter.unread_count,
            total_count=newsletter.total_count,
            last_email_received_at=newsletter.last_email_received_at,
            color=newsletter.color,
            on_click=lambda _, nid=newsletter.id: self.app.navigate(
                f"/newsletter/{nid}"
            ),
            on_refresh=lambda _, nid=newsletter.id: self.app.page.run_task(
                self._fetch_newsletter, nid
            ),
        )

    def _create_newsletter_list_item(self, newsletter: Newsletter) -> ft.Control:
        """Create a list item for a newsletter."""
        return NewsletterListItem(
            name=newsletter.name,
            label=newsletter.gmail_label_name,
            unread_count=newsletter.unread_count,
            total_count=newsletter.total_count,
            last_email_received_at=newsletter.last_email_received_at,
            color=newsletter.color,
            on_click=lambda _, nid=newsletter.id: self.app.navigate(
                f"/newsletter/{nid}"
            ),
            on_refresh=lambda _, nid=newsletter.id: self.app.page.run_task(
                self._fetch_newsletter, nid
            ),
        )

    async def _on_refresh_all(self, e: ft.ControlEvent) -> None:
        """Refresh all newsletters."""
        if not self.app.fetch_queue_service:
            return

        async with self.app.get_session() as session:
            service = NewsletterService(session=session)
            newsletters = await service.get_all_newsletters()
            ids = [n.id for n in newsletters]

        queued = await self.app.fetch_queue_service.queue_all_newsletters(
            ids, FetchPriority.HIGH
        )

        self.app.show_snackbar(f"Queued {queued} newsletters for refresh")

    async def _fetch_newsletter(self, newsletter_id: int) -> None:
        """Fetch a single newsletter."""
        if not self.app.fetch_queue_service:
            return

        await self.app.fetch_queue_service.queue_fetch(newsletter_id, FetchPriority.HIGH)
        self.app.show_snackbar("Newsletter queued for refresh")

    def _on_search_change(self, query: str) -> None:
        """Handle search query change."""
        self.search_query = query
        self._render_newsletters()
        self.app.page.update()

    def _on_sort_change(self, sort_by: str) -> None:
        """Handle sort selection change."""
        self.sort_by = sort_by
        self._render_newsletters()
        self.app.page.update()

    def _on_view_mode_change(self, mode: str) -> None:
        """Handle view mode toggle."""
        self.view_mode = mode
        self._render_newsletters()
        self.app.page.update()

    def _filter_and_sort_newsletters(self) -> List[Newsletter]:
        """Filter and sort newsletters based on current state."""
        result = self.newsletters

        # Filter by search query
        if self.search_query:
            query = self.search_query.lower()
            result = [n for n in result if query in n.name.lower()]

        # Sort
        if self.sort_by == "recent":
            result = sorted(
                result,
                key=lambda n: n.last_email_received_at or datetime.min.replace(
                    tzinfo=timezone.utc
                ),
                reverse=True,
            )
        elif self.sort_by == "unread":
            result = sorted(result, key=lambda n: n.unread_count, reverse=True)
        elif self.sort_by == "name_asc":
            result = sorted(result, key=lambda n: n.name.lower())
        elif self.sort_by == "name_desc":
            result = sorted(result, key=lambda n: n.name.lower(), reverse=True)

        return result

    def _render_newsletters(self) -> None:
        """Render newsletters in current view mode."""
        filtered = self._filter_and_sort_newsletters()

        # Clear both views
        self.newsletters_grid.controls.clear()
        self.newsletters_list.controls.clear()

        if not filtered:
            self.newsletters_grid.visible = False
            self.newsletters_list.visible = False
            self.empty_state.visible = True
            return

        self.empty_state.visible = False

        if self.view_mode == "grid":
            for newsletter in filtered:
                card = self._create_newsletter_card(newsletter)
                self.newsletters_grid.controls.append(card)
            self.newsletters_grid.visible = True
            self.newsletters_list.visible = False
        else:  # list mode
            for newsletter in filtered:
                item = self._create_newsletter_list_item(newsletter)
                self.newsletters_list.controls.append(item)
            self.newsletters_grid.visible = False
            self.newsletters_list.visible = True
