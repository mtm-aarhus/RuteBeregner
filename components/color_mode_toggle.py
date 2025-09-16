"""
Color Mode Toggle komponent for Dark Mode funktionalitet
"""
import reflex as rx
from jord_transport.jord_transport import State


def color_mode_toggle() -> rx.Component:
    """
    Color mode toggle med segmented control for system/light/dark valg.
    
    Bruger ikoner:
    - monitor: System preference
    - sun: Light mode  
    - moon: Dark mode
    
    Returns:
        rx.Component: Segmented control komponent
    """
    return rx.segmented_control.root(
        rx.segmented_control.item(
            rx.tooltip(
                rx.icon(tag="monitor", size=16),
                content="System",
                side="top",
            ),
            value="system",
        ),
        rx.segmented_control.item(
            rx.tooltip(
                rx.icon(tag="sun", size=16),
                content="Light", 
                side="top",
            ),
            value="light",
        ),
        rx.segmented_control.item(
            rx.tooltip(
                rx.icon(tag="moon", size=16),
                content="Dark",
                side="top", 
            ),
            value="dark",
        ),
        on_change=State.set_color_mode,
        variant="classic",
        radius="large", 
        value=State.color_mode,
        size="2",
        # Better visibility styling
        style={
            "background": "var(--color-bg-card)",
            "border": "1px solid var(--color-border-primary)",
            "color": "var(--color-text-primary)",
        },
        # Accessibility
        aria_label="Vælg farvetema",
    )


def color_mode_toggle_with_label() -> rx.Component:
    """
    Color mode toggle med label for bedre accessibility.
    
    Returns:
        rx.Component: Toggle med label
    """
    return rx.vstack(
        rx.text(
            "Farvetema",
            font_weight="medium", 
            color="gray.11",
            size="2"
        ),
        color_mode_toggle(),
        spacing="2",
        align="center",
    )


def compact_color_mode_toggle() -> rx.Component:
    """
    Kompakt version af color mode toggle til header brug.
    
    Returns:
        rx.Component: Kompakt toggle uden label
    """
    return rx.tooltip(
        color_mode_toggle(),
        content="Skift farvetema",
        side="bottom",
    )