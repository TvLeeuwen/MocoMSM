# Imports ---------------------------------------------------------------------
import os
import math
import numpy as np
import streamlit as st
import pyvista as pv
from stpyvista import stpyvista
from pathlib import Path

from utils.io import setup_paths, write_to_output, find_file_in_dir
from src.sto_generator import generate_sto, read_input
from src.moco_track_kinematics import moco_track_states

# Devs ------------------------------------------------------------------------
def visualize_obj(file_path):
    # Load the .obj file
    mesh = pv.read(file_path)
    # Create a PyVista plotter
    plotter = pv.Plotter(off_screen=True)
    plotter.add_mesh(mesh, color="white", show_edges=True)
    plotter.add_axes()
    plotter.add_floor()
    plotter.camera_position = 'iso'
    # Save the interactive plot to a file

    html_file = "output.html"
    plotter.export_html(html_file)
    return html_file

# Main ------------------------------------------------------------------------
st.title("OSim Moco track kinematics")

# Kill server -----------------------------------------------------------------
if st.button("Stop server"):
    st.warning("Shutting down the server...")
    os._exit(0)

# Set up paths ----------------------------------------------------------------
setup_paths()

# .osim uploader --------------------------------------------------------------
osim_file = st.file_uploader("Drag and drop you .osim model here", type=["osim"],)
if osim_file is not None:
    osim_file = write_to_output(osim_file, st.session_state.output_path)

# .osim uploader --------------------------------------------------------------
mat_file = st.file_uploader("Drag and drop you .mat model here", type=[".mat"])
if mat_file is not None:
    mat_file = write_to_output(mat_file, st.session_state.output_path)

# Run Moco --------------------------------------------------------------------
if osim_file is not None and mat_file is not None:
    if st.button("Run Moco"):
        try:
            os.chdir(st.session_state.output_path)
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

            st.session_state.moco_solution_path = moco_track_states(
                Path(osim_file.name),
                Path(sto_file.name),
                filter_params,
            )
            st.success("Script executed successfully!")
            st.write(f"Solution written: {st.session_state.moco_solution_path}")

            os.chdir(st.session_state.moco_path)

            # if st.button("Download solution"):
            #     with open(st.session_state.moco_solution_path.name, "rb") as temp_file:
            #         st.download_button(
            #             label="Download solution",
            #             data=temp_file,
            #             # file_name=f"{st.session_state.moco_solution_path}",
            #             mime="text/csv",

        except Exception as e:
            st.error(f"An error occurred: {e}")

else:
    st.write("No files uploaded yet. Please drag and drop a file.")


# Force vectors ---------------------------------------------------------------

# Initialize the session state for file_path

if "moco_solution_path" not in st.session_state:
    st.session_state.moco_solution_path = find_file_in_dir(
        st.session_state.output_path,
        "success.sto",
    )

if st.session_state.moco_solution_path is not None:
    st.write(
        "Moco solution file available:", st.session_state.moco_solution_path
    )

# Plotter ---------------------------------------------------------------------

mesh = pv.read(os.path.join(st.session_state.example_path, "Geometry/tmet.vtp"))
# mesh2 = pv.read(os.path.join(st.session_state.example_path, "Geometry/tibia.vtp"))

# # Define the initial force vector
# initial_point = np.array([0, 0, 0])  # Arrow origin
# vector = np.array([.01, 0, 0])  # Initial direction and magnitude
#
# # Create the arrow to represent the force vector
# arrow = pv.Arrow(start=initial_point, direction=vector, scale=1.0)

# Add the arrow to the plotter
# arrow_actor = plotter.add_mesh(arrow, color="blue")

# Set up a callback to update the arrow
# def callback(step):
#     print(step)
#     arrow_actor.position = [0, step*0.01]

plotter = pv.Plotter(window_size=[400,400])
plotter.add_mesh(mesh, color='white')
# plotter.add_mesh(mesh, scalars='my_scalar', cmap='bwr')
plotter.view_isometric()
plotter.add_scalar_bar()
plotter.show_axes()
plotter.background_color = 'black'

stpyvista(plotter, key="pv_tmet")


    # if st.button("Show force vectors"):
    #     try:
    #         # Here, you can use st.session_state.file_path to load your file
    #         st.write(f"Importing file from: {st.session_state.file_path}")
    #     except Exception as e:
    #         st.error(f"Error importing file: {e}")

if st.button("Animate"):
    plotter = pv.Plotter(window_size=[400,400])
    mesh = pv.read(os.path.join(st.session_state.example_path, "Geometry/tmet.vtp"))

    df, header = read_input(Path(st.session_state.moco_solution_path))

    pl = pv.Plotter()
    actor = pl.add_mesh(mesh, color="white")

    def callback(step):
        print(math.degrees(df["/jointset/ankle/ankle_flexion/value"].loc[step]))
        actor.orientation = [math.degrees(df["/jointset/ankle/ankle_flexion/value"].loc[step]), 0, 0]

    pl.add_timer_event(max_steps=200, duration=2000, callback=callback)
    pl.background_color = 'black'
    pl.view_isometric()
    pl.show()
