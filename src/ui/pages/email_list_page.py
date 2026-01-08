"""Email list page for a newsletter."""

from typing import TYPE_CHECKING

import flet as ft

from src.services.email_service import EmailService
from src.services.fetch_queue_service import FetchPriority
from src.services.newsletter_service import NewsletterService

if TYPE_CHECKING:
    from src.app import NewsletterApp


class EmailListPage(ft.View):
    """Page showing emails for a newsletter."""

    def __init__(self, app: "NewsletterApp", newsletter_id: int):
        super().__init__(route=f"/newsletter/{newsletter_id}")
        self.app = app
        self.newsletter_id = newsletter_id
        self.newsletter = None

        self.emails_list = ft.ListView(
            expand=True,
            spacing=4,
        )
        self.loading = ft.ProgressRing(visible=False)
        self.title_text = ft.Text("Loading...", size=20, weight=ft.FontWeight.BOLD)

        self.appbar = ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda _: self.app.navigate("/home"),
            ),
            title=self.title_text,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Fetch new emails",
                    on_click=lambda e: self.app.page.run_task(
                        self._on_refresh, e
                    ),
                ),
            ],
        )

        self.controls = [self._build_content()]

        # Load emails
        self.app.page.run_task(self._load_data)

    def _build_content(self) -> ft.Control:
        """Build page content."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            self.loading,
                        ],
                    ),
                    self.emails_list,
                ],
                expand=True,
            ),
            padding=24,
            expand=True,
        )

    async def _load_data(self) -> None:
        """Load newsletter and emails."""
        self.loading.visible = True
        self.app.page.update()

        try:
            async with self.app.get_session() as session:
                # Load newsletter
                newsletter_service = NewsletterService(session=session)
                self.newsletter = await newsletter_service.get_newsletter(
                    self.newsletter_id
                )

                if not self.newsletter:
                    self.app.show_snackbar("Newsletter not found", error=True)
                    self.app.navigate("/home")
                    return

                self.title_text.value = self.newsletter.name

                # Load emails
                email_service = EmailService(session)
                emails = await email_service.get_emails_for_newsletter(
                    self.newsletter_id, limit=100
                )

            self.emails_list.controls.clear()

            if emails:
                for email in emails:
                    tile = self._create_email_tile(email)
                    self.emails_list.controls.append(tile)
            else:
                self.emails_list.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.Icons.INBOX_OUTLINED,
                                    size=48,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                                ft.Text(
                                    "No emails yet",
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                                ft.TextButton(
                                    "Fetch Now",
                                    on_click=lambda e: self.app.page.run_task(
                                        self._on_refresh, e
                                    ),
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=48,
                        alignment=ft.Alignment.CENTER,
                    )
                )

        except Exception as ex:
            self.app.show_snackbar(f"Error: {ex}", error=True)
        finally:
            self.loading.visible = False
            self.app.page.update()

    def _create_email_tile(self, email) -> ft.Control:
        """Create a list tile for an email."""
        # Format date
        date_str = email.received_at.strftime("%b %d, %Y")

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.STAR if email.is_starred else ft.Icons.STAR_BORDER,
                            color=ft.Colors.AMBER if email.is_starred else None,
                            size=20,
                        ),
                        on_click=lambda _, eid=email.id: self.app.page.run_task(
                            self._toggle_star, eid
                        ),
                    ),
                    ft.Container(width=8),
                    ft.Container(
                        width=8,
                        height=8,
                        border_radius=4,
                        bgcolor=ft.Colors.PRIMARY if not email.is_read else None,
                    ),
                    ft.Container(width=12),
                    ft.Column(
                        [
                            ft.Text(
                                email.subject,
                                size=14,
                                weight=ft.FontWeight.BOLD
                                if not email.is_read
                                else ft.FontWeight.NORMAL,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                email.sender_name or email.sender_email,
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                email.snippet or "",
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Text(
                        date_str,
                        size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
            ),
            padding=12,
            border_radius=8,
            on_click=lambda _, eid=email.id: self.app.navigate(f"/email/{eid}"),
            bgcolor=ft.Colors.SURFACE_VARIANT if not email.is_read else None,
        )

    async def _on_refresh(self, e: ft.ControlEvent) -> None:
        """Fetch new emails."""
        if not self.app.fetch_queue_service:
            return

        await self.app.fetch_queue_service.queue_fetch(
            self.newsletter_id, FetchPriority.HIGH
        )
        self.app.show_snackbar("Fetching new emails...")

        # Wait a bit and reload
        import asyncio
        await asyncio.sleep(2)
        await self._load_data()

    async def _toggle_star(self, email_id: int) -> None:
        """Toggle email starred status."""
        try:
            async with self.app.get_session() as session:
                email_service = EmailService(session)
                await email_service.toggle_starred(email_id)
            await self._load_data()
        except Exception as ex:
            self.app.show_snackbar(f"Error: {ex}", error=True)
