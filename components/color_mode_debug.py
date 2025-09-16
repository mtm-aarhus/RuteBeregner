"""
Debug komponent til at teste color mode synchronization
"""
import reflex as rx
from jord_transport.jord_transport import State


def color_mode_debug_panel() -> rx.Component:
    """
    Debug panel til at vise color mode status og test synchronization.
    
    Returns:
        rx.Component: Debug panel
    """
    return rx.box(
        rx.vstack(
            rx.heading("Color Mode Debug", size="4"),
            
            # Current state display
            rx.vstack(
                rx.text(f"Current Mode: {State.color_mode}"),
                rx.text(f"System Preference: {State.system_preference}"),
                rx.text(f"Effective Mode: {State.current_effective_mode}"),
                
                spacing="1",
                align="start",
            ),
            
            # Test buttons
            rx.hstack(
                rx.button(
                    "Set Light",
                    on_click=lambda: State.set_color_mode("light"),
                    size="2",
                    color_scheme="yellow",
                ),
                rx.button(
                    "Set Dark", 
                    on_click=lambda: State.set_color_mode("dark"),
                    size="2",
                    color_scheme="gray",
                ),
                rx.button(
                    "Set System",
                    on_click=lambda: State.set_color_mode("system"),
                    size="2",
                    color_scheme="blue",
                ),
                spacing="2",
            ),
            
            # System info
            rx.text("Client-side info:", font_weight="bold"),
            rx.script("""
                // Display client-side color mode info
                if (window.colorModeUtils) {
                    const info = document.createElement('div');
                    info.innerHTML = `
                        <div>Client Mode: ${window.colorModeUtils.getCurrentMode()}</div>
                        <div>Effective Mode: ${window.colorModeUtils.getEffectiveMode()}</div>
                        <div>System Preference: ${window.colorModeUtils.getSystemPreference()}</div>
                    `;
                    document.currentScript.parentNode.appendChild(info);
                }
            """),
            
            spacing="3",
            align="start",
        ),
        
        padding="1rem",
        background="var(--color-bg-card)",
        border="1px solid var(--color-border-primary)",
        border_radius="0.5rem",
        margin="1rem",
    )


def color_mode_sync_test() -> rx.Component:
    """
    Test komponent til cross-tab synchronization.
    
    Returns:
        rx.Component: Sync test interface
    """
    return rx.box(
        rx.vstack(
            rx.heading("Cross-Tab Sync Test", size="4"),
            rx.text("Åbn denne side i flere tabs og test synchronization"),
            
            rx.button(
                "Test Cross-Tab Sync",
                on_click=rx.call_script("""
                    // Test cross-tab synchronization
                    const modes = ['light', 'dark', 'system'];
                    let index = 0;
                    
                    const interval = setInterval(() => {
                        if (window.colorModeUtils) {
                            const mode = modes[index];
                            window.colorModeUtils.setMode(mode);
                            console.log('Auto-switching to:', mode);
                            
                            index = (index + 1) % modes.length;
                            
                            if (index === 0) {
                                clearInterval(interval);
                                console.log('Cross-tab sync test completed');
                            }
                        }
                    }, 2000);
                """),
                color_scheme="green",
            ),
            
            spacing="2",
            align="start",
        ),
        
        padding="1rem", 
        background="var(--color-bg-card)",
        border="1px solid var(--color-border-primary)",
        border_radius="0.5rem",
        margin="1rem",
    )