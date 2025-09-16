"""
Toast notification komponent for RuteBeregner applikationen.
"""
import reflex as rx
from jord_transport.jord_transport import State


def toast_notification() -> rx.Component:
    """
    Toast notifikation komponent med automatisk skjul efter 5 sekunder.
    
    Returns:
        rx.Component: Toast notification med lukkemulighed
    """
    return rx.cond(
        State.show_toast,
        rx.box(
            rx.hstack(
                # Icon baseret på toast type
                rx.cond(
                    State.toast_type == "success",
                    rx.icon("check", size=20, color="green.9"),
                    rx.cond(
                        State.toast_type == "error",
                        rx.icon("x", size=20, color="red.9"),
                        rx.cond(
                            State.toast_type == "warning",
                            rx.icon("triangle-alert", size=20, color="orange.9"),
                            rx.icon("info", size=20, color="blue.9"),  # info default
                        ),
                    ),
                ),
                
                # Toast besked
                rx.text(
                    State.toast_message,
                    font_weight="medium",
                    color="gray.12",
                    flex="1",
                ),
                
                # Luk knap
                rx.button(
                    rx.icon("x", size=16),
                    on_click=State.hide_toast_notification,
                    size="1",
                    variant="soft",
                    color_scheme="gray",
                ),
                
                spacing="3",
                align="center",
                width="100%",
            ),
            
            # Styling baseret på toast type
            background=rx.cond(
                State.toast_type == "success",
                "green.3",
                rx.cond(
                    State.toast_type == "error",
                    "red.3",
                    rx.cond(
                        State.toast_type == "warning",
                        "orange.3",
                        "blue.3",  # info default
                    ),
                ),
            ),
            border=rx.cond(
                State.toast_type == "success",
                "1px solid",
                rx.cond(
                    State.toast_type == "error",
                    "1px solid",
                    rx.cond(
                        State.toast_type == "warning",
                        "1px solid",
                        "1px solid",  # info default
                    ),
                ),
            ),
            border_color=rx.cond(
                State.toast_type == "success",
                "green.6",
                rx.cond(
                    State.toast_type == "error",
                    "red.6",
                    rx.cond(
                        State.toast_type == "warning",
                        "orange.6",
                        "blue.6",  # info default
                    ),
                ),
            ),
            
            # Layout styling
            border_radius="lg",
            padding="1rem",
            box_shadow="lg",
            max_width="400px",
            margin="1rem",
            
            # Position fixed til top-right
            position="fixed",
            top="80px",
            right="20px",
            z_index="1000",
        ),
        rx.fragment(),
    )


def progress_indicator() -> rx.Component:
    """
    Progress indicator for bulk distance calculations.
    
    Returns:
        rx.Component: Progress bar med current/total progress
    """
    return rx.cond(
        State.calculation_progress.get("in_progress", False),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("calculator", size=16, color="blue.9"),
                    rx.text("Beregner afstande...", font_weight="medium", color="gray.11"),
                    rx.spacer(),
                    rx.text(
                        f"{State.calculation_progress.get('current', 0)}/{State.calculation_progress.get('total', 0)}",
                        font_size="sm",
                        color="gray.10",
                    ),
                    width="100%",
                    align="center",
                ),
                
                # Progress bar
                rx.box(
                    rx.box(
                        width="50%",
                        height="100%",
                        background="blue.8",
                        border_radius="full",
                        transition="width 0.3s ease",
                    ),
                    width="100%",
                    height="8px",
                    background="gray.6",
                    border_radius="full",
                    overflow="hidden",
                ),
                
                spacing="2",
                width="100%",
            ),
            
            padding="1rem",
            background="gray.2",
            border_radius="lg",
            border="1px solid",
            border_color="blue.6",
            box_shadow="md",
            margin_bottom="1rem",
        ),
        rx.fragment(),
    )