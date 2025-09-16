"""
Template download component for Jord Transport application.
"""
import reflex as rx
from pathlib import Path


def template_download_panel() -> rx.Component:
    """
    Creates a panel for downloading standardized templates.
    
    Returns:
        rx.Component: Template download panel with Excel and CSV options
    """
    return rx.box(
        rx.vstack(
            # Header
            rx.heading(
                "Download Standardiseret Skabelon",
                size="5",
                margin_bottom="1rem",
                style={"color": "var(--accent-9)"}
            ),
            
            # Description
            rx.text(
                "Brug den officielle skabelon for at sikre korrekt data format og hurtigere behandling.",
                font_size="md",
                margin_bottom="2rem",
                style={"color": "var(--color-text-secondary)"}
            ),
            
            # Template options
            rx.grid(
                # Excel template card
                rx.box(
                    rx.vstack(
                        # Excel icon and title
                        rx.hstack(
                            rx.icon("file-spreadsheet", size=32, style={"color": "var(--color-success)"}),
                            rx.vstack(
                                rx.text("Excel Skabelon", font_weight="bold", font_size="lg"),
                                rx.text("Anbefalet til de fleste brugere", font_size="sm", style={"color": "var(--color-text-tertiary)"}),
                                spacing="0",
                                align="start",
                            ),
                            spacing="3",
                            align="center",
                            width="100%",
                        ),
                        
                        # Features list
                        rx.vstack(
                            rx.text("Funktioner:", font_weight="medium", style={"color": "var(--color-text-secondary)"}),
                            rx.text("✅ Beskyttede headers", font_size="sm"),
                            rx.text("✅ Data validering", font_size="sm"),
                            rx.text("✅ Detaljeret instruktionsark", font_size="sm"),
                            rx.text("✅ Dropdown menuer", font_size="sm"),
                            rx.text("✅ Eksempel data", font_size="sm"),
                            spacing="1",
                            align="start",
                        ),
                        
                        # Download button
                        rx.button(
                            rx.icon("download", size=16),
                            "Download Excel",
                            size="3",
                            color_scheme="green",
                            width="100%",
                            on_click=State.download_excel_template,
                        ),
                        
                        spacing="4",
                        align="start",
                    ),
                    
                    padding="2rem",
                    border_radius="lg",
                    border="1px solid",
                    style={
                        "background": "var(--color-bg-secondary)",
                        "border_color": "var(--color-success)",
                        "box_shadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
                    },
                ),
                
                # CSV template card
                rx.box(
                    rx.vstack(
                        # CSV icon and title
                        rx.hstack(
                            rx.icon("file-text", size=32, style={"color": "var(--color-primary-500)"}),
                            rx.vstack(
                                rx.text("CSV Skabelon", font_weight="bold", font_size="lg"),
                                rx.text("Simpel tekstbaseret format", font_size="sm", style={"color": "var(--color-text-tertiary)"}),
                                spacing="0",
                                align="start",
                            ),
                            spacing="3",
                            align="center",
                            width="100%",
                        ),
                        
                        # Features list
                        rx.vstack(
                            rx.text("Funktioner:", font_weight="medium", style={"color": "var(--color-text-secondary)"}),
                            rx.text("✅ Universelt kompatibel", font_size="sm"),
                            rx.text("✅ Hurtig at redigere", font_size="sm"),
                            rx.text("✅ Lille filstørrelse", font_size="sm"),
                            rx.text("✅ Eksempel data", font_size="sm"),
                            rx.text("⚠️ Ingen indbygget validering", font_size="sm", style={"color": "var(--color-warning)"}),
                            spacing="1",
                            align="start",
                        ),
                        
                        # Download button
                        rx.button(
                            rx.icon("download", size=16),
                            "Download CSV",
                            size="3",
                            color_scheme="blue",
                            variant="outline",
                            width="100%",
                            on_click=State.download_csv_template,
                        ),
                        
                        spacing="4",
                        align="start",
                    ),
                    
                    padding="2rem",
                    border_radius="lg",
                    border="1px solid",
                    style={
                        "background": "var(--color-bg-secondary)",
                        "border_color": "var(--color-primary-500)",
                        "box_shadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
                    },
                ),
                
                columns="1fr 1fr",
                gap="2rem",
                width="100%",
            ),
            
            # Additional information
            rx.box(
                rx.vstack(
                    rx.heading("Vigtige Oplysninger", size="4", style={"color": "var(--accent-9)"}),
                    
                    rx.hstack(
                        rx.icon("info", size=20, style={"color": "var(--color-info)"}),
                        rx.vstack(
                            rx.text("Obligatoriske felter:", font_weight="bold"),
                            rx.text("• Adresse, Postnummer, PostDistrikt (startadresse)"),
                            rx.text("• SlutAdresse ELLER ModtageranlægID (for slutadresse)"),
                            spacing="0",
                            align="start",
                        ),
                        spacing="3",
                        align="start",
                        width="100%",
                    ),
                    
                    rx.hstack(
                        rx.icon("star", size=20, style={"color": "var(--color-warning)"}),
                        rx.vstack(
                            rx.text("Valgfrie felter:", font_weight="bold"),
                            rx.text("• Navn, Dato, KøretøjsType, LastVægt, Brændstoftype"),
                            rx.text("• Disse felter forbedrer nøjagtigheden af beregninger"),
                            spacing="0",
                            align="start",
                        ),
                        spacing="3",
                        align="start",
                        width="100%",
                    ),
                    
                    rx.hstack(
                        rx.icon("map-pin", size=20, style={"color": "var(--color-success)"}),
                        rx.vstack(
                            rx.text("SlutAdresse formater:", font_weight="bold"),
                            rx.text("• Almindelig adresse: 'Rugvænget 18, 8444 Grenå'"),
                            rx.text("• Koordinater: '56.4167,10.7833'"),
                            rx.text("• Modtager anlæg ID: '1061' (slås op automatisk)"),
                            spacing="0",
                            align="start",
                        ),
                        spacing="3",
                        align="start", 
                        width="100%",
                    ),
                    
                    rx.hstack(
                        rx.icon("shield-check", size=20, style={"color": "var(--color-success)"}),
                        rx.vstack(
                            rx.text("Kvalitetssikring:", font_weight="bold"),
                            rx.text("• Skabelonerne sikrer korrekt dataformat"),
                            rx.text("• Automatisk validering ved upload"),
                            rx.text("• Færre fejl og hurtigere behandling"),
                            spacing="0",
                            align="start",
                        ),
                        spacing="3",
                        align="start",
                        width="100%",
                    ),
                    
                    spacing="3",
                ),
                
                padding="2rem",
                border_radius="lg",
                border="1px solid",
                margin_top="2rem",
                style={
                    "background": "var(--color-bg-tertiary)",
                    "border_color": "var(--color-border-primary)",
                },
            ),
            
            spacing="4",
            align="center",
            width="100%",
        ),
        
        width="100%",
        max_width="800px",
        margin="0 auto",
    )


def template_validation_display(is_valid: bool, errors: list, compatibility_report: dict = None) -> rx.Component:
    """
    Displays template validation results.
    
    Args:
        is_valid: Whether the uploaded data is valid
        errors: List of validation errors
        compatibility_report: Optional compatibility analysis
        
    Returns:
        rx.Component: Validation display component
    """
    if is_valid:
        return rx.box(
            rx.hstack(
                rx.icon("check-circle", size=24, style={"color": "var(--color-success)"}),
                rx.vstack(
                    rx.text("Data Valideret!", font_weight="bold", style={"color": "var(--color-success)"}),
                    rx.text("Filen matcher skabelon formatet og er klar til behandling.", font_size="sm"),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
                align="center",
            ),
            padding="1.5rem",
            border_radius="lg",
            border="1px solid",
            style={
                "background": "rgba(22, 163, 74, 0.05)",
                "border_color": "var(--color-success)",
            },
        )
    
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("alert-triangle", size=24, style={"color": "var(--color-error)"}),
                rx.vstack(
                    rx.text("Validering Fejlede", font_weight="bold", style={"color": "var(--color-error)"}),
                    rx.text("Følgende problemer skal rettes:", font_size="sm"),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
                align="start",
            ),
            
            # Error list
            rx.vstack(
                *[
                    rx.text(f"• {error}", font_size="sm", style={"color": "var(--color-text-secondary)"})
                    for error in errors
                ],
                spacing="1",
                align="start",
                margin_left="2rem",
            ),
            
            # Compatibility info if available
            rx.cond(
                compatibility_report is not None,
                rx.box(
                    rx.vstack(
                        rx.text("Kompatibilitets Analyse:", font_weight="medium", font_size="sm"),
                        rx.text(f"Score: {compatibility_report.get('score', 0)*100:.0f}%", font_size="sm"),
                        rx.text(f"Obligatoriske felter: {compatibility_report.get('mandatory_coverage', 0)*100:.0f}%", font_size="sm"),
                        spacing="1",
                        align="start",
                    ),
                    margin_top="1rem",
                    padding="1rem",
                    border_radius="md",
                    style={"background": "var(--color-bg-quaternary)"},
                ),
                rx.fragment(),
            ),
            
            # Help section
            rx.box(
                rx.vstack(
                    rx.text("💡 Hjælp:", font_weight="bold", font_size="sm", style={"color": "var(--color-info)"}),
                    rx.text("1. Download den korrekte skabelon ovenfor", font_size="sm"),
                    rx.text("2. Kopier dine data til skabelonen", font_size="sm"), 
                    rx.text("3. Sørg for at alle obligatoriske felter er udfyldt", font_size="sm"),
                    rx.text("4. Gem og upload filen igen", font_size="sm"),
                    spacing="1",
                    align="start",
                ),
                margin_top="1.5rem",
                padding="1rem",
                border_radius="md",
                style={"background": "rgba(59, 130, 246, 0.05)", "border": "1px solid rgba(59, 130, 246, 0.2)"},
            ),
            
            spacing="3",
            align="start",
        ),
        
        padding="1.5rem",
        border_radius="lg",
        border="1px solid",
        style={
            "background": "rgba(239, 68, 68, 0.05)",
            "border_color": "var(--color-error)",
        },
    )