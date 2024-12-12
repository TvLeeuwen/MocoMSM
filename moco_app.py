# Imports ---------------------------------------------------------------------
import os
import streamlit as st

from app.widgets.io import setup_paths, setup_sidebar, osim_uploader, mat_uploader
from app.widgets.functions import run_moco, force_vector_extraction
from app.widgets.visuals import visual_compare_timeseries, visual_force_vector_gif


# Main ------------------------------------------------------------------------
st.title("OSim Moco track kinematics")

# Set up paths ----------------------------------------------------------------
setup_paths()

# Sidebar ---------------------------------------------------------------------
setup_sidebar()

# Upload files ----------------------------------------------------------------
st.subheader("Run Moco track kinematics")

osim_uploader()

mat_uploader()


# Run Moco --------------------------------------------------------------------
if st.session_state.osim_file is not None and st.session_state.mat_path is not None:
    st.subheader("Moco kinematics tracking")
    run_moco(
        st.session_state.moco_path,
        st.session_state.osim_file,
        st.session_state.mat_path,
        st.session_state.output_path,
    )
else:
    st.write("No files uploaded yet. Please drag and drop a file.")


# Compare kinematics ----------------------------------------------------------
if st.session_state.moco_solution_path is not None and os.path.exists(
    st.session_state.moco_solution_path
):
    st.subheader("Compare timeseries")

    visual_compare_timeseries(
        st.session_state.kinematics_path,
        st.session_state.moco_solution_path,
    )

# Force vectors ---------------------------------------------------------------
if (
    st.session_state.osim_file is not None
    and st.session_state.moco_solution_path is not None
):
    # Gif ---------------------------------------------------------------------
    force_vector_extraction(
        st.session_state.osim_file,
        st.session_state.moco_solution_path,
        st.session_state.output_path,
    )

if (
    st.session_state.force_origins_path is not None
    and st.session_state.force_vectors_path is not None
    and os.path.exists(st.session_state.force_origins_path)
    and os.path.exists(st.session_state.force_vectors_path)
):

    if st.button("Generate gif"):
        visual_force_vector_gif(
            st.session_state.osim_file,
            os.path.join(st.session_state.example_path, "Geometry/tmet.vtp"),
            st.session_state.moco_solution_path,
            st.session_state.force_origins_path,
            st.session_state.force_vectors_path,
            st.session_state.output_path,
        )


if st.session_state.gif_path is not None and os.path.isfile(
    st.session_state.gif_path,
):
    st.image(
        st.session_state.gif_path,
        caption="Force vector over time",
    )
