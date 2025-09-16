"""
Custom farvetema system for Light/Dark mode support
"""
import reflex as rx
from typing import Dict, Any


# Define color tokens for both light and dark modes
LIGHT_THEME_COLORS = {
    # Primary colors - enhanced for better light theme contrast
    "primary": {
        "50": "#f0f9ff",
        "100": "#e0f2fe", 
        "200": "#bae6fd",
        "300": "#7dd3fc",
        "400": "#38bdf8",
        "500": "#0ea5e9",
        "600": "#0284c7",
        "700": "#0369a1",
        "800": "#075985",
        "900": "#0c4a6e",
        "950": "#082f49"
    },
    # Background colors - optimized for light theme with better contrast
    "background": {
        "primary": "#ffffff",
        "secondary": "#f8fafc",  # Preserved current header color
        "tertiary": "#f1f5f9", 
        "card": "#ffffff",
        "overlay": "rgba(15, 23, 42, 0.05)"
    },
    # Text colors - enhanced contrast for better readability
    "text": {
        "primary": "#0f172a",
        "secondary": "#1e293b", 
        "tertiary": "#334155",
        "muted": "#64748b",
        "inverse": "#ffffff"
    },
    # Border colors - improved visibility
    "border": {
        "primary": "#e2e8f0",
        "secondary": "#cbd5e1",
        "focus": "#0ea5e9",
        "error": "#dc2626"
    },
    # Status colors - consistent with design system
    "success": "#16a34a",
    "warning": "#d97706",
    "error": "#dc2626",
    "info": "#0ea5e9"
}

DARK_THEME_COLORS = {
    # Primary colors (same as light but applied differently)
    "primary": {
        "50": "#172554",
        "100": "#1e3a8a",
        "200": "#1e40af",
        "300": "#1d4ed8",
        "400": "#2563eb",
        "500": "#3b82f6",
        "600": "#60a5fa",
        "700": "#93c5fd",
        "800": "#bfdbfe",
        "900": "#dbeafe",
        "950": "#eff6ff"
    },
    # Background colors
    "background": {
        "primary": "#0f172a",
        "secondary": "#1e293b",
        "tertiary": "#334155",
        "card": "#1e293b",
        "overlay": "rgba(255, 255, 255, 0.1)"
    },
    # Text colors
    "text": {
        "primary": "#f8fafc",
        "secondary": "#cbd5e1",
        "tertiary": "#94a3b8",
        "muted": "#64748b",
        "inverse": "#0f172a"
    },
    # Border colors
    "border": {
        "primary": "#334155",
        "secondary": "#475569",
        "focus": "#60a5fa", 
        "error": "#ef4444"
    },
    # Status colors
    "success": "#22c55e",
    "warning": "#f59e0b", 
    "error": "#ef4444",
    "info": "#60a5fa"
}


def get_base_theme() -> rx.theme:
    """
    Returnerer base theme konfiguration der virker med begge modes.
    """
    return rx.theme(
        appearance="inherit",  # Will be controlled by CSS
        has_background=True,
        radius="medium", 
        scaling="100%",
        accent_color="blue",
        gray_color="slate",
    )


def generate_css_variables() -> str:
    """
    Genererer CSS variabler for både light og dark mode.
    
    Returns:
        str: CSS string med alle color variables
    """
    css = """
:root {
    /* Light mode colors - enhanced for better contrast and visibility */
    --color-primary-50: #f0f9ff;
    --color-primary-100: #e0f2fe;
    --color-primary-200: #bae6fd;
    --color-primary-300: #7dd3fc;
    --color-primary-400: #38bdf8;
    --color-primary-500: #0ea5e9;
    --color-primary-600: #0284c7;
    --color-primary-700: #0369a1;
    --color-primary-800: #075985;
    --color-primary-900: #0c4a6e;
    
    --color-bg-primary: #ffffff;
    --color-bg-secondary: #f1f5f9;  /* Light gray for tab list in light mode */
    --color-bg-tertiary: #f1f5f9;
    --color-bg-card: #ffffff;
    --color-bg-overlay: rgba(15, 23, 42, 0.05);
    
    --color-text-primary: #0f172a;
    --color-text-secondary: #1e293b;
    --color-text-tertiary: #334155;
    --color-text-muted: #64748b;
    --color-text-inverse: #ffffff;
    
    --color-border-primary: #e2e8f0;
    --color-border-secondary: #cbd5e1;
    --color-border-focus: #0ea5e9;
    --color-border-error: #dc2626;
    
    --color-success: #16a34a;
    --color-warning: #d97706;
    --color-error: #dc2626;
    --color-info: #0ea5e9;
    
    /* Accent colors - mapped to primary for consistency */
    --accent-9: #0c4a6e;  /* Deep blue for headings and accents */
    --accent-10: #075985;
    --accent-11: #0369a1;
    --accent-12: #0284c7;
    
    /* Transitions */
    --transition-colors: color 0.2s ease-in-out, background-color 0.2s ease-in-out, border-color 0.2s ease-in-out;
}

[data-color-mode="dark"] {
    /* Dark mode colors */
    --color-primary-50: #172554;
    --color-primary-100: #1e3a8a;
    --color-primary-200: #1e40af;
    --color-primary-300: #1d4ed8;
    --color-primary-400: #2563eb;
    --color-primary-500: #3b82f6;
    --color-primary-600: #60a5fa;
    --color-primary-700: #93c5fd;
    --color-primary-800: #bfdbfe;
    --color-primary-900: #dbeafe;
    
    --color-bg-primary: #0f172a;
    --color-bg-secondary: #1e293b;
    --color-bg-tertiary: #334155;
    --color-bg-card: #1e293b;
    --color-bg-overlay: rgba(255, 255, 255, 0.1);
    
    --color-text-primary: #f8fafc;
    --color-text-secondary: #cbd5e1;
    --color-text-tertiary: #94a3b8;
    --color-text-muted: #64748b;
    --color-text-inverse: #0f172a;
    
    --color-border-primary: #334155;
    --color-border-secondary: #475569;
    --color-border-focus: #60a5fa;
    --color-border-error: #ef4444;
    
    --color-success: #22c55e;
    --color-warning: #f59e0b;
    --color-error: #ef4444;
    --color-info: #60a5fa;
    
    /* Accent colors - brighter for dark mode */
    --accent-9: #7dd3fc;  /* Light blue for headings and accents in dark mode */
    --accent-10: #38bdf8;
    --accent-11: #0ea5e9;
    --accent-12: #0284c7;
}

/* Apply global background and transitions - more specific selectors */
html {
    background-color: var(--color-bg-primary) !important;
}

body {
    background-color: var(--color-bg-primary) !important;
    color: var(--color-text-primary) !important;
    transition: var(--transition-colors);
}

/* Ensure Reflex app container uses theme colors */
#root {
    background-color: var(--color-bg-primary) !important;
    min-height: 100vh;
}

/* Force theme colors on common Reflex components */
.rt-Theme {
    background-color: var(--color-bg-primary) !important;
    color: var(--color-text-primary) !important;
}

/* Apply transitions to common elements */
body, div, span, p, h1, h2, h3, h4, h5, h6 {
    transition: var(--transition-colors);
}

/* Enhanced button and interactive element styling */
button, .rt-Button, .rt-Select, .rt-Input {
    transition: all 0.2s ease-in-out;
}

button:hover, .rt-Button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

button:active, .rt-Button:active {
    transform: translateY(0);
}

/* Input field enhancements */
.rt-Input:hover {
    border-color: var(--color-border-secondary);
}

.rt-Input:focus {
    border-color: var(--color-border-focus);
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

/* Card and container hover effects */
.rt-Card:hover, [data-theme-card]:hover {
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
    transform: translateY(-2px);
    transition: all 0.3s ease;
}

/* Responsive breakpoints */
@media (max-width: 768px) {
    :root {
        --spacing-scale: 0.8;
    }
}

@media (max-width: 480px) {
    :root {
        --spacing-scale: 0.6;
    }
}

/* Ensure smooth color transitions */
* {
    transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out, border-color 0.2s ease-in-out;
}
"""
    return css


def get_theme_aware_style(property_name: str, light_value: str, dark_value: str) -> Dict[str, str]:
    """
    Opretter en style dict der reagerer på color mode.
    
    Args:
        property_name: CSS property navn (f.eks. 'background_color')
        light_value: Værdi for light mode
        dark_value: Værdi for dark mode
        
    Returns:
        Dict med CSS custom property
    """
    return {
        property_name: f"var(--color-{light_value})"
    }


# Semantic color mappings for common UI elements
SEMANTIC_COLORS = {
    "page_background": "bg-primary",
    "card_background": "bg-card", 
    "text_primary": "text-primary",
    "text_secondary": "text-secondary",
    "text_muted": "text-muted",
    "border_default": "border-primary",
    "border_focus": "border-focus",
    "accent_color": "primary-600",
}


def get_semantic_style(semantic_key: str, property: str = "color") -> Dict[str, str]:
    """
    Få style baseret på semantic farve navn.
    
    Args:
        semantic_key: Key fra SEMANTIC_COLORS
        property: CSS property (color, background_color, border_color)
        
    Returns:
        Style dict med CSS variable
    """
    if semantic_key not in SEMANTIC_COLORS:
        return {}
    
    color_var = SEMANTIC_COLORS[semantic_key]
    return {
        property: f"var(--color-{color_var})"
    }


# Export theme configuration
def get_custom_theme_config() -> Dict[str, Any]:
    """
    Returnerer komplet theme konfiguration.
    
    Returns:
        Dict med theme settings
    """
    return {
        "base_theme": get_base_theme(),
        "css_variables": generate_css_variables(),
        "light_colors": LIGHT_THEME_COLORS,
        "dark_colors": DARK_THEME_COLORS,
        "semantic_colors": SEMANTIC_COLORS,
    }