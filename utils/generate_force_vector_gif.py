import os
import numpy as np
import pandas as pd
import pyvista as pv
import matplotlib.pyplot as plt

from src.sto_generator import read_input
from utils.osim_model_parser import parse_model_for_force_vector


# def generate_force_vector_gif(osim_path, mesh_path, solution_path, gif_path):
#     mesh = pv.read(os.path.join(mesh_path))
#     df, _ = read_input(solution_path)
#
#     # Initiate plotter
#     pl = pv.Plotter(off_screen=False)
#     pl.view_xy()
#     pl.camera.zoom(2.5)
#     pl.background_color = "black"
#
#     # Add actors - mesh
#     actor = pl.add_mesh(mesh, color="white")
#
#     # and vectors
#     muscle_vector_data = parse_model_for_force_vector(osim_path, solution_path)
#     muscle_names = list(muscle_vector_data.keys())
#     colors = plt.cm.gist_rainbow(np.linspace(0, 1, len(muscle_names)))
#
#     force_vectors = {}
#     for muscle, color in zip(muscle_vector_data, colors):
#         rgb_color = color[:3]
#
#         pl.add_mesh(
#             pv.PolyData(muscle_vector_data[muscle]["origin"]),
#             color=rgb_color,
#             point_size=20,
#             render_points_as_spheres=True,
#         )
#         force_vectors[muscle] = pl.add_mesh(
#             pv.Arrow(
#                 start=muscle_vector_data[muscle]["origin"],
#                 direction=muscle_vector_data[muscle]["vector_orientation"],
#                 scale=0.1,
#             ),
#             color=rgb_color,
#         )
#
#     pl.open_gif(gif_path)
#
#     # Generate steps and animation behaviour
#     for step, force in enumerate(df["/forceset/FL_p_test/normalized_tendon_force"]):
#         print(f"Generating gif: {step} / {len(df['time'])}", end="\r")
#         for muscle in muscle_vector_data:
#             force_vectors[muscle].scale = force
#             force_vectors[muscle].orientation = [
#                 0,
#                 0,
#                 math.degrees(
#                     df["/jointset/ankle/ankle_flexion/value"].loc[
#                         step % len(df["time"])
#                     ]
#                 ),
#             ]
#             force_vectors[muscle].position = muscle_vector_data[muscle]["origin"]
#         pl.write_frame()
#     pl.close()
#
#     print("\nGif succesfully generated.")


def generate_vector_gif(
    osim_path,
    mesh_path,
    solution_path,
    force_origins_path,
    force_vectors_path,
    gif_path,
):
    mesh = pv.read(os.path.join(mesh_path))
    df, _ = read_input(solution_path)

    force_origins = pd.read_json(force_origins_path, orient='records', lines=True)
    force_vectors = pd.read_json(force_vectors_path, orient='records', lines=True)

    # Initiate plotter
    pl = pv.Plotter(off_screen=False)
    pl.view_xy()
    pl.camera.zoom(2.5)
    pl.background_color = "black"
    pl.add_axes(interactive=True)

    # Add actors - mesh
    actor = pl.add_mesh(mesh, color="white")


    # and vectors
    muscle_vector_data = parse_model_for_force_vector(osim_path, solution_path)
    muscle_names = list(muscle_vector_data.keys())
    colors = plt.cm.gist_rainbow(np.linspace(0, 1, len(muscle_names)))

    force_vector_actor = {}
    for muscle, color in zip(muscle_vector_data, colors):
        rgb_color = color[:3]

        pl.add_mesh(
            pv.PolyData(muscle_vector_data[muscle]["origin"]),
            color=rgb_color,
            point_size=20,
            render_points_as_spheres=True,
        )
        # pl.add_mesh(
        #     pv.PolyData(force_origins[muscle]),
        #     color="blue",
        #     point_size=30,
        #     render_points_as_spheres=True,
        # )
        force_vector_actor[muscle] = pl.add_mesh(
            pv.Arrow(
                start=muscle_vector_data[muscle]["origin"],
                direction=muscle_vector_data[muscle]["vector_orientation"],
                scale=0.1,
            ),
            color=rgb_color,
        )

    pl.open_gif(gif_path)
    # Generate steps and animation behaviour
    for step, force in enumerate(df["/forceset/FL_p_test/normalized_tendon_force"]):
        print(f"Generating gif: {step} / {len(df['time'])}", end="\r")
        for muscle in muscle_vector_data:
            force_vector_actor[muscle].scale = force
            force_vector_actor[muscle].position = force_origins[muscle][0]
            force_vector_actor[muscle].orientation =force_vectors[muscle][step]
            # force_vector_actor[muscle].position = muscle_vector_data[muscle]["origin"]
        pl.write_frame()
    pl.close()

    print("\nGif succesfully generated.")


# mesh_file = "./app/example/Geometry/tmet.vtp"

# generate_force_vector_gif(
#     osim_path,
#     mesh_file,
#     sto_file,
#     muscle_lines_df,
#     force_origins,
#     "vectors.gif",
# )
