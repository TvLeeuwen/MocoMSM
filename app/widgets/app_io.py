"""Functions to facilitate file I/O"""

# Imports ---------------------------------------------------------------------
import os
import streamlit as st

from src.sto_generator import read_mat_to_df


# Defs ------------------------------------------------------------------------
def setup_paths():

    # Folders -----------------------------------------------------------------
    if "moco_path" not in st.session_state:
        st.session_state.moco_path = os.getcwd()

    if "output_path" not in st.session_state:
        st.session_state.output_path = os.path.join(
            st.session_state.moco_path, "app/output"
        )

    if "example_path" not in st.session_state:
        st.session_state.example_path = os.path.join(
            st.session_state.moco_path, "app/example"
        )

    # Files -------------------------------------------------------------------
    if "osim_path" not in st.session_state:
        st.session_state.osim_path = find_file_in_dir(
            st.session_state.output_path,
            ".osim",
        )
    if "mat_path" not in st.session_state:
        st.session_state.mat_path = find_file_in_dir(
            st.session_state.output_path,
            ".mat",
        )
    if "kinematics_path" not in st.session_state:
        st.session_state.kinematics_path = find_file_in_dir(
            st.session_state.output_path,
            "moco_track_states.sto",
        )

    if "moco_solution_path" not in st.session_state:
        st.session_state.moco_solution_path = find_file_in_dir(
            st.session_state.output_path,
            "success.sto",
        )

    if "moco_solution_muscle_fiber_path" not in st.session_state:
        st.session_state.moco_solution_muscle_fiber_path = find_file_in_dir(
            st.session_state.output_path,
            "muscle_fiber_data.sto",
        )

    if "force_origins_path" not in st.session_state:
        st.session_state.force_origins_path = find_file_in_dir(
            st.session_state.output_path,
            "muscle_origins.json",
        )

    if "force_vectors_path" not in st.session_state:
        st.session_state.force_vectors_path = find_file_in_dir(
            st.session_state.output_path,
            "muscle_vectors.json",
        )

    if "gif_path" not in st.session_state:
        st.session_state.gif_path = find_file_in_dir(
            st.session_state.output_path,
            "vectors.gif",
        )

    # Keep dir on homedir on refresh - may get stuck in /output
    if os.getcwd() == st.session_state.moco_path:
        os.makedirs(st.session_state.output_path, exist_ok=True)
    elif os.getcwd() == st.session_state.output_path:
        os.chdir(st.session_state.moco_path)


def find_file_in_dir(directory, string):
    for root, _, files in os.walk(directory):
        f = 0
        for file in files:
            if string in file.lower():
                f += 1
                if f > 1:
                    print("Multiple .osim files detected. Autoselected None...")
                    return None
                osim_file = os.path.join(root, file)
        return osim_file if osim_file else None


def write_to_output(file, output_dir):
    file_path = os.path.join(output_dir, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())

    return file_path


def osim_uploader():
    osim_path = st.file_uploader(
        "Drag and drop you .osim model here",
        type=["osim"],
    )
    if osim_path is not None:
        st.session_state.osim_path = write_to_output(
            osim_path, st.session_state.output_path
        )


def mat_uploader():
    mat_path = st.file_uploader(
        "Drag and drop you .mat data file here", type=[".mat"]
    )
    if mat_path is not None:
        st.session_state.mat_path = write_to_output(
            mat_path, st.session_state.output_path
        )

    if st.session_state.mat_path is not None:
        with st.expander("Show .mat keyvalues", expanded=False):
            df = read_mat_to_df(st.session_state.mat_path)
            st.write([col[:-3] for col in df if col.endswith("Ang")])
