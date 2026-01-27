# Theme System Documentation

This document describes the theming framework for Newsletter Reader, allowing users to customize colors, typography, and visual elements.

## Quick Start

1. Go to **Settings > Themes**
2. Click on a theme to preview it
3. Click **Apply Theme** to activate
4. Import custom themes using the **Import Theme** button
5. Export the current theme using **Export Current**

## Theme File Location

Theme files are stored in the user data directory:
- **Linux**: `~/.local/share/mr-newsletter/themes/`
- **macOS**: `~/Library/Application Support/mr-newsletter/themes/`
- **Windows**: `%LOCALAPPDATA%/mr-newsletter/themes/`

## Built-in Themes

Two themes are included by default:
1. **Default** - Sophistication & Trust palette with cool slate tones and blue accent
2. **Dark Slate** - OLED-optimized deep dark theme with indigo accent

Built-in themes cannot be deleted.

## Theme Schema

Themes are JSON files with the following structure:

```json
{
  "metadata": {
    "name": "Theme Name",
    "author": "Author Name",
    "version": "1.0.0",
    "description": "Theme description",
    "base": "light"
  },
  "colors": {
    "light": { /* light mode colors */ },
    "dark": { /* dark mode colors */ }
  },
  "typography": { /* optional typography overrides */ },
  "spacing": { /* optional spacing overrides */ },
  "border_radius": { /* optional border radius overrides */ },
  "shadows": { /* optional shadow definitions */ },
  "animation": { /* optional animation timings */ },
  "section_overrides": { /* optional section-specific overrides */ }
}
```

### Metadata Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Display name shown in theme list |
| `author` | string | No | Theme author name |
| `version` | string | No | Theme version (semver) |
| `description` | string | No | Short description for preview |
| `base` | string | No | Base mode: "light" or "dark" (default: "light") |

### Color Tokens

Each color set (light/dark) can include these tokens:

#### Background Colors
| Token | Description | Default (Light) |
|-------|-------------|-----------------|
| `bg_primary` | Main background | `#FFFFFF` |
| `bg_secondary` | Subtle alternate background | `#F8FAFC` |
| `bg_tertiary` | Cards hover, containers | `#F1F5F9` |
| `bg_elevated` | Modals, dropdowns | `#FFFFFF` |

#### Text Colors
| Token | Description | Default (Light) |
|-------|-------------|-----------------|
| `text_primary` | Headlines, primary text | `#0F172A` |
| `text_secondary` | Body text | `#475569` |
| `text_tertiary` | Captions, hints | `#94A3B8` |
| `text_disabled` | Disabled text | `#CBD5E1` |

#### Border Colors
| Token | Description | Default (Light) |
|-------|-------------|-----------------|
| `border_default` | Standard borders | `#E2E8F0` |
| `border_subtle` | Subtle dividers | `#F1F5F9` |
| `border_strong` | Emphasized borders | `#CBD5E1` |

#### Interactive States
| Token | Description | Default (Light) |
|-------|-------------|-----------------|
| `hover` | Hover background | `#F8FAFC` |
| `active` | Active/pressed state | `#F1F5F9` |
| `focus_ring` | Focus outline color | `#3B82F6` |

#### Accent Colors
| Token | Description | Default (Light) |
|-------|-------------|-----------------|
| `accent` | Primary actions | `#3B82F6` |
| `accent_hover` | Accent hover state | `#2563EB` |
| `accent_muted` | Accent background | `#DBEAFE` |

#### Semantic Colors
| Token | Description | Default (Light) |
|-------|-------------|-----------------|
| `success` | Success states | `#22C55E` |
| `success_muted` | Success background | `#DCFCE7` |
| `warning` | Warnings | `#F59E0B` |
| `warning_muted` | Warning background | `#FEF3C7` |
| `error` | Errors | `#EF4444` |
| `error_muted` | Error background | `#FEE2E2` |

#### Special Colors
| Token | Description | Default (Light) |
|-------|-------------|-----------------|
| `unread_dot` | Unread indicator | `#3B82F6` |
| `star_active` | Starred state | `#F59E0B` |
| `star_inactive` | Unstarred state | `#CBD5E1` |

### Typography (Optional)

```json
{
  "typography": {
    "font_family": "Inter",
    "h1_size": 28,
    "h2_size": 22,
    "h3_size": 18,
    "h4_size": 16,
    "body_size": 14,
    "body_small_size": 13,
    "caption_size": 12,
    "weight_bold": 600,
    "weight_medium": 500,
    "weight_regular": 400
  }
}
```

### Spacing (Optional)

```json
{
  "spacing": {
    "none": 0,
    "xxs": 4,
    "xs": 8,
    "sm": 12,
    "md": 16,
    "lg": 24,
    "xl": 32,
    "xxl": 48
  }
}
```

### Border Radius (Optional)

```json
{
  "border_radius": {
    "none": 0,
    "sm": 6,
    "md": 8,
    "lg": 12,
    "full": 999
  }
}
```

### Section Overrides (Optional)

Override specific UI sections:

```json
{
  "section_overrides": {
    "sidebar": {
      "bg": "#1A1A2E",
      "width": 280
    },
    "cards": {
      "bg": "#FFFFFF",
      "shadow": "0 2px 4px rgba(0,0,0,0.1)"
    },
    "emails": {
      "unread_bg": "#EEF2FF"
    },
    "dialogs": {
      "bg": "#FFFFFF"
    }
  }
}
```

## Fallback Behavior

Missing properties automatically fall back to default values:

1. If a color token is missing → Uses default from `Colors.Light` or `Colors.Dark`
2. If entire `colors.light` section is missing → Uses default light colors
3. If entire `colors.dark` section is missing → Uses default dark colors
4. If any other section is missing → Uses corresponding default class

This means you can create a minimal theme with just the colors you want to change:

```json
{
  "metadata": {
    "name": "Blue Accent Only",
    "description": "Custom blue accent, everything else default"
  },
  "colors": {
    "light": {
      "accent": "#2563EB",
      "accent_hover": "#1D4ED8",
      "accent_muted": "#DBEAFE"
    },
    "dark": {
      "accent": "#60A5FA",
      "accent_hover": "#3B82F6",
      "accent_muted": "#1E3A5F"
    }
  }
}
```

## Example Themes

### Nord Theme Pattern

```json
{
  "metadata": {
    "name": "Nord",
    "author": "Arctic Ice Studio",
    "version": "1.0.0",
    "description": "Arctic, north-bluish color palette",
    "base": "dark"
  },
  "colors": {
    "light": {
      "bg_primary": "#ECEFF4",
      "bg_secondary": "#E5E9F0",
      "bg_tertiary": "#D8DEE9",
      "text_primary": "#2E3440",
      "text_secondary": "#3B4252",
      "text_tertiary": "#4C566A",
      "accent": "#5E81AC",
      "accent_hover": "#81A1C1",
      "accent_muted": "#D8DEE9",
      "success": "#A3BE8C",
      "warning": "#EBCB8B",
      "error": "#BF616A"
    },
    "dark": {
      "bg_primary": "#2E3440",
      "bg_secondary": "#3B4252",
      "bg_tertiary": "#434C5E",
      "text_primary": "#ECEFF4",
      "text_secondary": "#E5E9F0",
      "text_tertiary": "#D8DEE9",
      "accent": "#88C0D0",
      "accent_hover": "#8FBCBB",
      "accent_muted": "#3B4252",
      "success": "#A3BE8C",
      "warning": "#EBCB8B",
      "error": "#BF616A"
    }
  }
}
```

### Dracula Theme Pattern

```json
{
  "metadata": {
    "name": "Dracula",
    "author": "Zeno Rocha",
    "version": "1.0.0",
    "description": "Dark theme with purple accent",
    "base": "dark"
  },
  "colors": {
    "light": {
      "bg_primary": "#F8F8F2",
      "bg_secondary": "#F1F1E6",
      "text_primary": "#282A36",
      "accent": "#BD93F9",
      "accent_hover": "#FF79C6",
      "success": "#50FA7B",
      "warning": "#F1FA8C",
      "error": "#FF5555"
    },
    "dark": {
      "bg_primary": "#282A36",
      "bg_secondary": "#44475A",
      "bg_tertiary": "#6272A4",
      "text_primary": "#F8F8F2",
      "text_secondary": "#F8F8F2",
      "text_tertiary": "#6272A4",
      "accent": "#BD93F9",
      "accent_hover": "#FF79C6",
      "accent_muted": "#44475A",
      "success": "#50FA7B",
      "warning": "#F1FA8C",
      "error": "#FF5555"
    }
  }
}
```

### Solarized Theme Pattern

```json
{
  "metadata": {
    "name": "Solarized",
    "author": "Ethan Schoonover",
    "version": "1.0.0",
    "description": "Precision colors for machines and people",
    "base": "light"
  },
  "colors": {
    "light": {
      "bg_primary": "#FDF6E3",
      "bg_secondary": "#EEE8D5",
      "bg_tertiary": "#E0DAC5",
      "text_primary": "#073642",
      "text_secondary": "#586E75",
      "text_tertiary": "#93A1A1",
      "accent": "#268BD2",
      "accent_hover": "#2AA198",
      "success": "#859900",
      "warning": "#B58900",
      "error": "#DC322F"
    },
    "dark": {
      "bg_primary": "#002B36",
      "bg_secondary": "#073642",
      "bg_tertiary": "#094554",
      "text_primary": "#FDF6E3",
      "text_secondary": "#EEE8D5",
      "text_tertiary": "#93A1A1",
      "accent": "#268BD2",
      "accent_hover": "#2AA198",
      "accent_muted": "#073642",
      "success": "#859900",
      "warning": "#B58900",
      "error": "#DC322F"
    }
  }
}
```

## Creating Custom Themes

1. **Start from a template**: Export an existing theme and modify it
2. **Test both modes**: Ensure both light and dark variants look good
3. **Check contrast**: Ensure text is readable against backgrounds
4. **Use hex colors**: All colors should be hex format (`#RRGGBB`)
5. **Validate JSON**: Use a JSON validator before importing

## Troubleshooting

### Theme doesn't load
- Check JSON syntax is valid
- Ensure file has `.json` extension
- Check color values are valid hex codes

### Colors look wrong
- Verify you're editing the correct mode (light/dark)
- Check for typos in color token names
- Ensure colors have proper contrast

### Theme reverts after restart
- Check the theme file still exists in the themes directory
- Ensure the theme filename matches what's saved in settings

## Technical Notes

- Themes are validated using Pydantic models on load
- Invalid properties are silently ignored (fallback to defaults)
- Theme changes require page recreation to fully apply
- The active theme filename is stored in the SQLite database
