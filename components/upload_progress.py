"""
Upload progress component for displaying file upload and validation progress.
"""
import reflex as rx
from jord_transport.jord_transport import State


def upload_progress_bar() -> rx.Component:
    """
    Progress bar component for file upload and validation.
    
    Returns:
        rx.Component: Progress bar with status text
    """
    return rx.cond(
        State.upload_in_progress | (State.upload_status != ""),
        rx.box(
            rx.vstack(
                # Progress bar header
                rx.hstack(
                    rx.icon(
                        rx.cond(
                            State.upload_status == "error",
                            "x-circle",
                            rx.cond(
                                State.upload_status == "complete",
                                "check-circle",
                                "loader-2"
                            )
                        ),
                        size=20,
                        class_name=rx.cond(
                            (State.upload_status == "") | (State.upload_status == "uploading") | (State.upload_status == "parsing") | (State.upload_status == "validating"),
                            "animate-spin",
                            ""
                        ),
                        style={
                            "color": rx.cond(
                                State.upload_status == "error",
                                "var(--color-error)",
                                rx.cond(
                                    State.upload_status == "complete",
                                    "var(--color-success)",
                                    "var(--color-primary-500)"
                                )
                            )
                        }
                    ),
                    
                    # Status text and filename
                    rx.vstack(
                        rx.text(
                            get_upload_status_text(),
                            font_weight="medium",
                            style={
                                "color": rx.cond(
                                    State.upload_status == "error",
                                    "var(--color-error)",
                                    rx.cond(
                                        State.upload_status == "complete",
                                        "var(--color-success)",
                                        "var(--color-text-primary)"
                                    )
                                )
                            }
                        ),
                        rx.cond(
                            State.current_file_name != "",
                            rx.text(
                                State.current_file_name,
                                font_size="sm",
                                style={"color": "var(--color-text-secondary)"}
                            ),
                            rx.fragment()
                        ),
                        spacing="1",
                        align="start"
                    ),
                    
                    rx.spacer(),
                    
                    # Progress percentage
                    rx.text(
                        f"{State.upload_progress:.0f}%",
                        font_weight="medium",
                        font_size="sm",
                        style={"color": "var(--color-text-secondary)"}
                    ),
                    
                    width="100%",
                    align="center"
                ),
                
                # Progress bar
                rx.box(
                    rx.box(
                        width=f"{State.upload_progress}%",
                        height="100%",
                        border_radius="inherit",
                        transition="width 0.3s ease",
                        style={
                            "background": rx.cond(
                                State.upload_status == "error",
                                "var(--color-error)",
                                rx.cond(
                                    State.upload_status == "complete",
                                    "var(--color-success)",
                                    "var(--color-primary-500)"
                                )
                            )
                        }
                    ),
                    width="100%",
                    height="8px",
                    border_radius="full",
                    style={"background": "var(--color-bg-tertiary)"}
                ),
                
                spacing="3",
                width="100%"
            ),
            
            padding="1.5rem",
            border_radius="lg",
            border="1px solid",
            margin_bottom="1rem",
            style={
                "background": rx.cond(
                    State.upload_status == "error",
                    "rgba(239, 68, 68, 0.05)",
                    rx.cond(
                        State.upload_status == "complete",
                        "rgba(22, 163, 74, 0.05)",
                        "var(--color-bg-secondary)"
                    )
                ),
                "border_color": rx.cond(
                    State.upload_status == "error",
                    "var(--color-error)",
                    rx.cond(
                        State.upload_status == "complete",
                        "var(--color-success)",
                        "var(--color-border-primary)"
                    )
                )
            }
        ),
        rx.fragment()
    )


def get_upload_status_text() -> str:
    """
    Returns appropriate status text based on upload state.
    
    Returns:
        Status text string
    """
    return rx.cond(
        State.upload_status == "uploading",
        "Uploader fil...",
        rx.cond(
            State.upload_status == "parsing",
            "Parser fil data...",
            rx.cond(
                State.upload_status == "validating",
                "Validerer data...",
                rx.cond(
                    State.upload_status == "complete",
                    "Upload og validering gennemført!",
                    rx.cond(
                        State.upload_status == "error",
                        "Upload fejlede",
                        "Forbereder upload..."
                    )
                )
            )
        )
    )


def upload_validation_summary() -> rx.Component:
    """
    Quick validation summary for upload panel.
    
    Returns:
        rx.Component: Validation summary display
    """
    return rx.cond(
        (State.validation_result != None) & (State.upload_status == "complete"),
        rx.box(
            rx.hstack(
                # Status icon
                rx.icon(
                    rx.cond(
                        State.validation_errors_length == 0,
                        "check-circle",
                        "alert-triangle"
                    ),
                    size=16,
                    style={
                        "color": rx.cond(
                            State.validation_errors_length == 0,
                            "var(--color-success)",
                            "var(--color-warning)"
                        )
                    }
                ),
                
                # Summary text
                rx.text(
                    rx.cond(
                        State.validation_errors_length == 0,
                        f"✓ {State.route_data_length} rækker valideret succesfuldt",
                        f"⚠ {State.validation_errors_length} fejl, {State.validation_warnings_length} advarsler"
                    ),
                    font_weight="medium",
                    font_size="sm",
                    style={
                        "color": rx.cond(
                            State.validation_errors_length == 0,
                            "var(--color-success)",
                            "var(--color-warning)"
                        )
                    }
                ),
                
                rx.spacer(),
                
                # Action button
                rx.cond(
                    State.validation_errors_length > 0,
                    rx.button(
                        "Vis fejl",
                        size="1",
                        variant="outline",
                        color_scheme="red"
                    ),
                    rx.button(
                        "Vis data",
                        size="1",
                        variant="outline",
                        color_scheme="blue",
                        on_click=State.switch_to_routes_tab
                    )
                ),
                
                width="100%",
                align="center"
            ),
            
            padding="1rem",
            border_radius="md",
            margin_top="1rem",
            style={
                "background": rx.cond(
                    State.validation_errors_length == 0,
                    "rgba(22, 163, 74, 0.05)",
                    "rgba(251, 191, 36, 0.05)"
                ),
                "border": rx.cond(
                    State.validation_errors_length == 0,
                    "1px solid var(--color-success)",
                    "1px solid var(--color-warning)"
                )
            }
        ),
        rx.fragment()
    )
