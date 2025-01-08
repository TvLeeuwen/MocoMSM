# Imports ---------------------------------------------------------------------
from app.widgets.app_setup import setup_app
from app.widgets.io import setup_paths

# Main ------------------------------------------------------------------------
setup_paths()
app_pages = setup_app()

app_pages.run()
