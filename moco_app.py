# Imports ---------------------------------------------------------------------
import os
import math
import numpy as np
import streamlit as st
import pyvista as pv
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.colors as pc
from stpyvista import stpyvista
from pathlib import Path

from utils.io import setup_paths, setup_sidebar, write_to_output
from utils.osim_model_parser import parse_model_for_force_vector
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
if (
    st.session_state.moco_solution_path is not None
    and st.session_state.osim_file is not None
):
    st.subheader("3D Plot")
    if st.button("Plot 3D"):
        mesh = pv.read(os.path.join(st.session_state.example_path, "Geometry/tmet.vtp"))
        # mesh2 = pv.read(os.path.join(st.session_state.example_path, "Geometry/tibia.vtp"))
        df, header = read_input(
            Path(
                os.path.join(
                    st.session_state.output_path, st.session_state.moco_solution_path
                )
            )
        )

        print(
            df["time"].loc[int(len(df["time"]) / 4)],
            math.degrees(
                df["/jointset/ankle/ankle_flexion/value"].loc[int(len(df["time"]) / 4)]
            ),
        )

        muscle_vector_data = parse_model_for_force_vector(
            st.session_state.osim_file, st.session_state.moco_solution_path
        )
        muscle_names = list(muscle_vector_data.keys())
        colors = plt.cm.gist_rainbow(np.linspace(0, 1, len(muscle_names)))

        force_vectors = {}
        plotter = pv.Plotter(window_size=[400, 400])
        for muscle, color in zip(muscle_vector_data, colors):
            rgb_color = color[:3]

            plotter.add_mesh(
                pv.PolyData(muscle_vector_data[muscle]["origin"]),
                color=rgb_color,
                point_size=20,
                render_points_as_spheres=True,
            )
            force_vectors[muscle] = plotter.add_mesh(
                pv.Arrow(
                    start=muscle_vector_data[muscle]["origin"],
                    direction=[
                        0,
                        math.degrees(
                            df["/jointset/ankle/ankle_flexion/value"].loc[
                                int(len(df["time"]) / 4)
                            ]
                        ),
                        0,
                    ],
                    scale=0.1,
                ),
                color=rgb_color,
            )
            force_vectors[muscle].orientation = [
                0,
                0,
                math.degrees(
                    df["/jointset/ankle/ankle_flexion/value"].loc[
                        int(len(df["time"]) / 4)
                    ]
                ),
            ]
            force_vectors[muscle].position = muscle_vector_data[muscle]["origin"]

        plotter.add_mesh(mesh, color="white")
        plotter.background_color = "black"

        # plotter.add_mesh(mesh, scalars='my_scalar', cmap='bwr')
        stpyvista(plotter, key="pv_tmet")

    # Animate -----------------------------------------------------------------

    if "is_animating" not in st.session_state:
        st.session_state.is_animating = False

    if st.button("Animate") and not st.session_state.is_animating:
        st.session_state.is_animating = True

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

        # Add muscle - cycle through muscle list - get name, origin and direction from previous path point
        # Get muscle names from .osim
        # Origin = last path point from .osim? - Double check with Julia
        # Directon = vector between origin and second-to-last pathpoint - ask Julia about conditional paths
        # Scale = force magnitude from solution.sto

        muscle_vector_data = parse_model_for_force_vector(
            st.session_state.osim_file, st.session_state.moco_solution_path
        )
        muscle_names = list(muscle_vector_data.keys())
        colors = plt.cm.gist_rainbow(np.linspace(0, 1, len(muscle_names)))

        force_vectors = {}
        for muscle, color in zip(muscle_vector_data, colors):
            rgb_color = color[:3]

            pl.add_mesh(
                pv.PolyData(muscle_vector_data[muscle]["second_to_last_location"]),
                color=rgb_color,
                point_size=20,
                render_points_as_spheres=True,
            )
            pl.add_mesh(
                pv.PolyData(muscle_vector_data[muscle]["origin"]),
                color=rgb_color,
                point_size=20,
                render_points_as_spheres=True,
            )
            force_vectors[muscle] = pl.add_mesh(
                pv.Arrow(
                    start=muscle_vector_data[muscle]["origin"],
                    direction=muscle_vector_data[muscle]["vector_orientation"],
                    scale=0.1,
                ),
                color=rgb_color,
            )

        def callback(step):
            print(step % len(df["time"]))
            for muscle in muscle_vector_data:
                force_vectors[muscle].scale = df[
                    "/forceset/FL_p_test/normalized_tendon_force"
                ].loc[step % len(df["time"])]
                force_vectors[muscle].orientation = [
                    0,
                    0,
                    math.degrees(
                        df["/jointset/ankle/ankle_flexion/value"].loc[
                            step % len(df["time"])
                        ]
                    ),
                ]
                force_vectors[muscle].position = muscle_vector_data[muscle]["origin"]

        pl.add_timer_event(max_steps=len(df["time"]), duration=10, callback=callback)

        pl.view_xy()
        pl.background_color = "black"
        pl.show()

        pl.close()
        st.session_state.is_animating = False

