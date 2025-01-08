import os
from app.widgets.app_pages import *


def setup_app():
    pages = {
        "App": [
            st.Page(page_home, title="Home"),
        ],
        "MSM": [
            st.Page(page_moco, title="Moco"),
            st.Page(page_force_vector, title="Force vectors"),
        ],
        "Output": [
            st.Page(page_output, title="Output"),
        ]
    }

    pg = st.navigation(pages)

    if st.sidebar.button("Stop server"):
        os._exit(0)

    return pg
