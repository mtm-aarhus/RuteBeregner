"""
Utility funktioner til theme-aware styling
"""
from typing import Dict, Any, Union


def themed_style(**kwargs) -> Dict[str, str]:
    """
    Opretter theme-aware styles ved hjælp af CSS variabler.
    
    Eksempel:
        themed_style(
            background_color="var(--color-bg-primary)",
            color="var(--color-text-primary)",
            border_color="var(--color-border-primary)"
        )
    
    Returns:
        Dict med CSS styles der reagerer på theme changes
    """
    styles = {}
    
    for prop, value in kwargs.items():
        if isinstance(value, str) and value.startswith("var("):
            # CSS variable - use as is
            styles[prop] = value
        else:
            # Regular value
            styles[prop] = value
    
    return styles


def card_style(elevated: bool = False) -> Dict[str, str]:
    """
    Standard card styling der tilpasser sig theme.
    
    Args:
        elevated: Om kortet skal have shadow/elevation
        
    Returns:
        Dict med card styles
    """
    base_style = themed_style(
        background_color="var(--color-bg-card)",
        border="1px solid var(--color-border-primary)",
        border_radius="0.5rem",
    )
    
    if elevated:
        base_style["box_shadow"] = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    
    return base_style


def text_style(variant: str = "primary") -> Dict[str, str]:
    """
    Text styling baseret på variant.
    
    Args:
        variant: primary, secondary, muted
        
    Returns:
        Dict med text styles
    """
    variants = {
        "primary": "var(--color-text-primary)",
        "secondary": "var(--color-text-secondary)", 
        "tertiary": "var(--color-text-tertiary)",
        "muted": "var(--color-text-muted)",
        "inverse": "var(--color-text-inverse)",
    }
    
    return themed_style(
        color=variants.get(variant, variants["primary"])
    )


def button_style(variant: str = "primary", size: str = "medium") -> Dict[str, str]:
    """
    Button styling der tilpasser sig theme.
    
    Args:
        variant: primary, secondary, outline, ghost
        size: small, medium, large
        
    Returns:
        Dict med button styles
    """
    base_style = {
        "transition": "var(--transition-colors)",
        "font_weight": "medium",
        "border_radius": "0.375rem",
        "cursor": "pointer",
    }
    
    # Size variants
    sizes = {
        "small": {"padding": "0.5rem 1rem", "font_size": "0.875rem"},
        "medium": {"padding": "0.625rem 1.25rem", "font_size": "1rem"},
        "large": {"padding": "0.75rem 1.5rem", "font_size": "1.125rem"},
    }
    
    base_style.update(sizes.get(size, sizes["medium"]))
    
    # Variant styles
    if variant == "primary":
        base_style.update({
            "background_color": "var(--color-primary-600)",
            "color": "var(--color-text-inverse)",
            "border": "1px solid var(--color-primary-600)",
        })
    elif variant == "secondary":
        base_style.update({
            "background_color": "var(--color-bg-secondary)", 
            "color": "var(--color-text-primary)",
            "border": "1px solid var(--color-border-primary)",
        })
    elif variant == "outline":
        base_style.update({
            "background_color": "transparent",
            "color": "var(--color-primary-600)",
            "border": "1px solid var(--color-primary-600)",
        })
    elif variant == "ghost":
        base_style.update({
            "background_color": "transparent",
            "color": "var(--color-text-primary)",
            "border": "1px solid transparent",
        })
    
    return base_style


def input_style() -> Dict[str, str]:
    """
    Input field styling der tilpasser sig theme.
    
    Returns:
        Dict med input styles  
    """
    return themed_style(
        background_color="var(--color-bg-primary)",
        border="1px solid var(--color-border-primary)",
        border_radius="0.375rem",
        color="var(--color-text-primary)",
        padding="0.5rem 0.75rem",
        transition="var(--transition-colors)",
        # Focus states
        _focus={
            "outline": "none",
            "border_color": "var(--color-border-focus)",
            "box_shadow": "0 0 0 3px rgba(59, 130, 246, 0.1)",
        }
    )


def navigation_style() -> Dict[str, str]:
    """
    Navigation bar styling.
    
    Returns:
        Dict med navigation styles
    """
    return themed_style(
        background_color="var(--color-bg-secondary)",
        border_bottom="1px solid var(--color-border-primary)",
        backdrop_filter="blur(8px)",
    )


def status_color(status: str) -> str:
    """
    Få farve for status.
    
    Args:
        status: success, warning, error, info
        
    Returns:
        CSS variable for status farve
    """
    return f"var(--color-{status})"


# Helper functions for common patterns
def theme_card(**extra_props) -> Dict[str, str]:
    """Shorthand for theme-aware card."""
    return {**card_style(), **extra_props}


def theme_text(variant: str = "primary", **extra_props) -> Dict[str, str]:
    """Shorthand for theme-aware text."""
    return {**text_style(variant), **extra_props}


def theme_button(variant: str = "primary", size: str = "medium", **extra_props) -> Dict[str, str]:
    """Shorthand for theme-aware button."""
    return {**button_style(variant, size), **extra_props}