"""Navigation component."""

import flet as ft


class Navigation(ft.NavigationRail):
    """Side navigation rail component."""

    def __init__(self, on_change=None):
        super().__init__(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.HOME_OUTLINED,
                    selected_icon=ft.icons.HOME,
                    label="Home",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.FOLDER_OUTLINED,
                    selected_icon=ft.icons.FOLDER,
                    label="Newsletters",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon=ft.icons.SETTINGS,
                    label="Settings",
                ),
            ],
            on_change=on_change,
        )
