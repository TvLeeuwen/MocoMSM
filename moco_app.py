# Imports ---------------------------------------------------------------------
from app.widgets.app_io import setup_paths
from app.widgets.app_setup import setup_app

# Main ------------------------------------------------------------------------
if __name__ == '__main__':

    setup_paths()
    app = setup_app()
    app.run()
