"""
Manuel input komponent for RuteBeregner applikationen.
"""
import reflex as rx
from jord_transport.jord_transport import State


def manual_input_component() -> rx.Component:
    """
    Manuel input komponent med start/slut adresser og udvidede CO₂ valg.
    
    Returns:
        rx.Component: Komplet manuel input panel
    """
    return rx.vstack(
        # Grundlæggende adresse inputs
        rx.vstack(
            
            # Start adresse
            rx.vstack(
                rx.text("Startadresse", font_weight="medium", style={"color": "var(--color-text-secondary)"}),
                rx.input(
                    placeholder="Indtast startadresse...",
                    value=State.current_start_address,
                    on_change=State.set_current_start_address,
                    width="100%",
                    size="3",
                    style={
                        "background": "var(--color-bg-card)",
                        "border_color": "var(--color-border-primary)",
                        "color": "var(--color-text-primary)",
                        "&:focus": {
                            "border_color": "var(--color-border-focus)",
                        }
                    }
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            
            # Slut adresse med toggle mellem manual og dropdown
            rx.vstack(
                rx.hstack(
                    rx.text("Slutadresse", font_weight="medium", style={"color": "var(--color-text-secondary)"}),
                    rx.spacer(),
                    rx.button(
                        rx.cond(
                            State.use_address_dropdown,
                            "Manual indtastning",
                            "Vælg fra liste"
                        ),
                        rx.icon(
                            rx.cond(
                                State.use_address_dropdown,
                                "keyboard",
                                "list"
                            ),
                            size=14
                        ),
                        on_click=State.toggle_address_dropdown,
                        size="1",
                        variant="outline",
                        color_scheme="blue",
                    ),
                    width="100%",
                    align="center",
                ),
                
                # Conditional input: either dropdown or manual input
                rx.cond(
                    State.use_address_dropdown,
                    # Simple address dropdown - må bruge reactive var
                    rx.cond(
                        State.addresses_length > 0,
                        rx.select(
                            State.address_dropdown_labels,
                            placeholder="Vælg slutdestination fra listen...",
                            on_change=State.handle_address_dropdown_change,
                            width="100%",
                            size="3",
                            style={
                                "background": "var(--color-bg-card)",
                                "border_color": "var(--color-border-primary)",
                                "color": "var(--color-text-primary)",
                            }
                        ),
                        rx.box(
                            rx.text(
                                "Ingen adresser tilgængelige. Gå til Adresseliste for at tilføje.",
                                style={"color": "var(--color-text-muted)"}
                            ),
                            padding="0.5rem",
                            border_radius="md",
                            border="1px solid",
                            style={
                                "background": "var(--color-bg-tertiary)",
                                "border_color": "var(--color-border-primary)",
                            },
                        ),
                    ),
                    # Manual input
                    rx.input(
                        placeholder="Indtast slutadresse...",
                        value=State.current_end_address,
                        on_change=State.set_current_end_address,
                        width="100%",
                        size="3",
                        style={
                            "background": "var(--color-bg-card)",
                            "border_color": "var(--color-border-primary)",
                            "color": "var(--color-text-primary)",
                            "&:focus": {
                                "border_color": "var(--color-border-focus)",
                            }
                        }
                    ),
                ),
                
                # Show selected address preview when using dropdown
                rx.cond(
                    rx.cond(
                        State.use_address_dropdown,
                        State.current_end_address != "",
                        False
                    ),
                    rx.box(
                        rx.text(
                            f"Valgt: {State.current_end_address}",
                            size="2",
                            font_style="italic",
                            style={"color": "var(--color-success)"}
                        ),
                        padding="0.5rem",
                        border_radius="md",
                        border="1px solid",
                        style={
                            "background": "rgba(22, 163, 74, 0.1)",
                            "border_color": "var(--color-success)",
                        },
                    ),
                    rx.fragment(),
                ),
                
                spacing="2",
                align="start",
                width="100%",
            ),
            
            spacing="3",
            width="100%",
            padding="1rem",
            border_radius="lg",
            border="1px solid",
            style={
                "background": "var(--color-bg-tertiary)",
                "border_color": "var(--color-border-primary)",
            },
        ),
        
        # Udvidede CO₂ valg (Accordion)
        rx.accordion.root(
            rx.accordion.item(
                header=rx.accordion.trigger(
                    rx.hstack(
                        rx.icon("settings", size=18, style={"color": "var(--accent-9)"}),
                        rx.text(
                            "Udvidede CO₂-valg",
                            font_weight="medium",
                            style={"color": "var(--accent-9)"},
                        ),
                        rx.spacer(),
                        spacing="2",
                        align="center",
                        width="100%",
                    ),
                    border="1px solid",
                    border_radius="lg",
                    padding="1rem",
                    style={
                        "background": "var(--color-bg-secondary)",
                        "border_color": "var(--color-border-primary)",
                        "&:hover": {
                            "background": "var(--color-bg-tertiary)",
                        }
                    },
                ),
                content=rx.accordion.content(
                    rx.vstack(
                        # Brændstof type
                        rx.vstack(
                            rx.text("Brændstof Type", font_weight="medium", style={"color": "var(--color-text-secondary)"}),
                            rx.select(
                                ["ikke_valgt", "diesel", "benzin", "el"],
                                placeholder="Vælg brændstof type",
                                value=State.current_fuel_type,
                                on_change=State.set_current_fuel_type,
                                width="100%",
                                size="3",
                                style={
                                    "background": "var(--color-bg-card)",
                                    "border_color": "var(--color-border-primary)",
                                    "color": "var(--color-text-primary)",
                                }
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                        ),
                        
                        # Last masse
                        rx.vstack(
                            rx.text("Last Masse (kg)", font_weight="medium", style={"color": "var(--color-text-secondary)"}),
                            rx.input(
                                placeholder="Indtast last masse i kg...",
                                value=State.current_load_mass_kg,
                                on_change=State.set_current_load_mass_kg,
                                type="number",
                                min=0,
                                width="100%",
                                size="3",
                                style={
                                    "background": "var(--color-bg-card)",
                                    "border_color": "var(--color-border-primary)",
                                    "color": "var(--color-text-primary)",
                                    "&:focus": {
                                        "border_color": "var(--color-border-focus)",
                                    }
                                }
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                        ),
                        
                        # Køretøjsklasse
                        rx.vstack(
                            rx.text("Køretøjsklasse", font_weight="medium", style={"color": "var(--color-text-secondary)"}),
                            rx.select(
                                ["ikke_valgt", "varebil", "lastbil", "stor_lastbil"],
                                placeholder="Vælg køretøjsklasse",
                                value=State.current_vehicle_class,
                                on_change=State.set_current_vehicle_class,
                                width="100%",
                                size="3",
                                style={
                                    "background": "var(--color-bg-card)",
                                    "border_color": "var(--color-border-primary)",
                                    "color": "var(--color-text-primary)",
                                }
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                        ),
                        
                        spacing="3",
                        width="100%",
                        padding="1rem",
                        border_radius="lg",
                        border="1px solid",
                        style={
                            "background": "var(--color-bg-card)",
                            "border_color": "var(--color-border-primary)",
                        },
                    ),
                ),
                value="co2_options",
            ),
            variant="soft",
            width="100%",
            margin_y="1rem",
        ),
        
        # Action knapper
        rx.hstack(
            rx.button(
                rx.icon("plus", size=18),
                "Tilføj til liste",
                on_click=State.add_manual_route,
                color_scheme="blue",
                size="3",
                font_weight="medium",
            ),
            rx.button(
                rx.icon("trash", size=18),
                "Ryd inputs",
                on_click=State.clear_inputs,
                variant="outline",
                color_scheme="gray",
                size="3",
                font_weight="medium",
            ),
            spacing="3",
            width="100%",
            justify="center",
        ),
        
        spacing="4",
        width="100%",
        align="start",
    )