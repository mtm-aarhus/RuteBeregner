"""
Address List komponent for CRUD operationer på modtager adresser
"""
import reflex as rx
from typing import Any


def address_form_component() -> rx.Component:
    """
    Formular til tilføjelse/redigering af adresser.
    """
    # Import State fra hovedapplikationen
    from jord_transport.jord_transport import State
    
    return rx.vstack(
        rx.heading(
            rx.cond(
                State.is_editing_address,
                "Rediger Adresse",
                "Tilføj Ny Adresse"
            ),
            size="4",
            color="var(--accent-9)",
            margin_bottom="1rem"
        ),
        
        # Form fields i et responsive grid
        rx.form(
            rx.vstack(
                # Anlæg ID (required)
                rx.vstack(
                    rx.text("Modtager anlæg ID *", font_weight="medium", color="gray.11"),
                    rx.input(
                        placeholder="f.eks. 1061",
                        value=State.current_address_anlaeg_id,
                        on_change=State.set_current_address_anlaeg_id,
                        required=True,
                        size="3",
                        width="100%",
                    ),
                    align="start",
                    spacing="1",
                ),
                
                # Navn (required)
                rx.vstack(
                    rx.text("Navn *", font_weight="medium", color="gray.11"),
                    rx.input(
                        placeholder="f.eks. Gert Svith, Birkesig Grusgrav",
                        value=State.current_address_navn,
                        on_change=State.set_current_address_navn,
                        required=True,
                        size="3",
                        width="100%",
                    ),
                    align="start",
                    spacing="1",
                ),
                
                # Adresse (required)
                rx.vstack(
                    rx.text("Adresse *", font_weight="medium", color="gray.11"),
                    rx.input(
                        placeholder="f.eks. Rugvænget 18",
                        value=State.current_address_adresse,
                        on_change=State.set_current_address_adresse,
                        required=True,
                        size="3",
                        width="100%",
                    ),
                    align="start",
                    spacing="1",
                ),
                
                # Post nr og By i samme række
                rx.hstack(
                    rx.vstack(
                        rx.text("Postnr *", font_weight="medium", color="gray.11"),
                        rx.input(
                            placeholder="f.eks. 8444",
                            value=State.current_address_postnr,
                            on_change=State.set_current_address_postnr,
                            required=True,
                            size="3",
                            max_length=4,
                            width="120px",
                        ),
                        align="start",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("By *", font_weight="medium", color="gray.11"),
                        rx.input(
                            placeholder="f.eks. Grenå",
                            value=State.current_address_by,
                            on_change=State.set_current_address_by,
                            required=True,
                            size="3",
                            width="100%",
                        ),
                        align="start",
                        spacing="1",
                        flex="1",
                    ),
                    spacing="3",
                    width="100%",
                ),
                
                # Action buttons
                rx.hstack(
                    rx.button(
                        rx.cond(
                            State.is_editing_address,
                            "Opdater",
                            "Tilføj"
                        ),
                        rx.icon(
                            rx.cond(
                                State.is_editing_address,
                                "check",
                                "plus"
                            ),
                            size=16
                        ),
                        on_click=rx.cond(
                            State.is_editing_address,
                            State.update_address_entry,
                            State.add_address_entry
                        ),
                        color_scheme="green",
                        size="3",
                        type="submit",
                    ),
                    rx.button(
                        "Annuller",
                        rx.icon("x", size=16),
                        on_click=State.cancel_address_editing,
                        color_scheme="gray",
                        variant="outline",
                        size="3",
                    ),
                    spacing="2",
                    justify="start",
                ),
                
                spacing="4",
                width="100%",
            ),
            on_submit=rx.cond(
                State.is_editing_address,
                State.update_address_entry,
                State.add_address_entry
            ),
            width="100%",
        ),
        
        padding="1.5rem",
        background="gray.3",
        border_radius="lg",
        border="1px solid",
        border_color="gray.6",
        width="100%",
        max_width="600px",
    )


def address_search_component() -> rx.Component:
    """
    Søge komponent til filtrering af adresser.
    """
    from jord_transport.jord_transport import State
    
    return rx.hstack(
        rx.input(
            placeholder="Søg efter anlæg ID, navn, adresse eller by...",
            value=State.address_search_text,
            on_change=State.set_address_search_text,
            size="3",
            width="100%",
        ),
        rx.button(
            rx.icon("search", size=16),
            "Søg",
            on_click=State.search_addresses,
            color_scheme="blue",
            size="3",
        ),
        rx.button(
            rx.icon("x", size=16),
            "Ryd",
            on_click=State.clear_address_search,
            color_scheme="gray",
            variant="outline",
            size="3",
        ),
        spacing="2",
        width="100%",
        margin_bottom="1rem",
    )


def address_table_component() -> rx.Component:
    """
    Tabel komponent til visning af adresser med CRUD funktionalitet.
    """
    from jord_transport.jord_transport import State
    
    return rx.vstack(
        # Search bar
        address_search_component(),
        
        # Address count info
        rx.text(
            rx.cond(
                State.filtered_addresses_length > 0,
                f"Viser {State.filtered_addresses_length} adresser",
                "Ingen adresser fundet"
            ),
            color="gray.10",
            size="2",
            margin_bottom="1rem",
        ),
        
        # Table
        rx.cond(
            State.filtered_addresses_length > 0,
            rx.scroll_area(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Anlæg ID", width="120px"),
                            rx.table.column_header_cell("Navn", width="200px"),
                            rx.table.column_header_cell("Adresse", width="180px"),
                            rx.table.column_header_cell("Postnr", width="80px"),
                            rx.table.column_header_cell("By", width="120px"),
                            rx.table.column_header_cell("Handlinger", width="140px"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            State.filtered_addresses,
                            lambda address, idx: rx.table.row(
                                rx.table.cell(
                                    rx.text(
                                        address.anlaeg_id,
                                        font_weight="medium",
                                        color="blue.9"
                                    ),
                                ),
                                rx.table.cell(
                                    rx.text(
                                        address.navn,
                                        font_weight="medium"
                                    ),
                                ),
                                rx.table.cell(
                                    rx.text(address.adresse),
                                ),
                                rx.table.cell(
                                    rx.text(address.postnr),
                                ),
                                rx.table.cell(
                                    rx.text(address.by),
                                ),
                                rx.table.cell(
                                    rx.hstack(
                                        rx.button(
                                            rx.icon("pencil", size=14),
                                            on_click=State.start_editing_address_by_index(idx),
                                            color_scheme="blue",
                                            variant="outline",
                                            size="1",
                                        ),
                                        rx.button(
                                            rx.icon("trash", size=14),
                                            on_click=State.delete_address_by_index(idx),
                                            color_scheme="red",
                                            variant="outline",
                                            size="1",
                                        ),
                                        spacing="1",
                                    ),
                                ),
                            ),
                        ),
                    ),
                    width="100%",
                    variant="surface",
                ),
                height="400px",
                width="100%",
            ),
            # Empty state
            rx.box(
                rx.vstack(
                    rx.icon("map-pin", size=48, color="gray.8"),
                    rx.text("Ingen adresser fundet", color="gray.10", font_style="italic"),
                    rx.text("Brug formularen ovenfor for at tilføje din første adresse", color="gray.8", size="2"),
                    spacing="2",
                    align="center",
                ),
                padding="3rem",
                text_align="center",
                background="gray.3",
                border_radius="lg",
                border="1px dashed",
                border_color="gray.6",
            ),
        ),
        
        width="100%",
    )


def address_stats_component() -> rx.Component:
    """
    Viser statistik om adresse databasen.
    """
    from jord_transport.jord_transport import State
    
    return rx.hstack(
        # Total addresses stat
        rx.box(
            rx.vstack(
                rx.text("Total Adresser", font_weight="medium", color="gray.11", size="2"),
                rx.text(State.addresses_length, font_weight="bold", color="blue.9", size="5"),
                rx.text("Modtager adresser i databasen", color="gray.10", size="1"),
                spacing="1",
                align="center",
            ),
            padding="1rem",
            background="blue.3",
            border_radius="lg",
            border="1px solid",
            border_color="blue.6",
            text_align="center",
        ),
        
        # Unique cities stat
        rx.box(
            rx.vstack(
                rx.text("Unikke Byer", font_weight="medium", color="gray.11", size="2"),
                rx.text(State.unique_cities_count, font_weight="bold", color="green.9", size="5"),
                rx.text("Forskellige byer", color="gray.10", size="1"),
                spacing="1",
                align="center",
            ),
            padding="1rem",
            background="green.3",
            border_radius="lg",
            border="1px solid",
            border_color="green.6",
            text_align="center",
        ),
        
        # Database status stat
        rx.box(
            rx.vstack(
                rx.text("Database Status", font_weight="medium", color="gray.11", size="2"),
                rx.text("Aktiv", font_weight="bold", color="orange.9", size="5"),
                rx.text("Filer gemmes automatisk", color="gray.10", size="1"),
                spacing="1",
                align="center",
            ),
            padding="1rem",
            background="orange.3",
            border_radius="lg",
            border="1px solid",
            border_color="orange.6",
            text_align="center",
        ),
        
        spacing="4",
        width="100%",
        justify="center",
        margin_bottom="2rem",
    )


def bulk_actions_component() -> rx.Component:
    """
    Bulk actions til import/export og database management.
    """
    from jord_transport.jord_transport import State
    
    return rx.hstack(
        rx.button(
            rx.icon("upload", size=16),
            "Import fra Excel",
            on_click=State.import_addresses_from_excel,
            color_scheme="green",
            size="3",
        ),
        rx.button(
            rx.icon("download", size=16),
            "Eksporter CSV",
            on_click=State.export_addresses_to_csv,
            color_scheme="blue",
            variant="outline",
            size="3",
        ),
        rx.button(
            rx.icon("database", size=16),
            "Backup Database",
            on_click=State.backup_address_database,
            color_scheme="purple",
            variant="outline",
            size="3",
        ),
        spacing="3",
        justify="center",
        margin_bottom="2rem",
    )


def address_list_component() -> rx.Component:
    """
    Hovedkomponent for address list med fuld CRUD funktionalitet.
    """
    from jord_transport.jord_transport import State
    
    return rx.vstack(
        # Page header
        rx.center(
            rx.heading(
                "Adresseliste",
                size="6",
                color="var(--accent-9)",
                margin_bottom="0.5rem"
            ),
        ),
        rx.center(
            rx.text(
                "Administrer modtager adresser til brug i ruteplanlægning",
                color="gray.10",
                size="3",
                margin_bottom="2rem",
                text_align="center"
            ),
        ),
        
        # Statistics
        rx.cond(
            State.addresses_length > 0,
            address_stats_component(),
            rx.fragment(),
        ),
        
        # Bulk actions
        bulk_actions_component(),
        
        # Address form
        address_form_component(),
        
        rx.divider(margin_y="2rem"),
        
        # Address table
        rx.heading("Eksisterende Adresser", size="4", color="var(--accent-9)", margin_bottom="1rem"),
        address_table_component(),
        
        spacing="4",
        width="100%",
        align="center",
    )