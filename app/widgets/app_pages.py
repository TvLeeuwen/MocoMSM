# Imports ---------------------------------------------------------------------
import os
import streamlit as st
from app.widgets.app_io import osim_uploader, mat_uploader
from app.widgets.app_functions import run_moco, force_vector_extraction
from app.widgets.app_visuals import (
    visual_compare_timeseries,
    visual_validate_muscle_parameters,
    visual_force_vector_gif,
)


# Defs ------------------------------------------------------------------------
def page_home():
    st.title("Input")
    st.write(f"Home directory: {st.session_state.moco_path}")

    osim_uploader()
    mat_uploader()

    st.write(st.session_state)


def page_moco():
    st.title("Run Moco track kinematics")

    # Run Moco ----------------------------------------------------------------
    if st.session_state.osim_path is not None and st.session_state.mat_path is not None:
        st.subheader("Moco kinematics tracking")
        run_moco(
            st.session_state.moco_path,
            st.session_state.osim_path,
            st.session_state.mat_path,
            st.session_state.output_path,
        )
    else:
        st.write("No files uploaded yet. Please drag and drop a file to run Moco.")

    # Compare kinematics ------------------------------------------------------
    if st.session_state.moco_solution_path is not None and os.path.exists(
        st.session_state.moco_solution_path
    ):
        st.subheader("Validate output versus input")

        visual_compare_timeseries(
            st.session_state.kinematics_path,
            st.session_state.moco_solution_path,
        )

    # Validate muscle parameters ----------------------------------------------
    if st.session_state.moco_solution_muscle_fiber_path is not None and os.path.exists(
        st.session_state.moco_solution_muscle_fiber_path
    ):
        st.subheader("Muscle fiber parameters")

        visual_validate_muscle_parameters(
            st.session_state.moco_solution_muscle_fiber_path,
        )


def page_force_vector():
    st.header("Force vector extraction")
    try:
        st.write(f"Model selected: {os.path.basename(st.session_state.osim_path)}")
    except:
        st.write(f"Model selected: {st.session_state.osim_path}")

    if (
        st.session_state.osim_path is not None
        and st.session_state.moco_solution_path is not None
    ):
        force_vector_extraction(
            st.session_state.osim_path,
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


def page_FE():
    st.title("Finite element")
    st.write(st.session_state)

def page_output():
    st.title("Output")
    st.write(f"Output directory: {st.session_state.output_path}")

    output_files = [
        f
        for f in os.listdir(st.session_state.output_path)
        if os.path.isfile(os.path.join(st.session_state.output_path, f))
    ]

    if output_files:
        st.subheader("Files")
        for file_name in output_files:
            with open(
                os.path.join(st.session_state.output_path, file_name), "rb"
            ) as file:
                file_data = file.read()
                st.download_button(
                    label=f"{file_name}",
                    data=file_data,
                    file_name=file_name,
                )

        st.subheader("Clear output")
        if st.button("Clear all output"):
            for file in os.listdir(st.session_state.output_path):
                file_path = os.path.join(st.session_state.output_path, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            st.session_state.moco_solution_path = None
            st.rerun()
    else:
        st.write("Output folder is empty")
