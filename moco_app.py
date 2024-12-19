# Imports ---------------------------------------------------------------------
import os
import streamlit as st

from app.widgets.io import setup_paths, setup_sidebar, osim_uploader, mat_uploader
from app.widgets.functions import run_moco, force_vector_extraction
from app.widgets.visuals import visual_compare_timeseries, visual_force_vector_gif


# test
import pandas as pd
import matplotlib as plt
from pathlib import Path
import pyvista as pv
import numpy as np
from src.sto_generator import read_input
import multiprocessing
import time


def test_gif():
    df, _ = read_input(st.session_state.moco_solution_path)
    current = pd.read_json(os.path.join(st.session_state.output_path,f"{Path(st.session_state.moco_solution_path).stem}_current.json"), orient='records', lines=True)
    previous = pd.read_json(os.path.join(st.session_state.output_path,f"{Path(st.session_state.moco_solution_path).stem}_previous.json"), orient='records', lines=True)
    force_vectors = pd.read_json(st.session_state.force_vectors_path, orient='records', lines=True)


    # Initiate plotter
    pl = pv.Plotter(off_screen=False)
    pl.view_xy()
    pl.camera.zoom(1)
    pl.background_color = "black"
    pl.add_axes(interactive=True)

    muscle_names = list(current.keys())
    colors = plt.cm.gist_rainbow(np.linspace(0, 1, len(muscle_names)))

    i=0
    o = {}
    p = {}
    force_vector_actor = {}
    for muscle, color in zip(muscle_names, colors):
        print(muscle)
        rgb_color = color[:3]

        pl.add_mesh(
            pv.PolyData([0,0,0]),
            color='white',
            point_size=30,
            render_points_as_spheres=True,
        )
        o[muscle] = pl.add_mesh(
            pv.PolyData(current[muscle][i]),
            # color=rgb_color,
            color="blue",
            point_size=20,
            render_points_as_spheres=True,
        )
        p[muscle] = pl.add_mesh(
            pv.PolyData(previous[muscle][i]),
            color=rgb_color,
            point_size=20,
            render_points_as_spheres=True,
        )
        force_vector_actor[muscle] = pl.add_mesh(
            pv.Arrow(
                start=current[muscle][i],
                direction=force_vectors[muscle][i],
                scale=0.1,
            ),
            color=rgb_color,
        )

    pl.open_gif(os.path.join(st.session_state.output_path, "test.gif"))
    # Generate steps and animation behaviour
    for step, force in enumerate(df["/forceset/FL_p_test/normalized_tendon_force"]):
        if step % 5 == 0:
            print(f"Generating gif: {step} / {len(df['time'])}", end="\r")
            for muscle in force_vectors:
                if muscle != 'time': 
                    o[muscle].position = current[muscle][step]
                    p[muscle].position = previous[muscle][step]
                    force_vector_actor[muscle].scale = [1,1,1]
                    force_vector_actor[muscle].position = current[muscle][step]
                    force_vector_actor[muscle].orientation = force_vectors[muscle][step]
            pl.write_frame()
    pl.close()

    print("\nGif succesfully generated.")

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

# Validate muscle parameters --------------------------------------------------
if st.session_state.moco_solution_path is not None and os.path.exists(
    st.session_state.moco_solution_path
):
    st.subheader("Validate")

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


if st.button("Generate test"):


    process = multiprocessing.Process(
        target=test_gif,
        args=(),
    )
    process.start()
    with st.spinner("Generating GIF..."):
        while process.is_alive():
            time.sleep(0.1)
    process.join()
    # mesh = pv.read(os.path.join(mesh_path))
    # df, _ = read_input(solution_path)

