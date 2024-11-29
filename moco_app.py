# Imports ---------------------------------------------------------------------
import os
import time
import math
import shutil
import numpy as np
import streamlit as st
import pyvista as pv
import plotly.graph_objects as go
import plotly.colors as pc
from stpyvista import stpyvista
from pathlib import Path

from utils.io import setup_paths, setup_sidebar, write_to_output
from src.sto_generator import generate_sto, read_input
from src.moco_track_kinematics import moco_track_states


# Main ------------------------------------------------------------------------
st.title("OSim Moco track kinematics")

# Set up paths ----------------------------------------------------------------
setup_paths()

# Sidebar ---------------------------------------------------------------------
setup_sidebar()


# .osim uploader --------------------------------------------------------------
st.subheader("Run Moco track kinematics")

st.session_state.osim_file = st.file_uploader(
    "Drag and drop you .osim model here",
    type=["osim"],
)
if st.session_state.osim_file is not None:
    st.session_state.osim_file = write_to_output(
        st.session_state.osim_file, st.session_state.output_path
    )

# .mat uploader --------------------------------------------------------------
st.session_state.mat_path = st.file_uploader(
    "Drag and drop you .mat data file here", type=[".mat"]
)
if st.session_state.mat_path is not None:
    st.session_state.mat_path = write_to_output(
        st.session_state.mat_path, st.session_state.output_path
    )

# Run Moco --------------------------------------------------------------------
if st.session_state.osim_file is not None and st.session_state.mat_path is not None:
    if st.button("Run Moco"):
        try:
            os.chdir(st.session_state.output_path)
            filter_params = {
                "state_filters": ["jointset"],
                "invert_filter": False,
            }

            st.session_state.kinematics_path = generate_sto(
                Path(st.session_state.mat_path.name),
                model_file=Path(st.session_state.osim_file.name),
            )
            st.write(f"Kinematics written: {st.session_state.kinematics_path}")
            st.write("Running Moco Track...")

            st.session_state.moco_solution_path = moco_track_states(
                Path(st.session_state.osim_file.name),
                Path(st.session_state.kinematics_path.name),
                filter_params,
            )
            os.chdir(st.session_state.moco_path)

            st.success("Script executed successfully!")
            st.write(f"Solution written: {st.session_state.moco_solution_path}")

        except Exception as e:
            st.error(f"An error occurred: {e}")

else:
    st.write("No files uploaded yet. Please drag and drop a file.")

# 2D Plot ---------------------------------------------------------------------
if st.session_state.moco_solution_path is not None and os.path.exists(
    os.path.join(st.session_state.output_path, st.session_state.moco_solution_path)
):
    st.subheader("Compare timeseries")
    df, _ = read_input(
        Path(
            os.path.join(st.session_state.output_path, st.session_state.kinematics_path)
        )
    )
    df2, _ = read_input(
        Path(
            os.path.join(
                st.session_state.output_path, st.session_state.moco_solution_path
            )
        )
    )

    color_scale_df = pc.get_colorscale("Viridis")
    fig = go.Figure()
    for i, column in enumerate(df.columns):
        if column != "time":
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[column],
                    mode="lines",
                    line=dict(color=color_scale_df[i % len(color_scale_df)][1]),
                    name=f"Input: {column}",
                    legendgroup=column,
                )
            )
    for column in df2.columns:
        if column != "time":
            fig.add_trace(
                go.Scatter(
                    x=df2.index,
                    y=df2[column],
                    mode="lines",
                    name=f"Output: {column}",
                    legendgroup=column,
                )
            )

    fig.update_layout(
        title=f"Input versus output data",
        height=1000,
        xaxis_title="Time (s)",
        yaxis_title="Value",
        legend_title="Variables",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="right",
            x=0.5,
            itemsizing="constant",
            traceorder="grouped",
        ),
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# Force vectors ---------------------------------------------------------------
# 3D Plot ---------------------------------------------------------------------
if st.session_state.moco_solution_path is not None:
    st.subheader("3D Plot")
    if st.button("Plot 3D"):
        mesh = pv.read(os.path.join(st.session_state.example_path, "Geometry/tmet.vtp"))
        # mesh2 = pv.read(os.path.join(st.session_state.example_path, "Geometry/tibia.vtp"))

        # # Define the initial force vector
        # vector_origin = np.array([0, 0, 0])  # Arrow origin
        # vector = np.array([.01, 0, 0])  # Initial direction and magnitude
        #
        # # Create the arrow to represent the force vector
        # arrow = pv.Arrow(start=vector_origin, direction=vector, scale=1.0)

        # Add the arrow to the plotter
        # arrow_actor = plotter.add_mesh(arrow, color="blue")

        # Set up a callback to update the arrow
        # def callback(step):
        #     print(step)
        #     arrow_actor.position = [0, step*0.01]

        plotter = pv.Plotter(window_size=[400, 400])
        plotter.add_mesh(mesh, color="white")
        # plotter.add_mesh(mesh, scalars='my_scalar', cmap='bwr')
        plotter.view_isometric()
        plotter.add_scalar_bar()
        plotter.show_axes()
        plotter.background_color = "black"

        stpyvista(plotter, key="pv_tmet")

    if st.button("Animate"):
        plotter = pv.Plotter(window_size=[400, 400])
        mesh = pv.read(os.path.join(st.session_state.example_path, "Geometry/tmet.vtp"))

        df, header = read_input(
            Path(
                os.path.join(
                    st.session_state.output_path, st.session_state.moco_solution_path
                )
            )
        )

        pl = pv.Plotter()
        actor = pl.add_mesh(mesh, color="white")

        force_vector = pl.add_mesh(
            pv.Arrow(
                start=[
                    -0.0062599999999999999,
                    -0.0025200000000000001,
                    -0.00055000000000000003,
                ],
                direction=[1, 0, 0],
                scale=0.1,
            ),
            color="red",
        )
        force_vector2 = pl.add_mesh(
            pv.Arrow(
                start=[0.00313, -0.01427, 0.0013500000000000001],
                direction=[-1, 0, 0],
                scale=0.1,
            ),
            color="blue",
        )

        def callback(step):
            print(step % len(df["time"]))
            force_vector.scale = df["/forceset/FL_p_test/normalized_tendon_force"].loc[
                step % len(df["time"])
            ]

            force_vector2.scale = df["/forceset/TC_t_test/normalized_tendon_force"].loc[
                step % len(df["time"])
            ]

            # arrow_actor.scale = [
            #     0,
            #     df["/forceset/FL_p_test/normalized_tendon_force"].loc[step],
            #     0,
            # ]

        pl.add_timer_event(
            max_steps=len(df["time"]) * 3, duration=10, callback=callback
        )
        pl.background_color = "black"
        pl.show()
