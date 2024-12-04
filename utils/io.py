"""Functions to facilitate file I/O"""

# Imports ---------------------------------------------------------------------
import os
from pathlib import Path
import streamlit as st


# Defs ------------------------------------------------------------------------
def setup_paths():
    if "moco_path" not in st.session_state:
        st.session_state.moco_path = os.getcwd()
    st.write(f"Home directory: {st.session_state.moco_path}")

    if "output_path" not in st.session_state:
        st.session_state.output_path = os.path.join(
            st.session_state.moco_path, "app/output"
        )

    if "example_path" not in st.session_state:
        st.session_state.example_path = os.path.join(
            st.session_state.moco_path, "app/example"
        )

    if "moco_solution_path" not in st.session_state:
        st.session_state.moco_solution_path = os.path.join(
            st.session_state.output_path,
            find_file_in_dir(
                st.session_state.output_path,
                "success.sto",
            ),
        )
    if "kinematics_path" not in st.session_state:
        st.session_state.kinematics_path = os.path.join(
            st.session_state.output_path,
            find_file_in_dir(
                st.session_state.output_path,
                "moco_track_states.sto",
            ),
        )
    if "gif_path" not in st.session_state:
        st.session_state.gif_path = os.path.join(
            st.session_state.output_path, "vectors.gif"
        )

    # Keep dir on homedir on refresh - may get stuck in /output
    if os.getcwd() == st.session_state.moco_path:
        os.makedirs(st.session_state.output_path, exist_ok=True)
    elif os.getcwd() == st.session_state.output_path:
        os.chdir(st.session_state.moco_path)


def setup_sidebar():
    if st.sidebar.button("Stop server"):
        os._exit(0)

    output_files = [
        f
        for f in os.listdir(st.session_state.output_path)
        if os.path.isfile(os.path.join(st.session_state.output_path, f))
    ]
    st.sidebar.header("Output folder")
    st.sidebar.write(f"Find your output in: {st.session_state.output_path}")
    st.sidebar.header("Output files")
    if output_files:
        if st.sidebar.button("Clear all output"):
            for file in os.listdir(st.session_state.output_path):
                file_path = os.path.join(st.session_state.output_path, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            st.session_state.moco_solution_path = None
            st.rerun()

        st.sidebar.header("Files")
        for file in output_files:
            st.sidebar.write(file)
    else:
        st.sidebar.text("Output folder is empty")


def find_file_in_dir(directory, string):
    for root, _, files in os.walk(directory):
        for file in files:
            if string in file.lower():
                return os.path.join(root, file)
    return None


def write_to_output(file, output_dir):
    file_path = os.path.join(output_dir, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    return Path(file_path)
