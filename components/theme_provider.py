"""
Theme Provider komponent til CSS injection
"""
import reflex as rx
from theme.custom_theme import generate_css_variables


def theme_provider() -> rx.Component:
    """
    Theme provider der injicerer CSS variables for color mode support.
    
    Returns:
        rx.Component: Style tag med CSS variables
    """
    return rx.el.style(
        generate_css_variables(),
        # Ensures the styles are injected in the head
        type="text/css"
    )


def color_mode_script() -> rx.Component:
    """
    Enhanced script til color mode management med sync support.
    
    Returns:
        rx.Component: Script tag med color mode initialization og sync
    """
    return rx.script(
        """
        // Enhanced Color Mode Management with Synchronization
        (function() {
            const STORAGE_KEY = 'color_mode';
            const DEFAULT_MODE = 'system';
            
            let currentMode = localStorage.getItem(STORAGE_KEY) || DEFAULT_MODE;
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            const root = document.documentElement;
            
            // State synchronization with backend
            let lastSyncedMode = null;
            
            function getEffectiveMode(mode) {
                return mode === 'system' ? (mediaQuery.matches ? 'dark' : 'light') : mode;
            }
            
            function applyColorMode(mode, skipStorage = false) {
                const effectiveMode = getEffectiveMode(mode);
                
                // Apply to DOM
                root.setAttribute('data-color-mode', effectiveMode);
                root.style.colorScheme = effectiveMode;
                
                // Apply theme class for additional styling if needed
                root.classList.remove('light-theme', 'dark-theme');
                root.classList.add(effectiveMode + '-theme');
                
                // Store in localStorage if not skipped
                if (!skipStorage) {
                    localStorage.setItem(STORAGE_KEY, mode);
                }
                
                // Sync with other tabs
                if (!skipStorage) {
                    window.dispatchEvent(new StorageEvent('storage', {
                        key: STORAGE_KEY,
                        newValue: mode,
                        oldValue: currentMode,
                        storageArea: localStorage
                    }));
                }
                
                currentMode = mode;
                
                // Sync with backend state if changed
                if (mode !== lastSyncedMode) {
                    lastSyncedMode = mode;
                    try {
                        // Send sync event to backend
                        window.dispatchEvent(new CustomEvent('syncColorModeToBackend', {
                            detail: { mode: mode, effectiveMode: effectiveMode }
                        }));
                    } catch (e) {
                        console.warn('Could not sync color mode to backend:', e);
                    }
                }
                
                console.log(`Color mode applied: ${mode} (effective: ${effectiveMode})`);
            }
            
            // Initialize color mode
            applyColorMode(currentMode);
            
            // Listen for system preference changes
            mediaQuery.addEventListener('change', function(e) {
                console.log('System color preference changed:', e.matches ? 'dark' : 'light');
                
                if (currentMode === 'system') {
                    applyColorMode('system', true); // Skip storage update
                }
                
                // Notify about system change
                window.dispatchEvent(new CustomEvent('systemColorModeChanged', {
                    detail: { matches: e.matches, mode: e.matches ? 'dark' : 'light' }
                }));
            });
            
            // Listen for storage changes (cross-tab synchronization)
            window.addEventListener('storage', function(e) {
                if (e.key === STORAGE_KEY && e.newValue && e.newValue !== currentMode) {
                    console.log('Color mode synchronized from another tab:', e.newValue);
                    applyColorMode(e.newValue, true); // Skip storage update to avoid loop
                }
            });
            
            // Listen for programmatic changes from React components
            window.addEventListener('colorModeChange', function(e) {
                const newMode = e.detail;
                console.log('Color mode changed programmatically:', newMode);
                applyColorMode(newMode);
            });
            
            // Expose utility functions globally
            window.colorModeUtils = {
                getCurrentMode: () => currentMode,
                getEffectiveMode: () => getEffectiveMode(currentMode),
                setMode: (mode) => applyColorMode(mode),
                isSystemMode: () => currentMode === 'system',
                getSystemPreference: () => mediaQuery.matches ? 'dark' : 'light'
            };
            
            // Auto-sync every 30 seconds to ensure consistency
            setInterval(() => {
                const savedMode = localStorage.getItem(STORAGE_KEY) || DEFAULT_MODE;
                if (savedMode !== currentMode) {
                    console.log('Auto-sync: Mode drift detected, correcting...');
                    applyColorMode(savedMode, true);
                }
            }, 30000);
            
            console.log('Color Mode Management initialized');
            
        })();
        """
    )


def with_theme(component: rx.Component) -> rx.Component:
    """
    Wrapper der tilføjer theme support til en komponent.
    
    Args:
        component: Komponenten der skal wrappes
        
    Returns:
        rx.Component: Component med theme support
    """
    return rx.fragment(
        theme_provider(),
        color_mode_script(),
        component,
    )