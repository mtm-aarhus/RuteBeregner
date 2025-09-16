"""
Enhanced upload panel komponent for RuteBeregner applikationen.
Includes template downloads, drag-and-drop with live validation, progress bars,
and detailed error reporting.
"""
import reflex as rx
from jord_transport.jord_transport import State
from components.data_table import advanced_data_table
from components.validation_status import validation_status_panel
from components.upload_progress import upload_progress_bar, upload_validation_summary
from components.template_download import template_download_panel


def enhanced_drag_drop_zone() -> rx.Component:
    """
    Enhanced drag-and-drop zone med korrekt Reflex 0.3.0+ upload API.
    
    Returns:
        rx.Component: Interactive drag-and-drop upload zone
    """
    return rx.vstack(
        rx.upload(
            rx.vstack(
                # Dynamic upload icon based on state
                rx.cond(
                    State.upload_in_progress,
                    rx.icon("check", size=48, style={"color": "var(--color-success)"}),
                    rx.icon("upload", size=48, style={"color": "var(--color-primary-500)"}),
                ),
                
                # Dynamic upload text based on state
                rx.cond(
                    State.upload_in_progress,
                    rx.vstack(
                        rx.text(
                            "📤 Fil uploadet!",
                            font_weight="bold",
                            font_size="lg",
                            style={"color": "var(--color-success)"}
                        ),
                        rx.text(
                            "Behandler og validerer filen...",
                            font_size="sm",
                            style={"color": "var(--color-success)"}
                        ),
                        spacing="1",
                        align="center",
                    ),
                    rx.vstack(
                        rx.text(
                            "Træk filer hertil eller klik for at browse",
                            font_weight="bold",
                            font_size="lg",
                            style={"color": "var(--accent-9)"}
                        ),
                        rx.text(
                            "Understøtter .csv, .xlsx og .xls filer (max 10MB)",
                            font_size="sm",
                            style={"color": "var(--color-text-muted)"}
                        ),
                        spacing="1",
                        align="center",
                    )
                ),
                
                spacing="3",
                align="center",
                text_align="center",
                padding="2rem",
                border="2px dashed",
                border_radius="xl",
                width="100%",
                min_height="200px",
                justify="center",
                style={
                    "border_color": rx.cond(
                        State.upload_in_progress,
                        "var(--color-success)",
                        "var(--color-border-primary)"
                    ),
                    "background": rx.cond(
                        State.upload_in_progress,
                        "rgba(22, 163, 74, 0.05)",
                        "var(--color-bg-tertiary)"
                    ),
                }
            ),
            id="upload",
            multiple=False,
            accept={
                "text/csv": [".csv"],
                "application/vnd.openxmlformats-officedocument.spreadsheetML.sheet": [".xlsx"],
                "application/vnd.ms-excel": [".xls"]
            },
            max_files=1,
            max_size=10 * 1024 * 1024,  # 10MB
            width="100%",
        ),
        
        # Show selected file name before processing
        rx.cond(
            rx.selected_files("upload").length() > 0,
            rx.center(
                rx.box(
                    rx.hstack(
                        rx.icon("file", size=16, style={"color": "var(--color-primary-500)"}),
                        rx.text(
                            "Valgt fil: ",
                            font_weight="medium",
                            style={"color": "var(--color-text-primary)"}
                        ),
                        rx.text(
                            rx.selected_files("upload")[0],
                            font_weight="bold",
                            style={"color": "var(--accent-9)"}
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.icon("x", size=14),
                            on_click=rx.clear_selected_files("upload"),
                            size="1",
                            color_scheme="gray",
                            variant="ghost",
                        ),
                        spacing="2",
                        align="center",
                        width="100%",
                    ),
                    padding="0.75rem 1rem",
                    border_radius="md",
                    style={
                        "background": "rgba(59, 130, 246, 0.05)",
                        "border": "1px solid rgba(59, 130, 246, 0.2)"
                    },
                ),
                width="100%",
            ),
            rx.fragment(),
        ),
        
        # Process uploaded files button - aktiveres når filer er valgt
        rx.button(
            rx.cond(
                State.upload_in_progress,
                "Behandler fil...",
                "Behandl uploadede filer"
            ),
            on_click=lambda: State.handle_file_upload(rx.upload_files("upload")),
            color_scheme="blue",
            size="3",
            width="100%",
            margin_top="1rem",
            disabled=State.upload_in_progress,
            loading=State.upload_in_progress,
        ),
        
        spacing="3",
        width="100%",
    )


def template_download_section() -> rx.Component:
    """
    Template download section with quick download buttons.
    
    Returns:
        rx.Component: Template download buttons section
    """
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("download", size=20, style={"color": "var(--color-primary-500)"}),
                rx.text(
                    "Download Skabelon",
                    font_weight="bold",
                    font_size="lg",
                    style={"color": "var(--accent-9)"}
                ),
                spacing="2",
                align="center"
            ),
            
            rx.text(
                "Start med den korrekte skabelon for hurtigere behandling og færre fejl",
                font_size="sm",
                text_align="center",
                style={"color": "var(--color-text-secondary)"}
            ),
            
            rx.hstack(
                rx.button(
                    rx.icon("file-spreadsheet", size=16),
                    "Excel Skabelon",
                    size="2",
                    color_scheme="green",
                    on_click=State.download_excel_template
                ),
                rx.button(
                    rx.icon("file-text", size=16),
                    "CSV Skabelon",
                    size="2",
                    color_scheme="blue",
                    variant="outline",
                    on_click=State.download_csv_template
                ),
                spacing="3",
                justify="center",
                flex_wrap="wrap"
            ),
            
            spacing="3",
            align="center",
            width="100%"
        ),
        
        padding="1.5rem",
        border_radius="lg",
        border="1px solid",
        style={
            "background": "var(--color-bg-secondary)",
            "border_color": "var(--color-border-primary)"
        }
    )


def upload_panel() -> rx.Component:
    """
    Enhanced file upload panel with template downloads, drag-and-drop zone, 
    progress tracking, and comprehensive validation feedback.
    
    Returns:
        rx.Component: Complete enhanced upload panel
    """
    return rx.vstack(
        # Template download section
        template_download_section(),
        
        # Upload progress bar (shows during upload/validation)
        upload_progress_bar(),
        
        # Always show upload zone (file uploaded state handled by toast notifications)
        enhanced_drag_drop_zone(),
        
        # Validation status panel (shows after validation) - midlertidigt deaktiveret
        # validation_status_panel(),
        rx.text("Validering midlertidigt ikke tilgængelig", color="gray", margin_y="1rem"),
        
        # Optional: Show data info when loaded (but allow new uploads)
        rx.cond(
            State.route_data_length > 0,
            rx.center(
                rx.box(
                    rx.hstack(
                        rx.icon("database", size=20, style={"color": "var(--accent-9)"}),
                        rx.vstack(
                            rx.text(
                                f"📊 {State.route_data_length} ruter indlæst",
                                font_weight="medium",
                                style={"color": "var(--accent-9)"}
                            ),
                            rx.text(
                                "Du kan uploade en ny fil eller gå til Ruteliste",
                                font_size="sm",
                                style={"color": "var(--color-text-secondary)"}
                            ),
                            spacing="0",
                            align="start"
                        ),
                        rx.button(
                            rx.icon("arrow-right", size=14),
                            "Gå til Ruteliste",
                            on_click=State.switch_to_routes_tab,
                            size="2",
                            color_scheme="blue",
                            variant="outline",
                        ),
                        spacing="3",
                        align="center",
                        width="100%",
                        justify="between",
                    ),
                    padding="1.5rem",
                    border_radius="md",
                    max_width="600px",
                    style={
                        "background": "rgba(59, 130, 246, 0.05)",
                        "border": "1px solid rgba(59, 130, 246, 0.2)"
                    },
                ),
                width="100%",
            ),
            rx.fragment(),
        ),
        
        spacing="4",
        width="100%",
        align="center",
    )