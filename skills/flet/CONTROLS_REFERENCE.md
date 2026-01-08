# Flet Controls Reference

Complete reference of Flet controls organized by category.

## Table of Contents
- [Layout Controls](#layout-controls)
- [Navigation Controls](#navigation-controls)
- [Input Controls](#input-controls)
- [Button Controls](#button-controls)
- [Display Controls](#display-controls)
- [Data Controls](#data-controls)
- [Dialog/Overlay Controls](#dialogoverlay-controls)
- [Utility Controls](#utility-controls)
- [Charts](#charts)
- [Media Controls](#media-controls)

---

## Layout Controls

### Container
Wrapper with styling capabilities.
```python
ft.Container(
    content=ft.Text("Content"),
    width=200, height=100,
    padding=ft.Padding(all=10),
    margin=ft.Margin(left=10),
    bgcolor=ft.Colors.AMBER,
    border=ft.border.all(2, ft.Colors.BLACK),
    border_radius=ft.border_radius.all(10),
    gradient=ft.LinearGradient(begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT, colors=[ft.Colors.BLUE, ft.Colors.RED]),
    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK54),
    alignment=ft.Alignment.CENTER,
    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    on_click=handler, on_hover=handler, on_long_press=handler,
)
```

### Row
Horizontal layout.
```python
ft.Row(
    controls=[...],
    alignment=ft.MainAxisAlignment.START,  # START, CENTER, END, SPACE_BETWEEN, SPACE_AROUND, SPACE_EVENLY
    vertical_alignment=ft.CrossAxisAlignment.CENTER,  # START, CENTER, END, STRETCH, BASELINE
    spacing=10,
    tight=False,
    wrap=False,
    run_spacing=10,  # Spacing between wrapped rows
    scroll=ft.ScrollMode.AUTO,
)
```

### Column
Vertical layout.
```python
ft.Column(
    controls=[...],
    alignment=ft.MainAxisAlignment.START,
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    spacing=10,
    tight=False,
    wrap=False,
    run_spacing=10,
    scroll=ft.ScrollMode.AUTO,
)
```

### Stack
Overlapping children.
```python
ft.Stack(
    controls=[...],
    clip_behavior=ft.ClipBehavior.NONE,
)
# Children can use left, top, right, bottom properties
```

### ListView
Scrollable list with virtualization for large lists.
```python
ft.ListView(
    controls=[...],
    horizontal=False,
    spacing=10,
    padding=20,
    auto_scroll=False,
    first_item_prototype=True,  # Performance optimization
    divider_thickness=1,
    on_scroll=handler,
    on_scroll_interval=100,
)
```

### GridView
Grid layout.
```python
ft.GridView(
    controls=[...],
    runs_count=3,  # Number of columns
    max_extent=150,  # Max size of each cell
    spacing=10,
    run_spacing=10,
    padding=10,
    child_aspect_ratio=1.0,
)
```

### ResponsiveRow
Bootstrap-style responsive grid.
```python
ft.ResponsiveRow(
    controls=[
        ft.Container(col={"sm": 6, "md": 4, "lg": 3}, content=...),
    ],
    spacing=10,
    run_spacing=10,
)
```

### Card
Material card container.
```python
ft.Card(
    content=ft.Container(content=..., padding=10),
    elevation=4,
    color=ft.Colors.WHITE,
    shadow_color=ft.Colors.BLACK,
    margin=10,
)
```

### Divider / VerticalDivider
```python
ft.Divider(height=20, thickness=2, color=ft.Colors.GREY)
ft.VerticalDivider(width=20, thickness=2, color=ft.Colors.GREY)
```

### ExpansionTile
Expandable list tile.
```python
ft.ExpansionTile(
    title=ft.Text("Title"),
    subtitle=ft.Text("Subtitle"),
    leading=ft.Icon(ft.Icons.FOLDER),
    trailing=ft.Icon(ft.Icons.ARROW_DROP_DOWN),
    controls=[ft.Text("Content")],
    initially_expanded=False,
    on_change=handler,
)
```

### ExpansionPanelList
Multiple expandable panels.
```python
ft.ExpansionPanelList(
    controls=[
        ft.ExpansionPanel(
            header=ft.ListTile(title=ft.Text("Panel 1")),
            content=ft.Container(content=...),
        ),
    ],
    on_change=handler,
)
```

---

## Navigation Controls

### AppBar
Top app bar.
```python
ft.AppBar(
    leading=ft.IconButton(icon=ft.Icons.MENU),
    leading_width=40,
    title=ft.Text("Title"),
    center_title=False,
    bgcolor=ft.Colors.SURFACE_VARIANT,
    actions=[ft.IconButton(icon=ft.Icons.SEARCH)],
    elevation=4,
    toolbar_height=56,
)
```

### NavigationBar
Bottom navigation.
```python
ft.NavigationBar(
    destinations=[
        ft.NavigationBarDestination(icon=ft.Icons.HOME, selected_icon=ft.Icons.HOME_FILLED, label="Home"),
    ],
    selected_index=0,
    on_change=handler,
    bgcolor=ft.Colors.SURFACE,
    elevation=8,
    label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
)
```

### NavigationRail
Side navigation.
```python
ft.NavigationRail(
    destinations=[
        ft.NavigationRailDestination(icon=ft.Icons.HOME, selected_icon=ft.Icons.HOME_FILLED, label="Home"),
    ],
    selected_index=0,
    on_change=handler,
    extended=False,
    min_width=72,
    min_extended_width=200,
    label_type=ft.NavigationRailLabelType.ALL,
    leading=ft.FloatingActionButton(icon=ft.Icons.ADD),
    trailing=ft.IconButton(icon=ft.Icons.SETTINGS),
)
```

### NavigationDrawer
Side drawer.
```python
ft.NavigationDrawer(
    controls=[
        ft.NavigationDrawerDestination(icon=ft.Icons.HOME, label="Home"),
    ],
    on_change=handler,
    selected_index=0,
)
# Open with: page.open(drawer)
```

### Tabs
Tabbed interface.
```python
ft.Tabs(
    tabs=[
        ft.Tab(text="Tab 1", icon=ft.Icons.HOME, content=ft.Text("Content 1")),
    ],
    selected_index=0,
    on_change=handler,
    scrollable=False,
    animation_duration=300,
    divider_color=ft.Colors.GREY,
)
```

### CupertinoNavigationBar
iOS-style navigation bar.
```python
ft.CupertinoNavigationBar(
    middle=ft.Text("Title"),
    leading=ft.CupertinoButton(text="Back"),
    trailing=ft.CupertinoButton(text="Done"),
)
```

---

## Input Controls

### TextField
Text input.
```python
ft.TextField(
    label="Label",
    hint_text="Hint",
    value="Initial value",
    prefix_icon=ft.Icons.SEARCH,
    suffix_icon=ft.Icons.CLEAR,
    prefix_text="$",
    suffix_text=".00",
    helper_text="Helper text",
    error_text="Error message",  # Set to show error state
    counter_text="0/100",
    password=False,
    can_reveal_password=True,
    multiline=False,
    min_lines=1,
    max_lines=1,
    max_length=100,
    keyboard_type=ft.KeyboardType.TEXT,
    text_align=ft.TextAlign.LEFT,
    autofocus=False,
    read_only=False,
    filled=True,
    border=ft.InputBorder.OUTLINE,  # OUTLINE, UNDERLINE, NONE
    border_radius=8,
    border_color=ft.Colors.BLUE,
    focused_border_color=ft.Colors.GREEN,
    on_change=handler,
    on_submit=handler,
    on_focus=handler,
    on_blur=handler,
)
```

### Dropdown
Select from options.
```python
ft.Dropdown(
    label="Select",
    hint_text="Choose one",
    value="opt1",
    options=[
        ft.dropdown.Option(key="opt1", text="Option 1"),
        ft.dropdown.Option(key="opt2", text="Option 2"),
    ],
    autofocus=False,
    on_change=handler,
    on_focus=handler,
    on_blur=handler,
)
```

### Checkbox
```python
ft.Checkbox(
    label="Accept terms",
    value=False,
    tristate=False,  # Allow indeterminate state
    autofocus=False,
    check_color=ft.Colors.WHITE,
    fill_color=ft.Colors.BLUE,
    on_change=handler,
)
```

### Switch
```python
ft.Switch(
    label="Enable",
    value=False,
    label_position=ft.LabelPosition.RIGHT,
    autofocus=False,
    active_color=ft.Colors.GREEN,
    active_track_color=ft.Colors.GREEN_200,
    inactive_thumb_color=ft.Colors.GREY,
    inactive_track_color=ft.Colors.GREY_300,
    on_change=handler,
)
```

### Radio / RadioGroup
```python
ft.RadioGroup(
    value="opt1",
    content=ft.Column([
        ft.Radio(value="opt1", label="Option 1"),
        ft.Radio(value="opt2", label="Option 2"),
    ]),
    on_change=handler,
)
```

### Slider
```python
ft.Slider(
    value=50,
    min=0,
    max=100,
    divisions=10,
    label="{value}",
    round=0,
    autofocus=False,
    active_color=ft.Colors.BLUE,
    inactive_color=ft.Colors.GREY,
    thumb_color=ft.Colors.BLUE,
    on_change=handler,
    on_change_start=handler,
    on_change_end=handler,
)
```

### RangeSlider
```python
ft.RangeSlider(
    start_value=20,
    end_value=80,
    min=0,
    max=100,
    divisions=10,
    labels=[ft.SliderLabel("{value}")],
    on_change=handler,
)
```

### DatePicker
```python
ft.DatePicker(
    first_date=datetime.datetime(2020, 1, 1),
    last_date=datetime.datetime(2030, 12, 31),
    current_date=datetime.datetime.now(),
    on_change=handler,
    on_dismiss=handler,
)
# Open with: page.open(date_picker)
```

### TimePicker
```python
ft.TimePicker(
    value=datetime.time(12, 0),
    on_change=handler,
    on_dismiss=handler,
)
# Open with: page.open(time_picker)
```

### SearchBar
```python
ft.SearchBar(
    value="",
    bar_hint_text="Search...",
    view_hint_text="Search items",
    controls=[
        ft.ListTile(title=ft.Text("Result 1"), on_click=handler),
    ],
    on_change=handler,
    on_submit=handler,
    on_tap=handler,
)
```

### AutoComplete
```python
ft.AutoComplete(
    suggestions=[
        ft.AutoCompleteSuggestion(key="1", value="Apple"),
        ft.AutoCompleteSuggestion(key="2", value="Banana"),
    ],
    on_select=handler,
)
```

---

## Button Controls

### Button
```python
ft.Button(
    text="Button",
    icon=ft.Icons.ADD,
    icon_color=ft.Colors.WHITE,
    color=ft.Colors.WHITE,
    bgcolor=ft.Colors.BLUE,
    elevation=4,
    style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=10),
        padding=ft.Padding(all=20),
    ),
    autofocus=False,
    on_click=handler,
    on_long_press=handler,
    on_hover=handler,
)
```

### FilledButton
```python
ft.FilledButton(text="Filled", on_click=handler)
```

### FilledTonalButton
```python
ft.FilledTonalButton(text="Tonal", on_click=handler)
```

### OutlinedButton
```python
ft.OutlinedButton(text="Outlined", on_click=handler)
```

### TextButton
```python
ft.TextButton(text="Text", on_click=handler)
```

### IconButton
```python
ft.IconButton(
    icon=ft.Icons.ADD,
    icon_color=ft.Colors.BLUE,
    icon_size=24,
    tooltip="Add",
    selected=False,
    selected_icon=ft.Icons.CHECK,
    selected_icon_color=ft.Colors.GREEN,
    on_click=handler,
)
```

### FloatingActionButton
```python
ft.FloatingActionButton(
    icon=ft.Icons.ADD,
    text="Add",
    bgcolor=ft.Colors.BLUE,
    foreground_color=ft.Colors.WHITE,
    mini=False,
    shape=ft.CircleBorder(),
    on_click=handler,
)
```

### PopupMenuButton
```python
ft.PopupMenuButton(
    icon=ft.Icons.MORE_VERT,
    items=[
        ft.PopupMenuItem(text="Edit", icon=ft.Icons.EDIT, on_click=handler),
        ft.PopupMenuItem(text="Delete", icon=ft.Icons.DELETE, on_click=handler),
        ft.PopupMenuItem(),  # Divider
    ],
)
```

### SegmentedButton
```python
ft.SegmentedButton(
    selected={"opt1"},
    allow_empty_selection=False,
    allow_multiple_selection=False,
    segments=[
        ft.Segment(value="opt1", label=ft.Text("Day"), icon=ft.Icon(ft.Icons.CALENDAR_TODAY)),
        ft.Segment(value="opt2", label=ft.Text("Week")),
    ],
    on_change=handler,
)
```

### CupertinoButton
iOS-style button.
```python
ft.CupertinoButton(
    text="iOS Button",
    color=ft.Colors.BLUE,
    on_click=handler,
)
```

---

## Display Controls

### Text
```python
ft.Text(
    value="Hello",
    spans=[ft.TextSpan("World", style=ft.TextStyle(color=ft.Colors.RED))],
    size=16,
    weight=ft.FontWeight.NORMAL,  # BOLD, W100-W900
    italic=False,
    font_family="Roboto",
    color=ft.Colors.BLACK,
    bgcolor=ft.Colors.YELLOW,
    text_align=ft.TextAlign.LEFT,
    overflow=ft.TextOverflow.ELLIPSIS,
    max_lines=2,
    selectable=False,
    no_wrap=False,
    style=ft.TextStyle(...),
    theme_style=ft.TextThemeStyle.BODY_MEDIUM,
)
```

### Icon
```python
ft.Icon(
    name=ft.Icons.FAVORITE,
    color=ft.Colors.RED,
    size=24,
    tooltip="Favorite",
)
```

### Image
```python
ft.Image(
    src="path/to/image.png",  # Local path, URL, or base64
    src_base64="...",
    width=200,
    height=200,
    fit=ft.ImageFit.CONTAIN,  # CONTAIN, COVER, FILL, FIT_WIDTH, FIT_HEIGHT, NONE, SCALE_DOWN
    repeat=ft.ImageRepeat.NO_REPEAT,
    border_radius=ft.border_radius.all(10),
    color=ft.Colors.BLUE,  # Tint color
    color_blend_mode=ft.BlendMode.MODULATE,
    gapless_playback=False,
    error_content=ft.Text("Failed to load"),
)
```

### CircleAvatar
```python
ft.CircleAvatar(
    foreground_image_src="avatar.png",
    content=ft.Text("AB"),
    radius=30,
    bgcolor=ft.Colors.BLUE,
    color=ft.Colors.WHITE,
)
```

### ProgressBar
```python
ft.ProgressBar(
    value=0.5,  # None for indeterminate
    width=200,
    bar_height=4,
    color=ft.Colors.BLUE,
    bgcolor=ft.Colors.GREY_200,
)
```

### ProgressRing
```python
ft.ProgressRing(
    value=0.5,  # None for indeterminate
    width=50,
    height=50,
    stroke_width=4,
    color=ft.Colors.BLUE,
    bgcolor=ft.Colors.GREY_200,
)
```

### Badge
```python
ft.Badge(
    content=ft.Icon(ft.Icons.SHOPPING_CART),
    text="3",
    small_size=10,
    large_size=20,
    bgcolor=ft.Colors.RED,
    text_color=ft.Colors.WHITE,
)
```

### Tooltip
```python
ft.Tooltip(
    message="Helpful tip",
    content=ft.Icon(ft.Icons.INFO),
    padding=10,
    vertical_offset=20,
    prefer_below=True,
    wait_duration=500,
    show_duration=2000,
)
```

### Markdown
```python
ft.Markdown(
    value="# Hello **World**",
    selectable=True,
    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
    code_theme=ft.MarkdownCodeTheme.GITHUB,
    code_style=ft.TextStyle(font_family="monospace"),
    on_tap_link=lambda e: page.launch_url(e.data),
)
```

### Lottie
Animation player.
```python
ft.Lottie(
    src="animation.json",
    repeat=True,
    reverse=False,
    animate=True,
)
```

---

## Data Controls

### DataTable
```python
ft.DataTable(
    columns=[
        ft.DataColumn(ft.Text("Name"), numeric=False, tooltip="Name column", on_sort=handler),
        ft.DataColumn(ft.Text("Age"), numeric=True),
    ],
    rows=[
        ft.DataRow(
            cells=[ft.DataCell(ft.Text("Alice")), ft.DataCell(ft.Text("30"))],
            selected=False,
            on_select_changed=handler,
            on_long_press=handler,
            color=ft.Colors.BLUE_50,
        ),
    ],
    sort_column_index=0,
    sort_ascending=True,
    show_checkbox_column=False,
    heading_row_color=ft.Colors.GREY_200,
    heading_row_height=56,
    data_row_min_height=48,
    data_row_max_height=100,
    horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY),
    vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY),
    divider_thickness=1,
    column_spacing=56,
)
```

### ListTile
```python
ft.ListTile(
    leading=ft.Icon(ft.Icons.ALBUM),
    title=ft.Text("Title"),
    subtitle=ft.Text("Subtitle"),
    trailing=ft.Icon(ft.Icons.ARROW_FORWARD_IOS),
    is_three_line=False,
    dense=False,
    content_padding=ft.Padding(horizontal=16),
    selected=False,
    autofocus=False,
    on_click=handler,
    on_long_press=handler,
)
```

### Chip
```python
ft.Chip(
    label=ft.Text("Tag"),
    leading=ft.Icon(ft.Icons.TAG),
    delete_icon=ft.Icon(ft.Icons.CLOSE),
    selected=False,
    disabled=False,
    autofocus=False,
    bgcolor=ft.Colors.BLUE_100,
    on_click=handler,
    on_delete=handler,
    on_select=handler,
)
```

### TreeView
```python
ft.TreeView(
    controls=[
        ft.TreeViewItem(
            title=ft.Text("Folder"),
            icon=ft.Icon(ft.Icons.FOLDER),
            children=[
                ft.TreeViewItem(title=ft.Text("File"), icon=ft.Icon(ft.Icons.FILE_PRESENT)),
            ],
            expanded=True,
        ),
    ],
    on_change=handler,
)
```

---

## Dialog/Overlay Controls

### AlertDialog
```python
ft.AlertDialog(
    modal=True,
    title=ft.Text("Title"),
    content=ft.Text("Content"),
    actions=[
        ft.TextButton("Cancel", on_click=lambda e: page.close(dialog)),
        ft.TextButton("OK", on_click=lambda e: page.close(dialog)),
    ],
    actions_alignment=ft.MainAxisAlignment.END,
    shape=ft.RoundedRectangleBorder(radius=10),
    on_dismiss=handler,
)
# Open with: page.open(dialog)
```

### BottomSheet
```python
ft.BottomSheet(
    content=ft.Container(content=..., padding=20),
    open=False,
    dismissible=True,
    enable_drag=True,
    show_drag_handle=True,
    use_safe_area=True,
    on_dismiss=handler,
)
# Open with: page.open(bottom_sheet)
```

### Banner
```python
ft.Banner(
    content=ft.Text("Message"),
    leading=ft.Icon(ft.Icons.WARNING),
    actions=[
        ft.TextButton("Dismiss", on_click=lambda e: page.close(banner)),
    ],
    bgcolor=ft.Colors.AMBER_100,
)
# Open with: page.open(banner)
```

### SnackBar
```python
ft.SnackBar(
    content=ft.Text("Message"),
    action="Undo",
    action_color=ft.Colors.BLUE,
    duration=4000,
    show_close_icon=True,
    close_icon_color=ft.Colors.WHITE,
    bgcolor=ft.Colors.GREY_900,
    on_action=handler,
)
# Open with: page.open(snack_bar)
```

### CupertinoAlertDialog
iOS-style dialog.
```python
ft.CupertinoAlertDialog(
    title=ft.Text("Title"),
    content=ft.Text("Content"),
    actions=[
        ft.CupertinoDialogAction(text="Cancel", is_default_action=True, on_click=handler),
        ft.CupertinoDialogAction(text="OK", is_destructive_action=True, on_click=handler),
    ],
)
```

---

## Utility Controls

### FilePicker
```python
file_picker = ft.FilePicker(
    on_result=handler,  # FilePickerResultEvent
    on_upload=handler,
)
page.overlay.append(file_picker)

# Pick files
file_picker.pick_files(
    dialog_title="Select files",
    initial_directory="/home",
    file_type=ft.FilePickerFileType.CUSTOM,
    allowed_extensions=["pdf", "txt"],
    allow_multiple=True,
)

# Save file
file_picker.save_file(
    dialog_title="Save file",
    file_name="document.txt",
    file_type=ft.FilePickerFileType.CUSTOM,
    allowed_extensions=["txt"],
)

# Get directory
file_picker.get_directory_path(dialog_title="Select folder")
```

### Audio
```python
audio = ft.Audio(
    src="audio.mp3",
    autoplay=False,
    volume=1.0,
    balance=0.0,
    playback_rate=1.0,
    on_loaded=handler,
    on_duration_changed=handler,
    on_position_changed=handler,
    on_state_changed=handler,
)
page.overlay.append(audio)

audio.play()
audio.pause()
audio.resume()
audio.seek(1000)  # milliseconds
audio.release()
```

### Video
```python
ft.Video(
    playlist=[
        ft.VideoMedia("video.mp4"),
        ft.VideoMedia("https://example.com/video.mp4"),
    ],
    autoplay=False,
    show_controls=True,
    aspect_ratio=16/9,
    volume=100,
    playback_rate=1.0,
    filter_quality=ft.FilterQuality.HIGH,
    on_loaded=handler,
    on_completed=handler,
    on_error=handler,
)
```

### WebView
```python
ft.WebView(
    url="https://example.com",
    javascript_enabled=True,
    prevent_link=False,
    on_page_started=handler,
    on_page_ended=handler,
    on_web_resource_error=handler,
)
```

### GestureDetector
```python
ft.GestureDetector(
    content=ft.Container(...),
    mouse_cursor=ft.MouseCursor.CLICK,
    drag_interval=10,
    on_tap=handler,
    on_tap_down=handler,
    on_tap_up=handler,
    on_double_tap=handler,
    on_long_press=handler,
    on_secondary_tap=handler,
    on_pan_start=handler,
    on_pan_update=handler,
    on_pan_end=handler,
    on_scale_start=handler,
    on_scale_update=handler,
    on_scale_end=handler,
    on_hover=handler,
    on_enter=handler,
    on_exit=handler,
    on_scroll=handler,
)
```

### ShaderMask
```python
ft.ShaderMask(
    content=ft.Image(src="image.png"),
    shader=ft.LinearGradient(
        begin=ft.Alignment.TOP_CENTER,
        end=ft.Alignment.BOTTOM_CENTER,
        colors=[ft.Colors.BLACK, ft.Colors.TRANSPARENT],
    ),
    blend_mode=ft.BlendMode.DST_IN,
)
```

### AnimatedSwitcher
```python
ft.AnimatedSwitcher(
    content=current_control,
    duration=300,
    reverse_duration=300,
    switch_in_curve=ft.AnimationCurve.EASE_IN,
    switch_out_curve=ft.AnimationCurve.EASE_OUT,
    transition=ft.AnimatedSwitcherTransition.FADE,
)
```

---

## Charts

### BarChart
```python
ft.BarChart(
    bar_groups=[
        ft.BarChartGroup(
            x=0,
            bar_rods=[
                ft.BarChartRod(from_y=0, to_y=40, width=40, color=ft.Colors.BLUE),
            ],
        ),
    ],
    border=ft.border.all(1, ft.Colors.GREY),
    left_axis=ft.ChartAxis(labels_size=40),
    bottom_axis=ft.ChartAxis(labels=[ft.ChartAxisLabel(value=0, label=ft.Text("Jan"))]),
    horizontal_grid_lines=ft.ChartGridLines(color=ft.Colors.GREY_300),
    tooltip_bgcolor=ft.Colors.WHITE,
    max_y=100,
    interactive=True,
    on_chart_event=handler,
)
```

### LineChart
```python
ft.LineChart(
    data_series=[
        ft.LineChartData(
            data_points=[
                ft.LineChartDataPoint(0, 10),
                ft.LineChartDataPoint(1, 20),
            ],
            stroke_width=2,
            color=ft.Colors.BLUE,
            curved=True,
            below_line_bgcolor=ft.Colors.BLUE_100,
        ),
    ],
    border=ft.border.all(1, ft.Colors.GREY),
    left_axis=ft.ChartAxis(labels_size=40),
    bottom_axis=ft.ChartAxis(labels_size=40),
    horizontal_grid_lines=ft.ChartGridLines(color=ft.Colors.GREY_300),
    vertical_grid_lines=ft.ChartGridLines(color=ft.Colors.GREY_300),
    tooltip_bgcolor=ft.Colors.WHITE,
    min_x=0, max_x=10,
    min_y=0, max_y=100,
    interactive=True,
    on_chart_event=handler,
)
```

### PieChart
```python
ft.PieChart(
    sections=[
        ft.PieChartSection(
            value=40,
            title="40%",
            title_style=ft.TextStyle(color=ft.Colors.WHITE),
            color=ft.Colors.BLUE,
            radius=100,
        ),
    ],
    sections_space=2,
    center_space_radius=40,
    center_space_color=ft.Colors.WHITE,
    on_chart_event=handler,
)
```

### ScatterChart
```python
ft.ScatterChart(
    data_series=[
        ft.ScatterChartData(
            data_points=[
                ft.ScatterChartDataPoint(1, 1, radius=5, color=ft.Colors.BLUE),
            ],
        ),
    ],
    border=ft.border.all(1, ft.Colors.GREY),
    left_axis=ft.ChartAxis(labels_size=40),
    bottom_axis=ft.ChartAxis(labels_size=40),
    horizontal_grid_lines=ft.ChartGridLines(color=ft.Colors.GREY_300),
    vertical_grid_lines=ft.ChartGridLines(color=ft.Colors.GREY_300),
    min_x=0, max_x=10,
    min_y=0, max_y=10,
    on_chart_event=handler,
)
```

---

## Media Controls

### Camera (requires flet_camera package)
```python
# pip install flet-camera
from flet_camera import Camera

camera = Camera(
    resolution=ft.CameraResolution.MAX,
    on_capture=handler,
)
```

### GoogleMobileAds (requires flet_ads package)
```python
# pip install flet-ads
from flet_ads import BannerAd

ad = BannerAd(
    unit_id="ca-app-pub-xxx/xxx",
    on_click=handler,
    on_close=handler,
    on_error=handler,
    on_impression=handler,
    on_open=handler,
    on_will_dismiss=handler,
)
```

---

## Common Properties (All Controls)

Most controls support these properties:
```python
control.visible = True
control.disabled = False
control.expand = 1  # Fill available space
control.col = {"sm": 6, "md": 4}  # ResponsiveRow sizing
control.opacity = 1.0
control.tooltip = "Helpful tip"
control.data = {"custom": "data"}  # Arbitrary data attachment
control.ref = ft.Ref[ft.Text]()  # Reference for later access
control.key = "unique_key"  # For efficient updates
```
