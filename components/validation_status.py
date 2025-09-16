"""
Validation status component that displays validation results to users.

Shows errors, warnings, and validation summary in an organized way.
"""
import reflex as rx
from jord_transport.jord_transport import State


def validation_error_item(error: dict) -> rx.Component:
    """
    Individual validation error item display.
    
    Args:
        error: Error dictionary from validation result
        
    Returns:
        rx.Component: Formatted error display
    """
    return rx.box(
        rx.hstack(
            # Error icon
            rx.icon(
                "circle_x", 
                size=16, 
                style={"color": "var(--color-error)", "flex_shrink": "0"}
            ),
            
            # Error content
            rx.vstack(
                # Main error message
                rx.text(
                    error["message"],
                    font_weight="medium",
                    style={"color": "var(--color-error)"}
                ),
                
                # Additional details if available
                rx.cond(
                    error["row_number"] != None,
                    rx.text(
                        f"Række {error['row_number']}, felt '{error["field"]}'",
                        font_size="sm",
                        style={"color": "var(--color-text-muted)"}
                    ),
                    rx.text(
                        f"Felt: {error["field"]}",
                        font_size="sm", 
                        style={"color": "var(--color-text-muted)"}
                    )
                ),
                
                # Show problematic value if available
                rx.cond(
                    error["value"] != None,
                    rx.box(
                        rx.text(
                            f"Værdi: '{error["value"]}'",
                            font_family="monospace",
                            font_size="sm",
                            padding="0.25rem 0.5rem",
                            border_radius="md",
                            style={
                                "background": "var(--color-bg-tertiary)",
                                "color": "var(--color-text-secondary)"
                            }
                        ),
                        margin_top="0.25rem"
                    ),
                    rx.fragment()
                ),
                
                spacing="1",
                align="start",
                flex="1"
            ),
            
            width="100%",
            align="start",
            spacing="3"
        ),
        
        padding="1rem",
        border_radius="lg", 
        border="1px solid",
        style={
            "background": "rgba(239, 68, 68, 0.05)",
            "border_color": "var(--color-error)"
        },
        margin_bottom="0.5rem"
    )


def validation_warning_item(warning: dict) -> rx.Component:
    """
    Individual validation warning item display.
    
    Args:
        warning: Warning dictionary from validation result
        
    Returns:
        rx.Component: Formatted warning display
    """
    return rx.box(
        rx.hstack(
            # Warning icon
            rx.icon(
                "triangle_alert", 
                size=16, 
                style={"color": "var(--color-warning)", "flex_shrink": "0"}
            ),
            
            # Warning content
            rx.vstack(
                # Main warning message
                rx.text(
                    warning["message"],
                    font_weight="medium",
                    style={"color": "var(--color-warning)"}
                ),
                
                # Additional details
                rx.cond(
                    warning["row_number"] != None,
                    rx.text(
                        f"Række {warning['row_number']}, felt '{warning["field"]}'",
                        font_size="sm",
                        style={"color": "var(--color-text-muted)"}
                    ),
                    rx.text(
                        f"Felt: {warning["field"]}",
                        font_size="sm",
                        style={"color": "var(--color-text-muted)"}
                    )
                ),
                
                # Show suggestion if available
                rx.cond(
                    warning.get("suggestion") != None,
                    rx.text(
                        f"💡 {warning["suggestion"]}",
                        font_size="sm",
                        font_style="italic",
                        style={"color": "var(--color-text-secondary)"}
                    ),
                    rx.fragment()
                ),
                
                # Show problematic value if available
                rx.cond(
                    warning["value"] != None,
                    rx.box(
                        rx.text(
                            f"Værdi: '{warning['value']}'",
                            font_family="monospace",
                            font_size="sm",
                            padding="0.25rem 0.5rem",
                            border_radius="md",
                            style={
                                "background": "var(--color-bg-tertiary)",
                                "color": "var(--color-text-secondary)"
                            }
                        ),
                        margin_top="0.25rem"
                    ),
                    rx.fragment()
                ),
                
                spacing="1",
                align="start",
                flex="1"
            ),
            
            width="100%",
            align="start",
            spacing="3"
        ),
        
        padding="1rem",
        border_radius="lg",
        border="1px solid", 
        style={
            "background": "rgba(251, 191, 36, 0.05)",
            "border_color": "var(--color-warning)"
        },
        margin_bottom="0.5rem"
    )


def validation_summary() -> rx.Component:
    """
    Validation summary display with overview statistics.
    
    Returns:
        rx.Component: Summary of validation results
    """
    return rx.cond(
        State.validation_result != None,
        rx.box(
            rx.vstack(
                # Title
                rx.heading(
                    "Validering Status",
                    size="4",
                    style={"color": "var(--accent-9)"},
                    margin_bottom="1rem"
                ),
                
                # Overall status indicator
                rx.hstack(
                    rx.cond(
                        (State.validation_errors_length == 0),
                        # Success state
                        rx.hstack(
                            rx.icon("circle_check", size=20, style={"color": "var(--color-success)"}),
                            rx.text(
                                "Validering gennemført",
                                font_weight="bold",
                                style={"color": "var(--color-success)"}
                            ),
                            spacing="2"
                        ),
                        # Error state
                        rx.hstack(
                            rx.icon("circle_x", size=20, style={"color": "var(--color-error)"}),
                            rx.text(
                                "Validering fejlede",
                                font_weight="bold",
                                style={"color": "var(--color-error)"}
                            ),
                            spacing="2"
                        )
                    ),
                    
                    rx.spacer(),
                    
                    # Timestamp
                    rx.text(
                        f"Sidst valideret: {State.last_validation_timestamp}",
                        font_size="sm",
                        style={"color": "var(--color-text-muted)"}
                    ),
                    
                    width="100%",
                    align="center"
                ),
                
                # Statistics badges
                rx.hstack(
                    # Error count
                    rx.badge(
                        rx.hstack(
                            rx.icon("circle_x", size=12),
                            rx.text(f"{State.validation_errors_length} fejl"),
                            spacing="1"
                        ),
                        color_scheme=rx.cond(
                            State.validation_errors_length > 0,
                            "red",
                            "gray"
                        ),
                        size="2"
                    ),
                    
                    # Warning count
                    rx.badge(
                        rx.hstack(
                            rx.icon("triangle_alert", size=12),
                            rx.text(f"{State.validation_warnings_length} advarsler"),
                            spacing="1"
                        ),
                        color_scheme=rx.cond(
                            State.validation_warnings_length > 0,
                            "yellow",
                            "gray"
                        ),
                        size="2"
                    ),
                    
                    # Processing indicator
                    rx.cond(
                        State.validation_in_progress,
                        rx.badge(
                            rx.hstack(
                                rx.icon("loader", size=12, class_name="animate-spin"),
                                rx.text("Validerer..."),
                                spacing="1"
                            ),
                            color_scheme="blue",
                            size="2"
                        ),
                        rx.fragment()
                    ),
                    
                    spacing="2",
                    justify="center",
                    width="100%"
                ),
                
                spacing="3",
                align="start",
                width="100%"
            ),
            
            padding="1.5rem",
            border_radius="lg",
            border="1px solid",
            style={
                "background": "var(--color-bg-secondary)",
                "border_color": "var(--color-border-primary)"
            },
            margin_bottom="1rem"
        ),
        rx.fragment()
    )


def validation_errors_section() -> rx.Component:
    """
    Section displaying all validation errors.
    
    Returns:
        rx.Component: Collapsible section with error details
    """
    return rx.cond(
        State.validation_errors_length > 0,
        rx.box(
            rx.vstack(
                # Section header
                rx.hstack(
                    rx.icon("circle_x", size=20, style={"color": "var(--color-error)"}),
                    rx.heading(
                        f"Valideringsfejl ({State.validation_errors_length})",
                        size="3",
                        style={"color": "var(--color-error)"}
                    ),
                    spacing="2",
                    align="center",
                    margin_bottom="1rem"
                ),
                
                # Error list
                rx.box(
                    rx.foreach(
                        State.validation_errors,
                        validation_error_item
                    ),
                    width="100%"
                ),
                
                # Help text
                rx.box(
                    rx.text(
                        "💡 Ret fejlene ovenfor og upload filen igen for at fortsætte.",
                        font_size="sm",
                        font_style="italic",
                        padding="1rem",
                        border_radius="md",
                        style={
                            "background": "var(--color-bg-tertiary)",
                            "color": "var(--color-text-secondary)"
                        }
                    ),
                    margin_top="1rem"
                ),
                
                spacing="2",
                align="start",
                width="100%"
            ),
            
            padding="1.5rem",
            border_radius="lg",
            border="1px solid",
            style={
                "background": "rgba(239, 68, 68, 0.02)",
                "border_color": "var(--color-error)"
            },
            margin_bottom="1rem"
        ),
        rx.fragment()
    )


def validation_warnings_section() -> rx.Component:
    """
    Section displaying all validation warnings.
    
    Returns:
        rx.Component: Collapsible section with warning details
    """
    return rx.cond(
        State.validation_warnings_length > 0,
        rx.box(
            rx.vstack(
                # Section header
                rx.hstack(
                    rx.icon("triangle_alert", size=20, style={"color": "var(--color-warning)"}),
                    rx.heading(
                        f"Advarsler ({State.validation_warnings_length})",
                        size="3",
                        style={"color": "var(--color-warning)"}
                    ),
                    spacing="2",
                    align="center",
                    margin_bottom="1rem"
                ),
                
                # Warning list
                rx.box(
                    rx.foreach(
                        State.validation_warnings,
                        validation_warning_item
                    ),
                    width="100%"
                ),
                
                # Help text
                rx.box(
                    rx.text(
                        "ℹ️ Advarsler forhindrer ikke behandling, men kan påvirke beregningsresultater.",
                        font_size="sm",
                        font_style="italic",
                        padding="1rem",
                        border_radius="md",
                        style={
                            "background": "var(--color-bg-tertiary)",
                            "color": "var(--color-text-secondary)"
                        }
                    ),
                    margin_top="1rem"
                ),
                
                spacing="2",
                align="start",
                width="100%"
            ),
            
            padding="1.5rem",
            border_radius="lg",
            border="1px solid",
            style={
                "background": "rgba(251, 191, 36, 0.02)",
                "border_color": "var(--color-warning)"
            },
            margin_bottom="1rem"
        ),
        rx.fragment()
    )


def validation_status_panel() -> rx.Component:
    """
    Complete validation status panel with summary, errors and warnings.
    
    Returns:
        rx.Component: Full validation status display
    """
    return rx.cond(
        # Only show if validation has been performed
        (State.validation_result != None) | (State.validation_in_progress == True),
        rx.box(
            rx.vstack(
                # Summary section
                validation_summary(),
                
                # Errors section 
                validation_errors_section(),
                
                # Warnings section
                validation_warnings_section(),
                
                spacing="3",
                width="100%"
            ),
            
            width="100%",
            margin_bottom="2rem"
        ),
        rx.fragment()
    )