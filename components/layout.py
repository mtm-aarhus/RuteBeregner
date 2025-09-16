"""
Layout komponent for RuteBeregner applikationen.
"""
import reflex as rx
from typing import Any

# Import State from the main app
from jord_transport.jord_transport import State
from components.manual_input import manual_input_component
from components.route_list import route_list_component
from components.toast import toast_notification
from components.upload_panel import upload_panel
from components.address_list import address_list_component
from components.theme_provider import with_theme
from components.color_mode_toggle import compact_color_mode_toggle


def manual_tab_content() -> rx.Component:
    """Indhold for Manuel tab."""
    return rx.vstack(
        # Beskrivelse
        rx.center(
            rx.heading("Manuel indtastning", size="5", style={"color": "var(--accent-9)"}, margin_bottom="1rem"),
        ),
        
        # Manuel input komponent
        manual_input_component(),
        
        # Smart rute visning - vis tilføjede ruter
        rx.cond(
            State.route_data_length > 0,
            rx.center(
                rx.vstack(
                    # Header med antal ruter
                    rx.hstack(
                        rx.icon("route", size=20, style={"color": "var(--accent-9)"}),
                        rx.heading(
                            f"Tilføjede Ruter ({State.route_data_length})", 
                            size="4", 
                            style={"color": "var(--accent-9)"}
                        ),
                        spacing="2",
                        align="center",
                        justify="center",
                    ),
                    
                    # Elegant tabel visning af ruter - centreret
                    rx.center(
                        rx.box(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("#", width="50px", text_align="center"),
                                    rx.table.column_header_cell("Fra", min_width="200px"),
                                    rx.table.column_header_cell("Til", min_width="200px"),
                                    rx.table.column_header_cell("Status", width="120px", text_align="center"),
                                    rx.table.column_header_cell("Handlinger", width="100px", text_align="center"),
                                ),
                            ),
                            rx.table.body(
                                rx.foreach(
                                    State.route_data,
                                    lambda route, idx: rx.table.row(
                                        # Rute nummer
                                        rx.table.cell(
                                            rx.badge(
                                                f"{idx + 1}",
                                                color_scheme="blue",
                                                size="2",
                                            ),
                                            text_align="center",
                                        ),
                                        
                                        # Fra adresse
                                        rx.table.cell(
                                            rx.text(
                                                route.get('start_address', 'Ikke angivet'),
                                                font_size="sm",
                                                font_weight="medium",
                                                overflow="hidden",
                                                white_space="nowrap",
                                                text_overflow="ellipsis",
                                            ),
                                        ),
                                        
                                        # Til adresse  
                                        rx.table.cell(
                                            rx.text(
                                                route.get('end_address', 'Ikke angivet'),
                                                font_size="sm",
                                                overflow="hidden",
                                                white_space="nowrap",
                                                text_overflow="ellipsis",
                                            ),
                                        ),
                                        
                                        # Status
                                        rx.table.cell(
                                            rx.cond(
                                                route.get("distance_label", "") != "",
                                                rx.badge(
                                                    route.get("distance_label", ""),
                                                    color_scheme="green",
                                                    size="2",
                                                ),
                                                rx.badge(
                                                    "Ikke beregnet",
                                                    color_scheme="gray",
                                                    size="2",
                                                ),
                                            ),
                                            text_align="center",
                                        ),
                                        
                                        # Handlinger
                                        rx.table.cell(
                                            rx.hstack(
                                                rx.button(
                                                    rx.icon("calculator", size=14),
                                                    on_click=State.calculate_single_distance(route["id"]),
                                                    size="1",
                                                    color_scheme="blue",
                                                    variant="outline",
                                                ),
                                                rx.button(
                                                    rx.icon("trash-2", size=14),
                                                    on_click=State.delete_route(route["id"]),
                                                    size="1",
                                                    color_scheme="red",
                                                    variant="outline",
                                                ),
                                                spacing="1",
                                                justify="center",
                                            ),
                                            text_align="center",
                                        ),
                                        
                                        _hover={"background": "var(--color-bg-tertiary)"},
                                    ),
                                ),
                            ),
                            variant="surface",
                            size="2",
                            width="100%",
                        ),
                        
                        max_height="300px",
                        overflow_y="auto",
                        border_radius="lg",
                        border="1px solid",
                        style={
                            "border_color": "var(--color-border-primary)",
                        },
                        max_width="900px",
                    ),
                    width="100%",
                ),
                    
                    # Batch handlinger - centreret
                    rx.center(
                        rx.hstack(
                        rx.button(
                            rx.cond(
                                State.calculation_progress.get("in_progress", False),
                                rx.icon("loader", size=16),
                                rx.icon("calculator", size=16),
                            ),
                            rx.cond(
                                State.calculation_progress.get("in_progress", False),
                                f"Beregner... ({State.calculation_progress.get('current', 0)}/{State.calculation_progress.get('total', 0)})",
                                "Beregn alle afstande"
                            ),
                            on_click=State.calculate_all_distances,
                            color_scheme="green",
                            size="3",
                            disabled=State.calculation_progress.get("in_progress", False),
                            loading=State.calculation_progress.get("in_progress", False),
                        ),
                        rx.button(
                            rx.icon("trash", size=16),
                            "Ryd alle",
                            on_click=State.clear_all_routes,
                            color_scheme="red",
                            variant="outline",
                            size="3",
                        ),
                        rx.button(
                            rx.icon("arrow-right", size=16),
                            "Gå til Ruteliste",
                            on_click=State.switch_to_routes_tab,
                            color_scheme="blue",
                            variant="outline",
                            size="3",
                        ),
                            spacing="2",
                            justify="center",
                            flex_wrap="wrap",
                        ),
                        width="100%",
                    ),
                    
                    spacing="4",
                    width="100%",
                    max_width="800px",
                    padding="1.5rem",
                    border_radius="lg",
                    border="1px solid",
                    style={
                        "background": "var(--color-bg-tertiary)",
                        "border_color": "var(--color-border-primary)",
                    },
                ),
                width="100%",
            ),
            # Empty state when no routes
            rx.center(
                rx.box(
                    rx.vstack(
                        rx.icon("route", size=48, style={"color": "var(--color-text-muted)"}),
                        rx.text("Ingen ruter tilføjet endnu", style={"color": "var(--color-text-tertiary)"}, font_style="italic"),
                        rx.text("Brug formularen ovenfor for at tilføje din første rute", style={"color": "var(--color-text-muted)"}, size="2"),
                        spacing="2",
                        align="center",
                    ),
                    padding="3rem",
                    text_align="center",
                    border_radius="lg",
                    border="1px dashed",
                    style={
                        "background": "var(--color-bg-tertiary)",
                        "border_color": "var(--color-border-primary)",
                    },
                    max_width="800px",
                ),
                width="100%",
            ),
        ),
        
        spacing="6",
        width="100%",
    )


def route_list_tab_content() -> rx.Component:
    """Indhold for Ruteliste tab med avancerede data funktionaliteter."""
    return rx.vstack(
        # Header
        rx.center(
            rx.heading("Ruteliste", size="5", style={"color": "var(--accent-9)"}, margin_bottom="1rem"),
        ),
        
        # Empty state when no data
        rx.cond(
            State.route_data_length == 0,
            rx.center(
                rx.box(
                    rx.vstack(
                        rx.icon("inbox", size=48, style={"color": "var(--color-text-muted)"}),
                        rx.text(
                            "Ingen data uploadet endnu",
                            font_weight="medium",
                            style={"color": "var(--color-text-muted)"}
                        ),
                        rx.text(
                            "Gå til Upload-fanen for at uploade dine rutedata",
                            style={"color": "var(--color-text-muted)"}
                        ),
                        rx.button(
                            rx.icon("upload", size=16),
                            "Gå til Upload",
                            on_click=State.switch_to_upload_tab,
                            color_scheme="blue",
                            variant="outline",
                            size="2",
                            margin_top="1rem"
                        ),
                        spacing="3",
                        align="center",
                        text_align="center"
                    ),
                    padding="3rem",
                    border_radius="lg",
                    border="1px dashed",
                    max_width="600px",
                    style={
                        "border_color": "var(--color-border-primary)",
                    },
                ),
                width="100%",
            ),
            rx.fragment(),
        ),
        
        # Route list with data table functionality (vis kun når der er data)
        rx.cond(
            State.route_data_length > 0,
            route_list_component(),
            rx.fragment(),
        ),
        
        spacing="4",
        width="100%",
    )


def upload_tab_content() -> rx.Component:
    """Indhold for Upload & batch tab."""
    return rx.vstack(
        # Header
        rx.center(
            rx.heading("Upload", size="5", style={"color": "var(--accent-9)"}, margin_bottom="1rem"),
        ),
        
        # Enhanced upload panel
        upload_panel(),
        
        spacing="4",
        width="100%",
    )


def address_list_tab_content() -> rx.Component:
    """Indhold for Adresseliste tab."""
    return rx.vstack(
        # Auto-load addresses when tab is opened
        rx.script("window.addEventListener('load', () => { /* Load addresses */ });"),
        
        # Address list komponent
        address_list_component(),
        
        spacing="4",
        width="100%",
    )


def header_component() -> rx.Component:
    """
    Header komponent med logo, titel og color mode toggle.
    
    Returns:
        rx.Component: Header med responsive design og theme support
    """
    return rx.box(
        # Header container
        rx.flex(
            # Logo sektion
            rx.link(
                rx.image(
                    src="/AAK_TM_venstre_neg.png",  # Negativ version - hvidt logo til mørk baggrund
                    alt="Teknik og Miljø Logo",
                    height=["60px", "70px", "80px"],
                    width="auto",
                    object_fit="contain",
                ),
                href="/",  # Link til homepage
                aria_label="Hjem",
                flex_shrink="0",
            ),
            
            # Titel sektion (centreret)
            rx.flex(
                rx.heading(
                    "Teknik og Miljø – beregning af kørte afstande",
                    size="5",  # Fast størrelse i stedet for responsive array
                    font_weight="bold",
                    text_align="center",
                    line_height="1.2",
                    style={
                        "color": "#ffffff",  # Hvid tekst
                        "fontSize": ["26px", "28px", "30px"],  # Responsive font size via CSS
                    },
                    display=["none", "block", "block"],  # Skjul på meget små skærme
                ),
                flex="1",
                justify="center",
                align="center",
            ),
            
            # Right side navigation elements
            rx.flex(
                # Color mode toggle
                rx.box(
                    compact_color_mode_toggle(),
                    flex_shrink="0",
                ),
                
                align="center",
                gap="1rem",
            ),
            
            align="center",
            justify="between",
            width="100%",
            min_height="60px",  # Ensured minimum height
        ),
        
        # Header styling med theme variables
        position="fixed",  # Fixed position for better UX
        top="0",
        left="0",
        right="0",
        z_index="1000",  # Higher z-index
        padding_x=["1.5rem", "3rem", "6rem"],
        padding_y="0.75rem",
        border_bottom="1px solid var(--color-border-primary)",
        backdrop_filter="blur(12px)",
        box_shadow="0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
        # Theme-aware styling with data attribute for CSS targeting
        style={
            "transition": "var(--transition-colors)",
            "background": "#1e293b",  # Dark header background
            "color": "#ffffff",  # White text for contrast
        },
        # Data attribute for CSS targeting
        data_jt_header="true",
        # Accessibility
        role="banner",
        aria_label="Hovednavigation",
    )


def layout() -> rx.Component:
    """
    Hovedlayout for applikationen med centreret titel og tab-navigation.
        
    Returns:
        rx.Component: Komplet layout struktur med tabs
    """
    return with_theme(
        rx.container(
        rx.vstack(
            # Initialize color mode on page load
            rx.script("""
                // Ensure color mode is initialized when page loads
                document.addEventListener('DOMContentLoaded', function() {
                    if (window.colorModeUtils) {
                        console.log('Page loaded - current color mode:', window.colorModeUtils.getCurrentMode());
                    }
                });
            """),
            
            # Header komponent
            header_component(),
            
            # Tab system
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger(
                        "Manuel",
                        value="manual",
                        font_weight="medium",
                        style={"color": "var(--accent-9)"},
                    ),
                    rx.tabs.trigger(
                        "Ruteliste",
                        value="routes",
                        font_weight="medium",
                        style={"color": "var(--accent-9)"},
                    ),
                    rx.tabs.trigger(
                        "Upload",
                        value="upload", 
                        font_weight="medium",
                        style={"color": "var(--accent-9)"},
                    ),
                    rx.tabs.trigger(
                        "Adresseliste",
                        value="addresses",
                        font_weight="medium", 
                        style={"color": "var(--accent-9)"},
                    ),
                    border_radius="lg",
                    border="1px solid",
                    style={
                        "background": "var(--color-bg-secondary)",
                        "border_color": "var(--color-primary-600)",
                    },
                    padding="0.5rem",
                    margin_bottom="1rem",
                    margin_top="1rem",  # Extra spacing from header
                    justify="center",
                ),
                
                rx.tabs.content(
                    rx.box(
                        manual_tab_content(),
                        padding="2rem",
                        border_radius="lg",
                        box_shadow="lg",
                        border="1px solid",
                        style={
                            "background": "var(--color-bg-secondary)",
                            "border_color": "var(--color-border-primary)",
                        },
                    ),
                    value="manual",
                ),
                
                rx.tabs.content(
                    rx.box(
                        route_list_tab_content(),
                        padding="2rem",
                        border_radius="lg",
                        box_shadow="lg",
                        border="1px solid",
                        style={
                            "background": "var(--color-bg-secondary)",
                            "border_color": "var(--color-border-primary)",
                        },
                    ),
                    value="routes",
                ),
                
                rx.tabs.content(
                    rx.box(
                        upload_tab_content(),
                        padding="2rem",
                        border_radius="lg",
                        box_shadow="lg",
                        border="1px solid",
                        style={
                            "background": "var(--color-bg-secondary)",
                            "border_color": "var(--color-border-primary)",
                        },
                    ),
                    value="upload",
                ),
                
                rx.tabs.content(
                    rx.box(
                        address_list_tab_content(),
                        padding="2rem",
                        border_radius="lg",
                        box_shadow="lg",
                        border="1px solid",
                        style={
                            "background": "var(--color-bg-secondary)",
                            "border_color": "var(--color-border-primary)",
                        },
                    ),
                    value="addresses",
                ),
                
                value=State.current_tab,
                on_change=State.set_current_tab,
                width="100%",
            ),
            
            # Footer
            rx.center(
                rx.text(
                    "© 2025 Teknik og Miljø",
                    size="2",
                    style={"color": "var(--color-text-tertiary)"},
                    margin_top="2rem",
                ),
                width="100%",
            ),
            
            # Toast notification (global)
            toast_notification(),
            
            spacing="6",
            width="100%",
            min_height="100vh",
            padding_y="2rem",
            padding_top=["4rem", "5rem", "6rem"],  # Reduced top padding since title is in header
        ),
        
        # Container styling for responsive design inspired by ChatGPT
        max_width="1200px",
        margin_x="auto",
        padding_x=["1.5rem", "3rem", "6rem"],  # Large responsive margins
        min_height="100vh",
        style={
            "background": "var(--color-bg-primary)",
            "color": "var(--color-text-primary)",
        }
        )
    )