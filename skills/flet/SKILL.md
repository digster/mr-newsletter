---
name: flet
description: "Build cross-platform apps (web, mobile, desktop) in pure Python using Flutter UI. Use when creating GUI applications with Flet framework for desktop apps (Windows, macOS, Linux), mobile apps (iOS, Android), web apps/PWAs, and real-time interactive UIs. Covers controls, layouts, events, theming, navigation, custom controls, and packaging with flet build."
---

# Flet - Cross-Platform Python UI Framework

Flet enables building web, mobile, and desktop applications in Python using Flutter for rendering. No frontend experience required.

## Installation

```bash
pip install flet[all] --break-system-packages
```

The `[all]` extra installs all platform dependencies. For minimal setup use just `pip install flet`.

## Quick Start

```python
import flet as ft

def main(page: ft.Page):
    page.title = "My App"
    page.add(ft.Text("Hello, Flet!"))

ft.run(main)  # Desktop window
# ft.run(main, view=ft.AppView.WEB_BROWSER)  # Browser
```

## Core Concepts

### Page Object

The `page` is the root container. Key properties:

```python
page.title = "App Title"
page.window.width = 800
page.window.height = 600
page.theme_mode = ft.ThemeMode.DARK  # LIGHT, DARK, SYSTEM
page.vertical_alignment = ft.MainAxisAlignment.CENTER
page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
page.padding = 20
page.bgcolor = ft.Colors.BLUE_GREY_900
page.scroll = ft.ScrollMode.AUTO  # Enable page scrolling
```

### Adding Controls

```python
# Add single control
page.add(ft.Text("Hello"))

# Add multiple controls
page.add(
    ft.Text("Line 1"),
    ft.Text("Line 2")
)

# Direct manipulation
page.controls.append(ft.Text("Added"))
page.update()  # Must call update() after manual changes
```

### Event Handling

```python
def button_clicked(e):
    print(f"Clicked! Control: {e.control}")
    e.control.text = "Clicked!"
    e.control.update()

page.add(ft.Button("Click me", on_click=button_clicked))
```

## Layout Controls

### Row and Column

```python
ft.Row(
    controls=[ft.Text("A"), ft.Text("B"), ft.Text("C")],
    alignment=ft.MainAxisAlignment.CENTER,
    vertical_alignment=ft.CrossAxisAlignment.CENTER,
    spacing=10,
    wrap=True,  # Wrap to next line
)

ft.Column(
    controls=[ft.Text("1"), ft.Text("2")],
    alignment=ft.MainAxisAlignment.START,
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    spacing=10,
    scroll=ft.ScrollMode.AUTO,
)
```

### Container

```python
ft.Container(
    content=ft.Text("Styled"),
    width=200,
    height=100,
    bgcolor=ft.Colors.AMBER,
    border_radius=10,
    border=ft.border.all(2, ft.Colors.BLACK),
    padding=20,
    margin=10,
    alignment=ft.Alignment.CENTER,
    on_click=lambda e: print("Container clicked"),
)
```

### Stack (for overlapping)

```python
ft.Stack(
    controls=[
        ft.Container(bgcolor=ft.Colors.RED, width=100, height=100),
        ft.Container(bgcolor=ft.Colors.BLUE, width=50, height=50, left=25, top=25),
    ]
)
```

### Expand and Flexible

```python
ft.Row([
    ft.TextField(expand=1),  # Takes available space
    ft.Button("Send"),
])
```

## Common Controls

### Input Controls

```python
# Text field
tf = ft.TextField(
    label="Name",
    hint_text="Enter your name",
    on_change=lambda e: print(e.control.value),
    on_submit=lambda e: print("Submitted"),
    password=True,  # For password fields
    multiline=True,
    max_lines=5,
)

# Dropdown
dd = ft.Dropdown(
    label="Color",
    options=[
        ft.dropdown.Option("red"),
        ft.dropdown.Option("green"),
        ft.dropdown.Option("blue"),
    ],
    on_change=lambda e: print(e.control.value),
)

# Checkbox
cb = ft.Checkbox(label="Accept terms", on_change=lambda e: print(e.control.value))

# Switch
sw = ft.Switch(label="Dark mode", on_change=lambda e: print(e.control.value))

# Slider
sl = ft.Slider(min=0, max=100, divisions=10, label="{value}", on_change=lambda e: print(e.control.value))

# Radio buttons
rg = ft.RadioGroup(
    content=ft.Column([
        ft.Radio(value="opt1", label="Option 1"),
        ft.Radio(value="opt2", label="Option 2"),
    ]),
    on_change=lambda e: print(e.control.value),
)
```

### Buttons

```python
ft.Button("Elevated", on_click=handler)
ft.FilledButton("Filled", on_click=handler)
ft.OutlinedButton("Outlined", on_click=handler)
ft.TextButton("Text", on_click=handler)
ft.IconButton(icon=ft.Icons.ADD, on_click=handler)
ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=handler)
```

### Display Controls

```python
ft.Text("Hello", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE)
ft.Icon(ft.Icons.FAVORITE, color=ft.Colors.RED, size=40)
ft.Image(src="image.png", width=200, height=200, fit=ft.ImageFit.CONTAIN)
ft.ProgressBar(value=0.5)
ft.ProgressRing()
```

### Data Display

```python
# DataTable
ft.DataTable(
    columns=[
        ft.DataColumn(ft.Text("Name")),
        ft.DataColumn(ft.Text("Age"), numeric=True),
    ],
    rows=[
        ft.DataRow(cells=[ft.DataCell(ft.Text("Alice")), ft.DataCell(ft.Text("30"))]),
        ft.DataRow(cells=[ft.DataCell(ft.Text("Bob")), ft.DataCell(ft.Text("25"))]),
    ],
)

# ListView (for large lists - uses virtualization)
ft.ListView(
    controls=[ft.Text(f"Item {i}") for i in range(100)],
    spacing=10,
    padding=20,
    auto_scroll=True,
)
```

## Navigation

### AppBar

```python
page.appbar = ft.AppBar(
    title=ft.Text("My App"),
    bgcolor=ft.Colors.SURFACE_VARIANT,
    leading=ft.IconButton(icon=ft.Icons.MENU),
    actions=[
        ft.IconButton(icon=ft.Icons.SETTINGS),
    ],
)
```

### NavigationBar (Bottom)

```python
page.navigation_bar = ft.NavigationBar(
    destinations=[
        ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
        ft.NavigationBarDestination(icon=ft.Icons.SEARCH, label="Search"),
        ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Profile"),
    ],
    on_change=lambda e: print(f"Selected: {e.control.selected_index}"),
)
```

### NavigationRail (Side)

```python
rail = ft.NavigationRail(
    destinations=[
        ft.NavigationRailDestination(icon=ft.Icons.HOME, label="Home"),
        ft.NavigationRailDestination(icon=ft.Icons.SETTINGS, label="Settings"),
    ],
    on_change=lambda e: print(e.control.selected_index),
)
page.add(ft.Row([rail, ft.VerticalDivider(), content_area], expand=True))
```

### Tabs

```python
ft.Tabs(
    tabs=[
        ft.Tab(text="Tab 1", content=ft.Text("Content 1")),
        ft.Tab(text="Tab 2", icon=ft.Icons.SEARCH, content=ft.Text("Content 2")),
    ],
    on_change=lambda e: print(e.control.selected_index),
)
```

### Views and Routing

```python
def main(page: ft.Page):
    def route_change(e):
        page.views.clear()
        page.views.append(
            ft.View("/", [ft.AppBar(title=ft.Text("Home")), ft.Button("Go to Store", on_click=lambda _: page.go("/store"))])
        )
        if page.route == "/store":
            page.views.append(
                ft.View("/store", [ft.AppBar(title=ft.Text("Store")), ft.Text("Store page")])
            )
        page.update()

    def view_pop(e):
        page.views.pop()
        page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")

ft.run(main)
```

## Dialogs and Overlays

### AlertDialog

```python
def open_dialog(e):
    dialog = ft.AlertDialog(
        title=ft.Text("Confirm"),
        content=ft.Text("Are you sure?"),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.close(dialog)),
            ft.TextButton("OK", on_click=lambda e: page.close(dialog)),
        ],
    )
    page.open(dialog)
```

### SnackBar

```python
page.open(ft.SnackBar(content=ft.Text("Operation completed!")))
```

### BottomSheet

```python
bs = ft.BottomSheet(
    content=ft.Container(
        content=ft.Column([ft.Text("Bottom Sheet"), ft.Button("Close", on_click=lambda e: page.close(bs))]),
        padding=20,
    ),
)
page.open(bs)
```

## File Operations

### FilePicker

```python
def pick_result(e: ft.FilePickerResultEvent):
    if e.files:
        for f in e.files:
            print(f.name, f.path)

file_picker = ft.FilePicker(on_result=pick_result)
page.overlay.append(file_picker)
page.update()

# To open picker
file_picker.pick_files(allow_multiple=True, allowed_extensions=["pdf", "txt"])
# Or save file
file_picker.save_file(file_name="document.txt")
# Or pick directory
file_picker.get_directory_path()
```

## Theming

```python
page.theme = ft.Theme(
    color_scheme_seed=ft.Colors.BLUE,
    font_family="Roboto",
)
page.dark_theme = ft.Theme(
    color_scheme_seed=ft.Colors.INDIGO,
)
page.theme_mode = ft.ThemeMode.SYSTEM
```

## Custom Controls

### Styled Control

```python
class MyButton(ft.Button):
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.bgcolor = ft.Colors.ORANGE_300
        self.color = ft.Colors.GREEN_800
```

### Composite Control

```python
class Task(ft.Row):
    def __init__(self, text, delete_callback):
        super().__init__()
        self.checkbox = ft.Checkbox(on_change=self.status_changed)
        self.text_view = ft.Text(text)
        self.delete_btn = ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda e: delete_callback(self))
        self.controls = [self.checkbox, self.text_view, self.delete_btn]
    
    def status_changed(self, e):
        self.text_view.style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if self.checkbox.value else None
        self.update()
```

### Lifecycle Methods

```python
class WeatherWidget(ft.Column):
    def __init__(self):
        super().__init__()
        self.temp = ft.Text("Loading...")
        self.controls = [self.temp]
    
    def did_mount(self):
        # Called after control added to page
        self.fetch_weather()
    
    def will_unmount(self):
        # Called before control removed
        pass
    
    def before_update(self):
        # Called before each update
        pass
```

## Async Support

```python
import asyncio

async def main(page: ft.Page):
    async def fetch_data(e):
        page.add(ft.ProgressRing())
        page.update()
        await asyncio.sleep(2)  # Simulate API call
        page.controls.pop()
        page.add(ft.Text("Data loaded!"))
        page.update()
    
    page.add(ft.Button("Load", on_click=fetch_data))

ft.run(main)
```

## Packaging and Distribution

### Project Structure

```
my_app/
├── main.py           # Entry point with ft.run(main)
├── assets/           # Images, fonts, etc.
│   └── icon.png
├── requirements.txt  # Dependencies
└── pyproject.toml    # Optional configuration
```

### pyproject.toml Configuration

```toml
[tool.flet]
app.module = "main"
app.product = "My App"
app.org = "com.example"

[tool.flet.app]
# Common settings
product = "My App"
description = "My awesome app"
version = "1.0.0"

[tool.flet.android]
min_sdk_version = 21

[tool.flet.ios]
# iOS specific settings
```

### Build Commands

```bash
# Desktop
flet build macos    # macOS app bundle
flet build windows  # Windows executable
flet build linux    # Linux executable

# Mobile
flet build apk      # Android APK
flet build aab      # Android App Bundle (Play Store)
flet build ipa      # iOS app (requires macOS)

# Web
flet build web      # Static website (runs client-side via WebAssembly)
```

### Common Build Options

```bash
flet build apk \
    --project my_app \
    --org com.example \
    --product "My App" \
    --description "My awesome app" \
    --include-packages flet_video flet_audio \
    --compile-app \
    --compile-packages
```

### Running for Development

```bash
flet run                    # Run with hot reload
flet run --web              # Run in browser
flet run -d                 # Run with verbose output
flet run --android          # Run on connected Android device
flet run --ios              # Run on iOS simulator
```

## Best Practices

1. **Call `update()` efficiently**: Batch multiple changes before calling `page.update()` to minimize UI refreshes.

2. **Use `ListView` for large lists**: It virtualizes items for better performance.

3. **Organize with custom controls**: Break complex UIs into reusable custom control classes.

4. **Use `expand` for responsive layouts**: Let controls fill available space dynamically.

5. **Handle state properly**: Store state in control classes, not global variables.

6. **Use `ref` for control references**:
   ```python
   text_ref = ft.Ref[ft.Text]()
   page.add(ft.Text("Hello", ref=text_ref))
   text_ref.current.value = "Updated"
   ```

## Common Patterns

### Form with Validation

```python
def validate_and_submit(e):
    if not name_field.value:
        name_field.error_text = "Name is required"
        name_field.update()
        return
    # Process form
    page.open(ft.SnackBar(content=ft.Text("Submitted!")))

name_field = ft.TextField(label="Name")
page.add(name_field, ft.Button("Submit", on_click=validate_and_submit))
```

### Loading State

```python
def load_data(e):
    btn = e.control
    btn.disabled = True
    btn.text = "Loading..."
    btn.update()
    # Do work
    btn.disabled = False
    btn.text = "Load"
    btn.update()
```

### Responsive Layout

```python
def on_resize(e):
    if page.width < 600:
        # Mobile layout
        content.controls = [mobile_layout]
    else:
        # Desktop layout
        content.controls = [desktop_layout]
    content.update()

page.on_resized = on_resize
```

## Reference Files

- **[CONTROLS_REFERENCE.md](references/CONTROLS_REFERENCE.md)**: Complete list of all Flet controls with properties
- **[ICONS_REFERENCE.md](references/ICONS_REFERENCE.md)**: Available Material icons (ft.Icons.*)
- **[COLORS_REFERENCE.md](references/COLORS_REFERENCE.md)**: Available colors (ft.Colors.*)
