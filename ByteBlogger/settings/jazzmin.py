# ===============================
# JAZZMIN ADMIN CUSTOMIZATION
# ===============================

JAZZMIN_SETTINGS = {
    "site_title":
    "ByteBlogger Admin",
    "site_header":
    "ByteBlogger",
    "site_brand":
    "ByteBlogger",
    "welcome_sign":
    "Welcome to ByteBlogger Admin Panel",
    "copyright":
    "ByteBlogger © 2026",

    # Sidebar
    "show_sidebar":
    True,
    "navigation_expanded":
    True,
    "order_with_respect_to": ["users", "blog", "auth"],

    # Top Menu
    "topmenu_links": [
        {
            "name": "Dashboard",
            "url": "admin:index"
        },
        {
            "app": "users"
        },
        {
            "app": "blog"
        },
    ],

    # Icons
    "icons": {
        "users.User": "fas fa-user",
        "users.UserProfile": "fas fa-id-card",
        "users.OTPRequest": "fas fa-key",
        "auth.Group": "fas fa-users-cog",
        "blog.Post": "fas fa-blog",
    },

    # Force Dark Theme
    "theme":
    "darkly",
    "dark_mode_theme":
    "darkly",

    # Buttons
    "button_classes": {
        "primary": "btn btn-primary",
        "secondary": "btn btn-secondary",
        "info": "btn btn-info",
        "warning": "btn btn-warning",
        "danger": "btn btn-danger",
        "success": "btn btn-success",
    },

    # Disable UI Builder (cleaner admin)
    "show_ui_builder":
    False,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "navbar": "navbar-dark bg-dark",
    "no_navbar_border": True,
    "sidebar": "sidebar-dark-primary",
    "accent": "accent-info",
    "navbar_small_text": False,
    "footer_small_text": False,
    "sidebar_nav_small_text": False,
    "sidebar_nav_flat_style": True,
}