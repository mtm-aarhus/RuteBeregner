"""
Hovedside til RuteBeregner applikationen.
"""
import reflex as rx
from components.address_mapping import get_all_companies

def file_upload_area() -> rx.Component:
    """Filupload-komponent."""
    return rx.vstack(
        rx.heading("Upload af rutedata", size="md"),
        rx.text("Upload en Excel eller CSV fil med dine rutedata"),
        rx.upload(
            rx.vstack(
                rx.icon("upload", size=36),
                rx.text("Træk filer hertil eller klik for at browse"),
                rx.text("Understøtter .csv, .xlsx og .xls", color="gray"),
                padding="30px",
                border="2px dashed",
                border_color="gray",
                border_radius="md",
            ),
            multiple=False,
            accept=[".csv", ".xlsx", ".xls"],
            max_files=1,
            on_change=rx.State.handle_file_upload,
        ),
        rx.cond(
            rx.State.uploaded_file != "",
            rx.hstack(
                rx.icon("check", color="green"),
                rx.text(rx.State.uploaded_file),
                rx.spacer(),
                rx.button(
                    "Nulstil",
                    on_click=rx.State.clear_uploaded_file,
                    size="sm",
                    color_scheme="red",
                ),
            ),
        ),
        width="100%",
        spacing="4",
        padding="20px",
        border="1px solid",
        border_color="gray.200",
        border_radius="md",
    )

def route_table() -> rx.Component:
    """Tabel der viser ruter og mulighed for at beregne afstande."""
    return rx.cond(
        rx.State.route_data_length > 0,
        rx.vstack(
            rx.heading("Ruter", size="md"),
            rx.data_table(
                data=rx.State.route_data,
                columns=[
                    rx.data_column("Virksomhed", "company_name"),
                    rx.data_column("Startadresse", "start_address"),
                    rx.data_column("Slutadresse", "end_address"),
                    rx.data_column("Afstand (km)", lambda row: rx.State.distance_results.get(row.id, "-")),
                    rx.data_column(
                        "Handlinger",
                        lambda row: rx.hstack(
                            rx.button(
                                "Beregn",
                                on_click=rx.State.calculate_single_distance(row.id),
                                size="sm",
                                color_scheme="blue",
                            ),
                            rx.button(
                                "Rediger",
                                on_click=rx.redirect(f"/rediger/{row.id}"),
                                size="sm",
                                variant="outline",
                            ),
                            spacing="2",
                        ),
                    ),
                ],
                pagination=True,
                search=True,
                sort=True,
            ),
            rx.hstack(
                rx.button(
                    rx.cond(
                        rx.State.calculation_progress.get("in_progress", False),
                        f"Beregner... ({rx.State.calculation_progress.get('current', 0)}/{rx.State.calculation_progress.get('total', 0)})",
                        "Beregn alle afstande"
                    ),
                    on_click=rx.State.calculate_all_distances,
                    color_scheme="green",
                    disabled=rx.State.calculation_progress.get("in_progress", False),
                    loading=rx.State.calculation_progress.get("in_progress", False),
                ),
                rx.button(
                    "Tilføj ny rute", 
                    on_click=rx.State.add_manual_route,
                    variant="outline",
                ),
                rx.spacer(),
                rx.button(
                    "Eksporter resultater", 
                    on_click=rx.window_alert("Eksport funktionalitet kommer snart"),
                    color_scheme="purple",
                    variant="outline",
                ),
                width="100%",
            ),
            width="100%",
            spacing="4",
            padding="20px",
            border="1px solid",
            border_color="gray.200",
            border_radius="md",
        ),
        rx.fragment(),
    )

def index() -> rx.Component:
    """RuteBeregner hovedside."""
    return rx.container(
        rx.vstack(
            rx.heading("RuteBeregner", size="xl"),
            rx.text("Beregn reelle kørselsafstande mellem adresser"),
            rx.divider(),
            file_upload_area(),
            route_table(),
            rx.divider(),
            rx.text("© 2025 RuteBeregner", size="sm", color="gray"),
            width="100%",
            spacing="6",
            padding_y="20px",
            max_width="1200px",
        )
    )

# Tilføj siden til appen
def about() -> rx.Component:
    """Om RuteBeregner siden."""
    return rx.container(
        rx.vstack(
            rx.heading("Om RuteBeregner", size="xl"),
            rx.text(
                "RuteBeregner er et værktøj til at beregne reelle kørselsafstande mellem adresser. "
                "Upload en Excel eller CSV fil med dine rutedata, eller indtast adresserne manuelt."
            ),
            rx.divider(),
            rx.heading("Understøttede virksomheder", size="lg"),
            rx.text("Følgende virksomheder er registreret i systemet med automatisk adresseopslag:"),
            rx.ordered_list(
                [rx.text(company) for company in get_all_companies()],
                spacing="1",
            ),
            rx.divider(),
            rx.link("Tilbage til forsiden", href="/", button=True, color_scheme="blue"),
            width="100%",
            spacing="6",
            padding_y="20px",
            max_width="800px",
        )
    )
