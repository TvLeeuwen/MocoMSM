# Imports ---------------------------------------------------------------------
import streamlit as st
import os
from pathlib import Path
from src.sto_generator import generate_sto
from src.moco_track_kinematics import moco_track_states


def write_to_temp(uploaded_file):
    temp_path = os.path.join("app/output", uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return Path(temp_path)


# Main ------------------------------------------------------------------------
st.title("OSim Moco track kinematics")

if os.path.basename(os.getcwd()) == "MocoMSM":
    os.makedirs("app/output", exist_ok=True)
elif os.path.basename(os.getcwd()) == "output":
    os.chdir("../..")

# Kill server -----------------------------------------------------------------
if st.button("Stop server"):
    st.warning("Shutting down the server...")
    os._exit(0)

# .osim uploader --------------------------------------------------------------
osim_file = st.file_uploader("Drag and drop you .osim model here", type=["osim"])
if osim_file is not None:
    osim_file = write_to_temp(osim_file)

# .osim uploader --------------------------------------------------------------
mat_file = st.file_uploader("Drag and drop you .mat model here", type=[".mat"])
if mat_file is not None:
    mat_file = write_to_temp(mat_file)

# Run Moco --------------------------------------------------------------------
if osim_file is not None and mat_file is not None:
    if st.button("Run Moco"):
        try:

            os.chdir("app/output")
            filter_params = {
                "state_filters": ["jointset"],
                "invert_filter": False,
            }

            sto_file = generate_sto(
                Path(mat_file.name),
                model_file=Path(osim_file.name),
            )
            st.write(f"Kinematics written: {sto_file}")
            st.write("Running Moco Track...")

            tracked_states_solution_file = moco_track_states(
                Path(osim_file.name),
                Path(sto_file.name),
                filter_params,
            )
            st.success("Script executed successfully!")
            st.write(f"Solution written: {tracked_states_solution_file}")

            os.chdir("../..")



            # if st.button("Download solution"):
            #     with open(tracked_states_solution_file.name, "rb") as temp_file:
            #         st.download_button(
            #             label="Download solution",
            #             data=temp_file,
            #             # file_name=f"{tracked_states_solution_file}",
            #             mime="text/csv",

        except Exception as e:
            st.error(f"An error occurred: {e}")

else:
    st.write("No file uploaded yet. Please drag and drop a file.")
