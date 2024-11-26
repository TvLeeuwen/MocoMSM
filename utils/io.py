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
    st.write(f"Find your output in: {st.session_state.output_path}")

    if "example_path" not in st.session_state:
        st.session_state.example_path = os.path.join(
            st.session_state.moco_path, "app/example"
        )

    # Keep dir on homedir on refresh - may get stuck in /output
    if os.getcwd() == st.session_state.moco_path:
        os.makedirs(st.session_state.output_path, exist_ok=True)
    elif os.getcwd() == st.session_state.output_path:
        os.chdir(st.session_state.moco_path)


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
