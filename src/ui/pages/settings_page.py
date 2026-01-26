"""Settings page for app configuration with sophisticated styling."""

from typing import TYPE_CHECKING

import flet as ft

from src.repositories.user_settings_repository import UserSettingsRepository
from src.services.auth_service import AuthService
from src.services.llm_service import LLMService
from src.services.newsletter_service import NewsletterService
from src.ui.components import ConfirmDialog, Sidebar
from src.ui.themes import BorderRadius, Spacing, Typography, get_colors

if TYPE_CHECKING:
    from src.app import NewsletterApp


class SettingsPage(ft.View):
    """Settings page for app configuration with sidebar."""

    def __init__(self, app: "NewsletterApp"):
        super().__init__(route="/settings", padding=0, spacing=0)
        self.app = app
        self.newsletters = []

        # Get theme-aware colors
        self.colors = get_colors(self.app.page)

        self.user_email_text = ft.Text(
            "Loading...",
            size=Typography.BODY_SIZE,
            color=self.colors.TEXT_SECONDARY,
        )

        # Determine current theme value for dropdown
        theme_value = "system"
        if self.app.page.theme_mode == ft.ThemeMode.LIGHT:
            theme_value = "light"
        elif self.app.page.theme_mode == ft.ThemeMode.DARK:
            theme_value = "dark"

        self.theme_dropdown = ft.Dropdown(
            label="Theme",
            value=theme_value,
            options=[
                ft.dropdown.Option("system", "System"),
                ft.dropdown.Option("light", "Light"),
                ft.dropdown.Option("dark", "Dark"),
            ],
            width=200,
            border_radius=BorderRadius.SM,
            content_padding=ft.padding.symmetric(
                horizontal=Spacing.SM, vertical=Spacing.SM
            ),
            text_size=Typography.BODY_SIZE,
            text_style=ft.TextStyle(
                size=Typography.BODY_SIZE,
                color=self.colors.TEXT_PRIMARY,
            ),
            label_style=ft.TextStyle(
                color=self.colors.TEXT_SECONDARY,
            ),
        )
        self.theme_dropdown.on_select = self._on_theme_change

        # LLM Settings - initialized with defaults, updated in _load_data
        self._llm_enabled = False
        self._llm_api_base_url = "http://localhost:1234/v1"
        self._llm_model = ""
        self._llm_max_tokens = 500
        self._llm_temperature = 0.3
        self._llm_has_api_key = False  # Track if API key is set (don't show actual key)

        # LLM UI controls
        c = self.colors
        self.llm_enabled_switch = ft.Switch(
            value=self._llm_enabled,
            active_color=c.ACCENT,
            on_change=lambda e: self.app.page.run_task(self._on_llm_toggle, e),
        )
        self.llm_api_url_field = ft.TextField(
            label="API Base URL",
            value=self._llm_api_base_url,
            hint_text="http://localhost:1234/v1",
            border_radius=BorderRadius.SM,
            text_size=Typography.BODY_SIZE,
            text_style=ft.TextStyle(size=Typography.BODY_SIZE, color=c.TEXT_PRIMARY),
            label_style=ft.TextStyle(color=c.TEXT_SECONDARY),
            on_blur=lambda e: self.app.page.run_task(self._on_llm_url_change, e),
        )
        self.llm_api_key_field = ft.TextField(
            label="API Key (optional for local)",
            value="",
            password=True,
            can_reveal_password=True,
            hint_text="Leave empty for LM Studio",
            border_radius=BorderRadius.SM,
            text_size=Typography.BODY_SIZE,
            text_style=ft.TextStyle(size=Typography.BODY_SIZE, color=c.TEXT_PRIMARY),
            label_style=ft.TextStyle(color=c.TEXT_SECONDARY),
            on_blur=lambda e: self.app.page.run_task(self._on_api_key_change, e),
        )
        self.llm_model_field = ft.TextField(
            label="Model Name",
            value=self._llm_model,
            hint_text="Leave empty for server default",
            border_radius=BorderRadius.SM,
            text_size=Typography.BODY_SIZE,
            text_style=ft.TextStyle(size=Typography.BODY_SIZE, color=c.TEXT_PRIMARY),
            label_style=ft.TextStyle(color=c.TEXT_SECONDARY),
            on_blur=lambda e: self.app.page.run_task(self._on_llm_model_change, e),
        )
        self.llm_max_tokens_field = ft.TextField(
            label="Max Tokens",
            value=str(self._llm_max_tokens),
            hint_text="500",
            width=120,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=BorderRadius.SM,
            text_size=Typography.BODY_SIZE,
            text_style=ft.TextStyle(size=Typography.BODY_SIZE, color=c.TEXT_PRIMARY),
            label_style=ft.TextStyle(color=c.TEXT_SECONDARY),
            on_blur=lambda e: self.app.page.run_task(self._on_max_tokens_change, e),
        )
        self.llm_temperature_slider = ft.Slider(
            value=self._llm_temperature,
            min=0,
            max=1,
            divisions=10,
            label="{value}",
            active_color=c.ACCENT,
            on_change_end=lambda e: self.app.page.run_task(self._on_temperature_change, e),
        )
        self.llm_temperature_label = ft.Text(
            f"{self._llm_temperature:.1f}",
            size=Typography.BODY_SIZE,
            color=c.TEXT_PRIMARY,
            width=30,
        )
        self.llm_connection_status = ft.Text(
            "",
            size=Typography.CAPTION_SIZE,
            color=c.TEXT_TERTIARY,
        )
        self.llm_test_button = ft.OutlinedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.WIFI_TETHERING, size=16, color=c.TEXT_SECONDARY),
                    ft.Container(width=Spacing.XS),
                    ft.Text("Test Connection", color=c.TEXT_PRIMARY),
                ],
                tight=True,
            ),
            style=ft.ButtonStyle(
                side=ft.BorderSide(1, c.BORDER_DEFAULT),
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
            ),
            on_click=lambda e: self.app.page.run_task(self._test_llm_connection, e),
        )

        self.sidebar = Sidebar(
            current_route="/settings",
            newsletters=[],
            on_navigate=self._handle_navigate,
            page=self.app.page,
        )

        self.controls = [self._build_content()]

        # Load data
        self.app.page.run_task(self._load_data)

    def _build_content(self) -> ft.Control:
        """Build page content with sidebar."""
        c = self.colors  # Shorthand for readability
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
                                content=ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.Icons.ARROW_BACK,
                                            icon_color=c.TEXT_SECONDARY,
                                            icon_size=20,
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(
                                                    radius=BorderRadius.SM
                                                ),
                                            ),
                                            on_click=lambda _: self.app.navigate(
                                                "/home"
                                            ),
                                        ),
                                        ft.Container(width=Spacing.XS),
                                        ft.Text(
                                            "Settings",
                                            size=Typography.H1_SIZE,
                                            weight=ft.FontWeight.W_600,
                                            color=c.TEXT_PRIMARY,
                                        ),
                                    ],
                                ),
                                padding=ft.padding.only(bottom=Spacing.XL),
                            ),
                            # Settings content
                            ft.Container(
                                content=ft.Column(
                                    [
                                        # Account section
                                        self._build_section(
                                            "Account",
                                            ft.Column(
                                                [
                                                    ft.Row(
                                                        [
                                                            ft.CircleAvatar(
                                                                content=ft.Icon(
                                                                    ft.Icons.PERSON,
                                                                    size=20,
                                                                    color=c.TEXT_PRIMARY,
                                                                ),
                                                                radius=24,
                                                                bgcolor=c.BG_TERTIARY,
                                                            ),
                                                            ft.Container(width=Spacing.MD),
                                                            ft.Column(
                                                                [
                                                                    ft.Text(
                                                                        "Google Account",
                                                                        size=Typography.BODY_SIZE,
                                                                        weight=ft.FontWeight.W_500,
                                                                        color=c.TEXT_PRIMARY,
                                                                    ),
                                                                    self.user_email_text,
                                                                ],
                                                                spacing=Spacing.XXS,
                                                            ),
                                                        ],
                                                    ),
                                                    ft.Container(height=Spacing.MD),
                                                    ft.OutlinedButton(
                                                        content=ft.Row(
                                                            [
                                                                ft.Icon(
                                                                    ft.Icons.LOGOUT,
                                                                    size=16,
                                                                    color=c.ERROR,
                                                                ),
                                                                ft.Container(
                                                                    width=Spacing.XS
                                                                ),
                                                                ft.Text(
                                                                    "Sign Out",
                                                                    color=c.ERROR,
                                                                ),
                                                            ],
                                                        ),
                                                        style=ft.ButtonStyle(
                                                            side=ft.BorderSide(
                                                                1, c.ERROR
                                                            ),
                                                            shape=ft.RoundedRectangleBorder(
                                                                radius=BorderRadius.SM
                                                            ),
                                                        ),
                                                        on_click=lambda e: self.app.page.run_task(
                                                            self._on_sign_out, e
                                                        ),
                                                    ),
                                                ],
                                            ),
                                        ),
                                        ft.Container(height=Spacing.LG),
                                        # Appearance section
                                        self._build_section(
                                            "Appearance",
                                            self.theme_dropdown,
                                        ),
                                        ft.Container(height=Spacing.LG),
                                        # AI Summarization section
                                        self._build_section(
                                            "AI Summarization",
                                            self._build_llm_settings(),
                                        ),
                                        ft.Container(height=Spacing.LG),
                                        # About section
                                        self._build_section(
                                            "About",
                                            ft.Column(
                                                [
                                                    ft.Row(
                                                        [
                                                            ft.Icon(
                                                                ft.Icons.MARK_EMAIL_READ,
                                                                size=20,
                                                                color=c.ACCENT,
                                                            ),
                                                            ft.Container(width=Spacing.XS),
                                                            ft.Text(
                                                                "Newsletter Reader",
                                                                size=Typography.BODY_SIZE,
                                                                weight=ft.FontWeight.W_500,
                                                                color=c.TEXT_PRIMARY,
                                                            ),
                                                        ],
                                                    ),
                                                    ft.Container(height=Spacing.XS),
                                                    ft.Text(
                                                        "Version 0.1.0",
                                                        size=Typography.CAPTION_SIZE,
                                                        color=c.TEXT_TERTIARY,
                                                        font_family="monospace",
                                                    ),
                                                    ft.Container(height=Spacing.SM),
                                                    ft.Text(
                                                        "A newsletter reader with Gmail.",
                                                        size=Typography.BODY_SMALL_SIZE,
                                                        color=c.TEXT_SECONDARY,
                                                    ),
                                                ],
                                                spacing=0,
                                            ),
                                        ),
                                    ],
                                    scroll=ft.ScrollMode.AUTO,
                                ),
                                expand=True,
                            ),
                        ],
                        expand=True,
                    ),
                    padding=Spacing.LG,
                    expand=True,
                    bgcolor=c.BG_SECONDARY,
                ),
            ],
            expand=True,
            spacing=0,
        )

    def _build_llm_settings(self) -> ft.Control:
        """Build LLM settings content."""
        c = self.colors
        return ft.Column(
            [
                # Enable toggle row
                ft.Row(
                    [
                        self.llm_enabled_switch,
                        ft.Container(width=Spacing.SM),
                        ft.Text(
                            "Enable AI Summaries",
                            size=Typography.BODY_SIZE,
                            color=c.TEXT_PRIMARY,
                        ),
                    ],
                ),
                ft.Container(height=Spacing.SM),
                ft.Text(
                    "Generate concise summaries of newsletter emails using AI. "
                    "Works with LM Studio, Ollama, or any OpenAI-compatible API.",
                    size=Typography.CAPTION_SIZE,
                    color=c.TEXT_TERTIARY,
                ),
                ft.Container(height=Spacing.MD),
                # API Base URL
                self.llm_api_url_field,
                ft.Container(height=Spacing.SM),
                # API Key
                self.llm_api_key_field,
                ft.Container(height=Spacing.SM),
                # Model name
                self.llm_model_field,
                ft.Container(height=Spacing.MD),
                # Advanced settings row
                ft.Row(
                    [
                        # Max Tokens
                        self.llm_max_tokens_field,
                        ft.Container(width=Spacing.LG),
                        # Temperature
                        ft.Column(
                            [
                                ft.Text(
                                    "Temperature",
                                    size=Typography.CAPTION_SIZE,
                                    color=c.TEXT_SECONDARY,
                                ),
                                ft.Row(
                                    [
                                        ft.Container(
                                            content=self.llm_temperature_slider,
                                            width=150,
                                        ),
                                        self.llm_temperature_label,
                                    ],
                                    spacing=Spacing.SM,
                                ),
                            ],
                            spacing=Spacing.XXS,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.END,
                ),
                ft.Container(height=Spacing.MD),
                # Test connection row
                ft.Row(
                    [
                        self.llm_test_button,
                        ft.Container(width=Spacing.MD),
                        self.llm_connection_status,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=0,
        )

    def _build_section(self, title: str, content: ft.Control) -> ft.Control:
        """Build a settings section with title and card."""
        c = self.colors
        return ft.Column(
            [
                ft.Text(
                    title.upper(),
                    size=11,
                    weight=ft.FontWeight.W_500,
                    color=c.TEXT_TERTIARY,
                ),
                ft.Container(height=Spacing.SM),
                ft.Container(
                    content=content,
                    padding=Spacing.MD,
                    border_radius=BorderRadius.MD,
                    border=ft.border.all(1, c.BORDER_DEFAULT),
                    bgcolor=c.BG_PRIMARY,
                ),
            ],
            spacing=0,
        )

    def _handle_navigate(self, route: str) -> None:
        """Handle navigation from sidebar."""
        self.app.navigate(route)

    async def _load_data(self) -> None:
        """Load user information, newsletters, and LLM settings."""
        try:
            async with self.app.get_session() as session:
                # Load user info
                auth_service = AuthService(session)
                email = await auth_service.get_current_user_email()
                self.user_email_text.value = email or "Not signed in"

                # Load newsletters for sidebar
                newsletter_service = NewsletterService(session=session)
                self.newsletters = await newsletter_service.get_all_newsletters()

                # Load LLM settings
                settings_repo = UserSettingsRepository(session)
                user_settings = await settings_repo.get_settings()

                # Update LLM UI with loaded settings
                self._llm_enabled = user_settings.llm_enabled
                self._llm_api_base_url = user_settings.llm_api_base_url or "http://localhost:1234/v1"
                self._llm_model = user_settings.llm_model or ""
                self._llm_max_tokens = user_settings.llm_max_tokens
                self._llm_temperature = user_settings.llm_temperature
                self._llm_has_api_key = bool(user_settings.llm_api_key_encrypted)

                # Update UI controls
                self.llm_enabled_switch.value = self._llm_enabled
                self.llm_api_url_field.value = self._llm_api_base_url
                self.llm_model_field.value = self._llm_model
                self.llm_max_tokens_field.value = str(self._llm_max_tokens)
                self.llm_temperature_slider.value = self._llm_temperature
                self.llm_temperature_label.value = f"{self._llm_temperature:.1f}"

                # Show placeholder if API key is set
                if self._llm_has_api_key:
                    self.llm_api_key_field.hint_text = "API key is set (enter new to change)"

            # Update sidebar
            self.sidebar.update_newsletters(self.newsletters)
            self.app.page.update()
        except Exception:
            self.user_email_text.value = "Error loading user info"
            self.app.page.update()

    def _on_theme_change(self, e: ft.ControlEvent) -> None:
        """Handle theme change."""
        # Use e.data which contains the selected option key in on_select events
        theme_value = e.data or self.theme_dropdown.value
        if theme_value == "light":
            self.app.page.theme_mode = ft.ThemeMode.LIGHT
        elif theme_value == "dark":
            self.app.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.app.page.theme_mode = ft.ThemeMode.SYSTEM
        self.app.page.update()

        # Force page recreation by navigating away then back
        # This is needed because same-route navigation doesn't trigger route change
        self.app.page.views.clear()
        from src.ui.pages.settings_page import SettingsPage
        self.app.page.views.append(SettingsPage(self.app))
        self.app.page.update()

    async def _on_llm_toggle(self, e: ft.ControlEvent) -> None:
        """Handle LLM enabled toggle."""
        try:
            async with self.app.get_session() as session:
                settings_repo = UserSettingsRepository(session)
                await settings_repo.update_llm_enabled(e.control.value)
                await session.commit()
                self._llm_enabled = e.control.value
        except Exception as ex:
            self.app.show_snackbar(f"Error saving setting: {ex}", error=True)
            # Revert switch
            e.control.value = self._llm_enabled
            self.app.page.update()

    async def _on_llm_url_change(self, e: ft.ControlEvent) -> None:
        """Handle API URL change."""
        url = e.control.value.strip()
        if not url:
            url = "http://localhost:1234/v1"
            e.control.value = url
            self.app.page.update()

        try:
            async with self.app.get_session() as session:
                settings_repo = UserSettingsRepository(session)
                await settings_repo.update_llm_api_base_url(url)
                await session.commit()
                self._llm_api_base_url = url
        except Exception as ex:
            self.app.show_snackbar(f"Error saving setting: {ex}", error=True)

    async def _on_api_key_change(self, e: ft.ControlEvent) -> None:
        """Handle API key change."""
        api_key = e.control.value
        if not api_key:
            return  # Don't clear existing key on empty input

        try:
            async with self.app.get_session() as session:
                settings_repo = UserSettingsRepository(session)
                await settings_repo.update_llm_api_key(api_key)
                await session.commit()
                self._llm_has_api_key = True
                e.control.value = ""  # Clear the field for security
                e.control.hint_text = "API key is set (enter new to change)"
                self.app.page.update()
                self.app.show_snackbar("API key saved")
        except Exception as ex:
            self.app.show_snackbar(f"Error saving API key: {ex}", error=True)

    async def _on_llm_model_change(self, e: ft.ControlEvent) -> None:
        """Handle model name change."""
        model = e.control.value.strip()
        try:
            async with self.app.get_session() as session:
                settings_repo = UserSettingsRepository(session)
                await settings_repo.update_llm_model(model if model else None)
                await session.commit()
                self._llm_model = model
        except Exception as ex:
            self.app.show_snackbar(f"Error saving setting: {ex}", error=True)

    async def _on_max_tokens_change(self, e: ft.ControlEvent) -> None:
        """Handle max tokens change."""
        try:
            max_tokens = int(e.control.value)
            if max_tokens < 50:
                max_tokens = 50
            elif max_tokens > 4000:
                max_tokens = 4000
            e.control.value = str(max_tokens)
            self.app.page.update()

            async with self.app.get_session() as session:
                settings_repo = UserSettingsRepository(session)
                await settings_repo.update_llm_max_tokens(max_tokens)
                await session.commit()
                self._llm_max_tokens = max_tokens
        except ValueError:
            e.control.value = str(self._llm_max_tokens)
            self.app.page.update()
        except Exception as ex:
            self.app.show_snackbar(f"Error saving setting: {ex}", error=True)

    async def _on_temperature_change(self, e: ft.ControlEvent) -> None:
        """Handle temperature slider change."""
        temperature = round(e.control.value, 1)
        self.llm_temperature_label.value = f"{temperature:.1f}"
        self.app.page.update()

        try:
            async with self.app.get_session() as session:
                settings_repo = UserSettingsRepository(session)
                await settings_repo.update_llm_temperature(temperature)
                await session.commit()
                self._llm_temperature = temperature
        except Exception as ex:
            self.app.show_snackbar(f"Error saving setting: {ex}", error=True)

    async def _test_llm_connection(self, e: ft.ControlEvent) -> None:
        """Test connection to LLM API."""
        c = self.colors
        self.llm_connection_status.value = "Testing..."
        self.llm_connection_status.color = c.TEXT_TERTIARY
        self.app.page.update()

        try:
            # Get current settings from database
            async with self.app.get_session() as session:
                settings_repo = UserSettingsRepository(session)
                user_settings = await settings_repo.get_settings()

            # Test connection
            llm_service = LLMService(user_settings=user_settings)
            success, message = await llm_service.check_connection()

            if success:
                self.llm_connection_status.value = message
                self.llm_connection_status.color = c.SUCCESS
            else:
                self.llm_connection_status.value = message
                self.llm_connection_status.color = c.ERROR

        except Exception as ex:
            self.llm_connection_status.value = f"Error: {ex}"
            self.llm_connection_status.color = c.ERROR

        self.app.page.update()

    async def _on_sign_out(self, e: ft.ControlEvent) -> None:
        """Handle sign out."""

        async def confirm_sign_out(e: ft.ControlEvent) -> None:
            try:
                async with self.app.get_session() as session:
                    auth_service = AuthService(session)
                    await auth_service.logout()

                self.app.gmail_service = None
                dialog.open = False
                self.app.page.update()
                self.app.show_snackbar("Signed out successfully")
                self.app.navigate("/login")
            except Exception as ex:
                self.app.show_snackbar(f"Error: {ex}", error=True)

        def close_dialog(_: ft.ControlEvent | None) -> None:
            dialog.open = False
            self.app.page.update()

        dialog = ConfirmDialog(
            title="Sign Out",
            message="Are you sure you want to sign out?",
            confirm_text="Sign Out",
            cancel_text="Cancel",
            is_destructive=True,
            on_confirm=lambda e: self.app.page.run_task(confirm_sign_out, e),
            on_cancel=close_dialog,
        )

        self.app.page.show_dialog(dialog)
