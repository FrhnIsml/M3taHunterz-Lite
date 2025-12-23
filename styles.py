# styles.py
# --- THEME CONFIGURATION ---

# 1. WINDOW SETTINGS
# Increased height to 850 to fit the new Copy button row
WINDOW_SIZE = "1000x850"
APP_TITLE_TEXT = "M3taHunterz" 

# 2. COLOR PALETTE
COLORS = {
    "bg_main":    "#1e1e1e",   # Main Dark Background
    "bg_panel":   "#252526",   # Slightly lighter (for inputs/canvas)
    "bg_input":   "#333333",   # Input fields
    "text_main":  "#00ff00",   # Hacker Green
    "text_light": "#ffffff",   # White
    "text_dim":   "#cccccc",   # Light Grey
    "text_highlight": "#444444", # Selection color (Required for v11.5)
    
    # Buttons
    "btn_dark":   "#333333",   # Load/Copy
    "btn_warn":   "#f0ad4e",   # Fake (Orange)
    "btn_danger": "#d9534f",   # Scrub/Clear (Red)
    "btn_info":   "#5bc0de",   # Undo/Redo (Blue)
    "btn_success":"#00ff00",   # Save (Green)
}

# 3. FONTS
FONTS = {
    "header":      ("Consolas", 28, "bold"),
    "subhead":     ("Arial", 16, "bold"),
    "ui_bold":     ("Arial", 11, "bold"),
    "ui_norm":     ("Arial", 10),
    "code":        ("Consolas", 11),
    "small":       ("Arial", 8),
    "ui_sml_bold": ("Arial", 9, "bold")
}

# 4. BUTTON PRESETS
BTN_MAIN = {
    "font": FONTS["ui_bold"],
    "width": 12,
    "height": 2,
    "fg": "white",
    "bd": 0
}

BTN_NAV = {
    "font": ("Arial", 10, "bold"),  # Changed from 9 to 10 Bold
    "width": 10,                    # Slightly wider to fit text comfortably
    "height": 2,
    "fg": "white",                  # Changed Black to White for better readability
    "bd": 0
}

BTN_DANGER_SMALL = {
    "font": FONTS["ui_sml_bold"],
    "fg": "white",
    "bg": COLORS["btn_danger"],
    "padx": 10,
    "pady": 5
}