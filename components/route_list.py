"""
Route list komponent for RuteBeregner applikationen.
"""
import reflex as rx
from jord_transport.jord_transport import State
from components.toast import progress_indicator


def route_list_component() -> rx.Component:
    """
    Route list komponent med tabelvisning og CRUD funktionalitet.
    
    Returns:
        rx.Component: Komplet route list tabel med handlinger
    """
    return rx.cond(
        State.route_data_length > 0,
        rx.vstack(
            # Progress indicator (vises kun under bulk beregninger)
            progress_indicator(),
            
            # Tabel container
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Rute #", width="80px"),
                            rx.table.column_header_cell("Start", min_width="200px"),
                            rx.table.column_header_cell("Slut", min_width="200px"),
                            rx.table.column_header_cell("Km", width="100px", text_align="center"),
                            rx.table.column_header_cell("CO₂ Info", width="150px"),
                            rx.table.column_header_cell("Handlinger", width="150px", text_align="center"),
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
                                
                                # Start adresse (inline editable)
                                rx.table.cell(
                                    rx.input(
                                        value=route["start_address"],
                                        on_blur=lambda value: State.update_address(idx, "start_address", value),
                                        placeholder="Startadresse...",
                                        variant="soft",
                                        size="2",
                                        width="100%",
                                    ),
                                ),
                                
                                # Slut adresse (inline editable)
                                rx.table.cell(
                                    rx.input(
                                        value=route["end_address"],
                                        on_blur=lambda value: State.update_address(idx, "end_address", value),
                                        placeholder="Slutadresse...",
                                        variant="soft",
                                        size="2",
                                        width="100%",
                                    ),
                                ),
                                
                                # Distance
                                rx.table.cell(
                                    rx.cond(
                                        route.get("error_status", "") != "",
                                        # Vis fejl badge
                                        rx.vstack(
                                            rx.badge(
                                                "Fejl",
                                                color_scheme="red",
                                                size="2",
                                            ),
                                            rx.tooltip(
                                                rx.icon("info", size=14, color="red.500"),
                                                content=route.get("error_status", ""),
                                            ),
                                            spacing="1",
                                            align="center",
                                        ),
                                        rx.cond(
                                            route.get("distance_label", "") != "",
                                            rx.badge(
                                                route.get("distance_label", ""),
                                                color_scheme="green",
                                                size="2",
                                            ),
                                            rx.text("—", color="gray.8"),
                                        ),
                                    ),
                                    text_align="center",
                                ),
                                
                                # CO₂ info
                                rx.table.cell(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.badge(
                                                rx.cond(
                                                    route["fuel_type"] == "ikke_valgt",
                                                    "Ikke valgt",
                                                    route.get("fuel_type", "N/A")
                                                ),
                                                color_scheme=rx.cond(
                                                    route["fuel_type"] == "ikke_valgt",
                                                    "gray",
                                                    "blue"
                                                ),
                                                size="1",
                                            ),
                                            rx.badge(
                                                rx.cond(
                                                    route["vehicle_class"] == "ikke_valgt",
                                                    "Ikke valgt",
                                                    route.get("vehicle_class", "N/A")
                                                ),
                                                color_scheme=rx.cond(
                                                    route["vehicle_class"] == "ikke_valgt",
                                                    "gray",
                                                    "green"
                                                ),
                                                size="1",
                                            ),
                                            spacing="1",
                                        ),
                                        rx.badge(
                                            f"{route.get('load_mass_kg', 0)} kg",
                                            color_scheme="orange",
                                            size="1",
                                        ),
                                        spacing="1",
                                        align="start",
                                    ),
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
                                            rx.icon("trash", size=14),
                                            on_click=State.delete_route(route["id"]),
                                            size="1",
                                            color_scheme="red",
                                            variant="outline",
                                        ),
                                        spacing="2",
                                        justify="center",
                                    ),
                                    text_align="center",
                                ),
                                
                                _hover={"background": "gray.3"},
                            ),
                        ),
                    ),
                    variant="surface",
                    size="2",
                    width="100%",
                ),
                
                background="gray.2",
                border_radius="lg",
                border="1px solid",
                border_color="gray.6",
                padding="1rem",
                overflow_x="auto",
            ),
            
            # Bulk handlinger footer
            rx.box(
                rx.hstack(
                    # Venstre side - primære handlinger
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
                                "Beregn alle"
                            ),
                            on_click=State.calculate_all_distances,
                            color_scheme="green",
                            size="3",
                            disabled=State.calculation_progress.get("in_progress", False),
                            loading=State.calculation_progress.get("in_progress", False),
                        ),
                        rx.button(
                            rx.icon("trash", size=16),
                            "Slet alle",
                            on_click=State.delete_all_routes,
                            color_scheme="red",
                            variant="outline",
                            size="3",
                        ),
                        spacing="3",
                    ),
                    
                    rx.spacer(),
                    
                    # Højre side - export handlinger
                    rx.hstack(
                        rx.button(
                            rx.icon("download", size=16),
                            "Eksportér",
                            on_click=State.export_results,
                            color_scheme="purple",
                            variant="outline",
                            size="3",
                        ),
                        rx.button(
                            rx.icon("file-text", size=16),
                            "Generér PDF",
                            on_click=State.generate_pdf,
                            color_scheme="orange",
                            variant="outline",
                            size="3",
                        ),
                        spacing="3",
                    ),
                    
                    width="100%",
                    align="center",
                ),
                
                padding="1.5rem",
                background="gray.3",
                border_radius="lg",
                border="1px solid",
                border_color="gray.6",
                margin_top="1rem",
            ),
            
            spacing="4",
            width="100%",
        ),
        
        # Tom tilstand
        rx.box(
            rx.vstack(
                rx.icon("table", size=48, color="gray.8"),
                rx.text("Ingen ruter at vise", color="gray.10", font_style="italic", size="4"),
                rx.text("Tilføj ruter via Manuel tab for at se dem her", color="gray.8", size="2"),
                spacing="3",
                align="center",
            ),
            padding="4rem",
            text_align="center",
            background="gray.3",
            border_radius="lg",
            border="1px dashed",
            border_color="gray.6",
            width="100%",
        ),
    )