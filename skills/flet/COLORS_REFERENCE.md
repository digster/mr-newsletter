# Flet Colors Reference

Flet provides Material Design colors via `ft.Colors.*` and color utilities.

## Usage

```python
# Named colors
ft.Container(bgcolor=ft.Colors.BLUE)
ft.Text("Hello", color=ft.Colors.RED_500)

# Hex colors
ft.Container(bgcolor="#FF5722")
ft.Container(bgcolor="#80FF5722")  # With alpha (50% opacity)

# RGBA colors
ft.Container(bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLUE))
```

## Primary Colors

Each color has shades from 50 (lightest) to 900 (darkest), plus accent shades.

### Red
```
ft.Colors.RED_50      # Lightest
ft.Colors.RED_100
ft.Colors.RED_200
ft.Colors.RED_300
ft.Colors.RED_400
ft.Colors.RED_500     # Base (same as ft.Colors.RED)
ft.Colors.RED_600
ft.Colors.RED_700
ft.Colors.RED_800
ft.Colors.RED_900     # Darkest
ft.Colors.RED_ACCENT_100
ft.Colors.RED_ACCENT_200
ft.Colors.RED_ACCENT_400
ft.Colors.RED_ACCENT_700
```

### Pink
```
ft.Colors.PINK
ft.Colors.PINK_50 through PINK_900
ft.Colors.PINK_ACCENT_100 through PINK_ACCENT_700
```

### Purple
```
ft.Colors.PURPLE
ft.Colors.PURPLE_50 through PURPLE_900
ft.Colors.PURPLE_ACCENT_100 through PURPLE_ACCENT_700
```

### Deep Purple
```
ft.Colors.DEEP_PURPLE
ft.Colors.DEEP_PURPLE_50 through DEEP_PURPLE_900
ft.Colors.DEEP_PURPLE_ACCENT_100 through DEEP_PURPLE_ACCENT_700
```

### Indigo
```
ft.Colors.INDIGO
ft.Colors.INDIGO_50 through INDIGO_900
ft.Colors.INDIGO_ACCENT_100 through INDIGO_ACCENT_700
```

### Blue
```
ft.Colors.BLUE
ft.Colors.BLUE_50 through BLUE_900
ft.Colors.BLUE_ACCENT_100 through BLUE_ACCENT_700
```

### Light Blue
```
ft.Colors.LIGHT_BLUE
ft.Colors.LIGHT_BLUE_50 through LIGHT_BLUE_900
ft.Colors.LIGHT_BLUE_ACCENT_100 through LIGHT_BLUE_ACCENT_700
```

### Cyan
```
ft.Colors.CYAN
ft.Colors.CYAN_50 through CYAN_900
ft.Colors.CYAN_ACCENT_100 through CYAN_ACCENT_700
```

### Teal
```
ft.Colors.TEAL
ft.Colors.TEAL_50 through TEAL_900
ft.Colors.TEAL_ACCENT_100 through TEAL_ACCENT_700
```

### Green
```
ft.Colors.GREEN
ft.Colors.GREEN_50 through GREEN_900
ft.Colors.GREEN_ACCENT_100 through GREEN_ACCENT_700
```

### Light Green
```
ft.Colors.LIGHT_GREEN
ft.Colors.LIGHT_GREEN_50 through LIGHT_GREEN_900
ft.Colors.LIGHT_GREEN_ACCENT_100 through LIGHT_GREEN_ACCENT_700
```

### Lime
```
ft.Colors.LIME
ft.Colors.LIME_50 through LIME_900
ft.Colors.LIME_ACCENT_100 through LIME_ACCENT_700
```

### Yellow
```
ft.Colors.YELLOW
ft.Colors.YELLOW_50 through YELLOW_900
ft.Colors.YELLOW_ACCENT_100 through YELLOW_ACCENT_700
```

### Amber
```
ft.Colors.AMBER
ft.Colors.AMBER_50 through AMBER_900
ft.Colors.AMBER_ACCENT_100 through AMBER_ACCENT_700
```

### Orange
```
ft.Colors.ORANGE
ft.Colors.ORANGE_50 through ORANGE_900
ft.Colors.ORANGE_ACCENT_100 through ORANGE_ACCENT_700
```

### Deep Orange
```
ft.Colors.DEEP_ORANGE
ft.Colors.DEEP_ORANGE_50 through DEEP_ORANGE_900
ft.Colors.DEEP_ORANGE_ACCENT_100 through DEEP_ORANGE_ACCENT_700
```

### Brown
```
ft.Colors.BROWN
ft.Colors.BROWN_50 through BROWN_900
# No accent shades for brown
```

### Grey
```
ft.Colors.GREY
ft.Colors.GREY_50 through GREY_900
# No accent shades for grey
```

### Blue Grey
```
ft.Colors.BLUE_GREY
ft.Colors.BLUE_GREY_50 through BLUE_GREY_900
# No accent shades for blue grey
```

## Basic Colors

```
ft.Colors.BLACK
ft.Colors.BLACK12    # 12% opacity
ft.Colors.BLACK26    # 26% opacity
ft.Colors.BLACK38    # 38% opacity
ft.Colors.BLACK45    # 45% opacity
ft.Colors.BLACK54    # 54% opacity
ft.Colors.BLACK87    # 87% opacity

ft.Colors.WHITE
ft.Colors.WHITE10    # 10% opacity
ft.Colors.WHITE12    # 12% opacity
ft.Colors.WHITE24    # 24% opacity
ft.Colors.WHITE30    # 30% opacity
ft.Colors.WHITE38    # 38% opacity
ft.Colors.WHITE54    # 54% opacity
ft.Colors.WHITE60    # 60% opacity
ft.Colors.WHITE70    # 70% opacity

ft.Colors.TRANSPARENT
```

## Semantic Colors

These adapt to light/dark theme automatically:

```
ft.Colors.PRIMARY
ft.Colors.ON_PRIMARY
ft.Colors.PRIMARY_CONTAINER
ft.Colors.ON_PRIMARY_CONTAINER

ft.Colors.SECONDARY
ft.Colors.ON_SECONDARY
ft.Colors.SECONDARY_CONTAINER
ft.Colors.ON_SECONDARY_CONTAINER

ft.Colors.TERTIARY
ft.Colors.ON_TERTIARY
ft.Colors.TERTIARY_CONTAINER
ft.Colors.ON_TERTIARY_CONTAINER

ft.Colors.ERROR
ft.Colors.ON_ERROR
ft.Colors.ERROR_CONTAINER
ft.Colors.ON_ERROR_CONTAINER

ft.Colors.BACKGROUND
ft.Colors.ON_BACKGROUND

ft.Colors.SURFACE
ft.Colors.ON_SURFACE
ft.Colors.SURFACE_VARIANT
ft.Colors.ON_SURFACE_VARIANT

ft.Colors.OUTLINE
ft.Colors.OUTLINE_VARIANT

ft.Colors.SHADOW
ft.Colors.SCRIM

ft.Colors.INVERSE_SURFACE
ft.Colors.ON_INVERSE_SURFACE
ft.Colors.INVERSE_PRIMARY
```

## Color Utilities

### With Opacity
```python
# Apply opacity to any color
color = ft.Colors.with_opacity(0.5, ft.Colors.BLUE)  # 50% opacity
color = ft.Colors.with_opacity(0.8, "#FF5722")       # Works with hex too
```

### Hex Colors
```python
# 6-digit hex (RGB)
bgcolor="#FF5722"

# 8-digit hex (ARGB - Alpha first)
bgcolor="#80FF5722"  # 50% opacity orange

# 3-digit shorthand
bgcolor="#F00"  # Same as #FF0000
```

### Theme-Based Colors
```python
# Set theme color seed for automatic color scheme
page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)

# Then use semantic colors that auto-adapt
ft.Container(bgcolor=ft.Colors.PRIMARY)
ft.Text("Hello", color=ft.Colors.ON_PRIMARY)
```

## Gradients

### Linear Gradient
```python
ft.Container(
    gradient=ft.LinearGradient(
        begin=ft.Alignment.TOP_LEFT,
        end=ft.Alignment.BOTTOM_RIGHT,
        colors=[ft.Colors.BLUE, ft.Colors.RED],
        stops=[0.0, 1.0],  # Optional color stops
        tile_mode=ft.GradientTileMode.CLAMP,
    )
)
```

### Radial Gradient
```python
ft.Container(
    gradient=ft.RadialGradient(
        center=ft.Alignment.CENTER,
        radius=0.5,
        colors=[ft.Colors.YELLOW, ft.Colors.ORANGE],
        stops=[0.0, 1.0],
        tile_mode=ft.GradientTileMode.CLAMP,
    )
)
```

### Sweep Gradient
```python
ft.Container(
    gradient=ft.SweepGradient(
        center=ft.Alignment.CENTER,
        start_angle=0.0,
        end_angle=6.28,  # 2*pi for full circle
        colors=[ft.Colors.RED, ft.Colors.BLUE, ft.Colors.GREEN, ft.Colors.RED],
    )
)
```

## Common Color Combinations

### Light Theme
```python
page.bgcolor = ft.Colors.WHITE
page.theme_mode = ft.ThemeMode.LIGHT

# Primary action buttons
ft.Button(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)

# Secondary/muted
ft.Container(bgcolor=ft.Colors.GREY_100)

# Cards
ft.Card(color=ft.Colors.WHITE)

# Text hierarchy
ft.Text("Title", color=ft.Colors.BLACK87)
ft.Text("Body", color=ft.Colors.BLACK54)
ft.Text("Caption", color=ft.Colors.BLACK38)
```

### Dark Theme
```python
page.bgcolor = ft.Colors.GREY_900
page.theme_mode = ft.ThemeMode.DARK

# Primary action buttons
ft.Button(bgcolor=ft.Colors.BLUE_ACCENT_200, color=ft.Colors.BLACK)

# Secondary/muted
ft.Container(bgcolor=ft.Colors.GREY_800)

# Cards
ft.Card(color=ft.Colors.GREY_850)

# Text hierarchy
ft.Text("Title", color=ft.Colors.WHITE)
ft.Text("Body", color=ft.Colors.WHITE70)
ft.Text("Caption", color=ft.Colors.WHITE54)
```

### Status Colors
```python
# Success
ft.Colors.GREEN_500
ft.Colors.GREEN_ACCENT_400

# Warning
ft.Colors.AMBER_500
ft.Colors.ORANGE_500

# Error
ft.Colors.RED_500
ft.Colors.RED_ACCENT_400

# Info
ft.Colors.BLUE_500
ft.Colors.LIGHT_BLUE_500
```

## Full Reference

For complete color specifications, see:
- Material Design Color System: https://m3.material.io/styles/color/overview
- Flutter Colors class: https://api.flutter.dev/flutter/material/Colors-class.html
