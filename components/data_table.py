"""
Advanced data table komponent med filtrering, paginering og multi-select for RuteBeregner.
"""
import reflex as rx
from jord_transport.jord_transport import State
from typing import Dict, Any


def filter_chips() -> rx.Component:
    """Filter chips til hurtig filtrering af data."""
    return rx.hstack(
        rx.text("Filtre:", font_weight="medium", color="gray.700"),
        
        # Missing start address filter
        rx.button(
            rx.cond(
                State.table_filters.get("missing_start", False),
                rx.hstack(
                    rx.icon("x", size=14),
                    "Mangler start",
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("filter", size=14),
                    "Mangler start",
                    spacing="1", 
                    align="center",
                ),
            ),
            on_click=lambda: State.toggle_table_filter("missing_start"),
            size="2",
            color_scheme=rx.cond(
                State.table_filters.get("missing_start", False),
                "red",
                "gray",
            ),
            variant=rx.cond(
                State.table_filters.get("missing_start", False),
                "solid",
                "outline",
            ),
        ),
        
        # Missing end address filter
        rx.button(
            rx.cond(
                State.table_filters.get("missing_end", False),
                rx.hstack(
                    rx.icon("x", size=14),
                    "Mangler slut",
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("filter", size=14),
                    "Mangler slut",
                    spacing="1",
                    align="center",
                ),
            ),
            on_click=lambda: State.toggle_table_filter("missing_end"),
            size="2",
            color_scheme=rx.cond(
                State.table_filters.get("missing_end", False),
                "red",
                "gray",
            ),
            variant=rx.cond(
                State.table_filters.get("missing_end", False),
                "solid",
                "outline",
            ),
        ),
        
        # Missing both addresses filter
        rx.button(
            rx.cond(
                State.table_filters.get("missing_both", False),
                rx.hstack(
                    rx.icon("x", size=14),
                    "Mangler begge",
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("filter", size=14),
                    "Mangler begge",
                    spacing="1",
                    align="center",
                ),
            ),
            on_click=lambda: State.toggle_table_filter("missing_both"),
            size="2",
            color_scheme=rx.cond(
                State.table_filters.get("missing_both", False),
                "red",
                "gray",
            ),
            variant=rx.cond(
                State.table_filters.get("missing_both", False),
                "solid",
                "outline",
            ),
        ),
        
        # Has errors filter
        rx.button(
            rx.cond(
                State.table_filters.get("has_errors", False),
                rx.hstack(
                    rx.icon("x", size=14),
                    "Har fejl",
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("filter", size=14),
                    "Har fejl",
                    spacing="1",
                    align="center",
                ),
            ),
            on_click=lambda: State.toggle_table_filter("has_errors"),
            size="2",
            color_scheme=rx.cond(
                State.table_filters.get("has_errors", False),
                "orange",
                "gray",
            ),
            variant=rx.cond(
                State.table_filters.get("has_errors", False),
                "solid",
                "outline",
            ),
        ),
        
        # Calculated filter
        rx.button(
            rx.cond(
                State.table_filters.get("calculated", False),
                rx.hstack(
                    rx.icon("x", size=14),
                    "Beregnet",
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("filter", size=14),
                    "Beregnet",
                    spacing="1",
                    align="center",
                ),
            ),
            on_click=lambda: State.toggle_table_filter("calculated"),
            size="2",
            color_scheme=rx.cond(
                State.table_filters.get("calculated", False),
                "green",
                "gray",
            ),
            variant=rx.cond(
                State.table_filters.get("calculated", False),
                "solid",
                "outline",
            ),
        ),
        
        spacing="2",
        flex_wrap="wrap",
        align="center",
    )


def search_bar() -> rx.Component:
    """Søgebar til tekstsøgning."""
    return rx.hstack(
        rx.input(
            placeholder="Søg på virksomhed, start- eller slutadresse...",
            value=State.search_text,
            on_change=State.set_search_text,
            size="3",
            width="100%",
        ),
        rx.button(
            rx.icon("search", size=16),
            variant="outline",
            color_scheme="blue",
            size="3",
        ),
        width="100%",
        spacing="2",
    )


def pagination_controls() -> rx.Component:
    """Pagination kontroller."""
    return rx.hstack(
        # Page info
        rx.text(
            f"Side {State.current_page} af {State.get_total_pages()} ({State.filtered_routes_count} ruter)",
            color="gray.600",
            font_size="sm",
        ),
        
        rx.spacer(),
        
        # Navigation buttons
        rx.hstack(
            rx.button(
                rx.icon("chevron-first", size=16),
                on_click=lambda: State.set_current_page(1),
                disabled=State.current_page == 1,
                size="2",
                variant="outline",
            ),
            rx.button(
                rx.icon("chevron-left", size=16),
                on_click=lambda: State.set_current_page(State.current_page - 1),
                disabled=State.current_page == 1,
                size="2",
                variant="outline",
            ),
            rx.button(
                rx.icon("chevron-right", size=16),
                on_click=lambda: State.set_current_page(State.current_page + 1),
                disabled=State.current_page == State.get_total_pages(),
                size="2",
                variant="outline",
            ),
            rx.button(
                rx.icon("chevron-last", size=16),
                on_click=lambda: State.set_current_page(State.get_total_pages()),
                disabled=State.current_page == State.get_total_pages(),
                size="2",
                variant="outline",
            ),
            spacing="1",
        ),
        
        width="100%",
        align="center",
    )


def bulk_actions() -> rx.Component:
    """Bulk handlinger for valgte ruter."""
    return rx.cond(
        State.selected_routes_count > 0,
        rx.box(
            rx.hstack(
                # Selection info
                rx.text(
                    f"{State.selected_routes_count} ruter valgt",
                    font_weight="medium",
                    color="blue.600",
                ),
                
                rx.spacer(),
                
                # Bulk action buttons
                rx.hstack(
                    rx.button(
                        rx.icon("calculator", size=14),
                        "Beregn valgte",
                        on_click=State.calculate_selected_routes,
                        size="2",
                        color_scheme="green",
                    ),
                    rx.button(
                        rx.icon("trash", size=14),
                        "Slet valgte",
                        on_click=State.delete_selected_routes,
                        size="2",
                        color_scheme="red",
                        variant="outline",
                    ),
                    rx.button(
                        rx.icon("x", size=14),
                        "Ryd valg",
                        on_click=State.clear_all_selections,
                        size="2",
                        color_scheme="gray",
                        variant="outline",
                    ),
                    spacing="2",
                ),
                
                width="100%",
                align="center",
            ),
            
            padding="1rem",
            background="blue.50",
            border_radius="lg",
            border="1px solid",
            border_color="blue.200",
            margin_bottom="1rem",
        ),
        rx.fragment(),
    )


def data_table() -> rx.Component:
    """Avanceret data tabel med pagination og multi-select."""
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    # Select all checkbox
                    rx.table.column_header_cell(
                        rx.checkbox(
                            checked=State.all_paginated_routes_selected,
                            on_change=rx.cond(
                                State.all_filtered_routes_selected,
                                State.clear_all_selections,
                                State.select_all_filtered_routes,
                            ),
                        ),
                        width="50px",
                        text_align="center",
                    ),
                    rx.table.column_header_cell("#", width="60px"),
                    rx.table.column_header_cell("Virksomhed", width="200px"),
                    rx.table.column_header_cell("Start", width="250px"),
                    rx.table.column_header_cell("Slut", width="250px"),
                    rx.table.column_header_cell("Afstand", width="100px", text_align="center"),
                    rx.table.column_header_cell("Status", width="100px", text_align="center"),
                    rx.table.column_header_cell("Handlinger", width="120px", text_align="center"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    State.route_data.to(dict),
                    lambda route: rx.table.row(
                        # Selection checkbox
                        rx.table.cell(
                            rx.checkbox(
                                checked=False,  # Temporarily disabled due to ArrayCastedVar limitations
                                # on_change=State.toggle_route_selection(route["id"]),  # Disabled due to ArrayCastedVar issues
                            ),
                            text_align="center",
                            width="50px",
                        ),
                        
                        # Row number (based on pagination)
                        rx.table.cell(
                            rx.badge(
                                route["id"][:8] + "...",
                                color_scheme="gray",
                                size="1",
                            ),
                            text_align="center",
                            width="60px",
                        ),
                        
                        # Company name
                        rx.table.cell(
                            rx.text(
                                route["company_name"],
                                font_size="sm",
                                overflow="hidden",
                                white_space="nowrap",
                                text_overflow="ellipsis",
                            ),
                            width="200px",
                        ),
                        
                        # Start address (editable)
                        rx.table.cell(
                            rx.input(
                                value=route["start_address"],
                                # on_blur=lambda value, route=route: State.update_address(route["id"], "start_address", value),  # Disabled
                                placeholder="Startadresse...",
                                variant="soft",
                                size="2",
                                width="100%",
                            ),
                            width="250px",
                        ),
                        
                        # End address (editable)
                        rx.table.cell(
                            rx.input(
                                value=route["end_address"],
                                # on_blur=lambda value: State.update_address(route["id"], "end_address", value),  # Disabled
                                placeholder="Slutadresse...",
                                variant="soft",
                                size="2",
                                width="100%",
                            ),
                            width="250px",
                        ),
                        
                        # Distance
                        rx.table.cell(
                            rx.cond(
                                route["error_status"] != "",
                                rx.badge("Fejl", color_scheme="red", size="2"),
                                rx.cond(
                                    route["distance_label"] != "",
                                    rx.badge(
                                        route["distance_label"],
                                        color_scheme="green",
                                        size="2",
                                    ),
                                    rx.text("—", color="gray.400"),
                                ),
                            ),
                            text_align="center",
                            width="100px",
                        ),
                        
                        # Status
                        rx.table.cell(
                            rx.cond(
                                route["error_status"] != "",
                                rx.tooltip(
                                    rx.badge("Fejl", color_scheme="red", size="2"),
                                    content=route["error_status"],
                                ),
                                rx.cond(
                                    route["distance_label"] != "",
                                    rx.badge("Klar", color_scheme="green", size="2"),
                                    rx.badge("Venter", color_scheme="gray", size="2"),
                                ),
                            ),
                            text_align="center",
                            width="100px",
                        ),
                        
                        # Actions
                        rx.table.cell(
                            rx.hstack(
                                rx.button(
                                    rx.icon("calculator", size=12),
                                    on_click=State.calculate_single_distance(route["id"]),
                                    size="1",
                                    color_scheme="blue",
                                    variant="outline",
                                ),
                                rx.button(
                                    rx.icon("trash", size=12),
                                    on_click=State.delete_route(route["id"]),
                                    size="1",
                                    color_scheme="red",
                                    variant="outline",
                                ),
                                spacing="1",
                                justify="center",
                            ),
                            text_align="center",
                            width="120px",
                        ),
                        
                        _hover={"background": "gray.50"},
                        background="white",  # Temporarily disabled selection highlighting
                    ),
                ),
            ),
            variant="surface",
            size="2",
            width="100%",
        ),
        
        overflow_x="auto",
        border_radius="lg",
        border="1px solid",
        border_color="gray.200",
        width="100%",
        max_width="100%",
    )


def advanced_data_table() -> rx.Component:
    """Komplet avanceret data tabel med alle features."""
    return rx.vstack(
        # Search bar
        search_bar(),
        
        # Filter chips
        filter_chips(),
        
        # Bulk actions (vis kun når der er valgte ruter)
        bulk_actions(),
        
        # Data table
        data_table(),
        
        # Pagination controls
        pagination_controls(),
        
        spacing="4",
        width="100%",
    )