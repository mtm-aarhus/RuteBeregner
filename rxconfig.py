import reflex as rx

config = rx.Config(
    app_name="jord_transport",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)