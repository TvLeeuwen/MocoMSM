import os
import math
import opensim as osim
import numpy as np
import pandas as pd
import pyvista as pv
import matplotlib as plt

from utils.osim_model_parser import parse_model_for_force_vector
from src.sto_generator import read_input

# Load the OpenSim model
osim_file = "./app/output/GuineaFowl_lumpmodel_new_2D_weldjoint_TvL.osim"
sto_file = "./app/output/GuineaFowl_lumpmodel_new_2D_weldjoint_TvL_moco_track_states_solution_success.sto"

model = osim.Model(osim_file)

state = model.initSystem()

# Load the Moco solution
sto_data = osim.TimeSeriesTable(sto_file)

# Extract model coordinate names
model_coordinates = {coord.getName(): coord for coord in model.getCoordinateSet()}

sto_labels = sto_data.getColumnLabels()

sto_to_coord_map = {}
for label in sto_labels:
    if "/value" in label:  # Only process coordinate value labels
        coord_name = label.split("/")[-2]  # Extract coordinate name
        if coord_name in model_coordinates:
            sto_to_coord_map[label] = coord_name


def extract_muscle_lines(model, state, sto_data, sto_to_coord_map):
    force_directions = {"time": []}
    force_origin = {}
    muscles = model.getMuscles()
    for muscle_name in [muscles.get(i).getName() for i in range(muscles.getSize())]:
        force_directions[muscle_name] = []
        force_origin[muscle_name] = []

    # Iterate through time steps in the .sto file
    for time_index in range(sto_data.getNumRows()):
        print(time_index)
        time = sto_data.getIndependentColumn()[time_index]
        force_directions["time"].append(time)

        # Update the model
        for sto_label, coord_name in sto_to_coord_map.items():
            value = sto_data.getDependentColumn(sto_label)[time_index]
            coord = model.updCoordinateSet().get(coord_name)
            coord.setValue(state, math.degrees(value))
        model.realizeDynamics(state)

        # Extract muscle path points
        for i in range(muscles.getSize()):
            muscle = muscles.get(i)
            geom_path = muscle.getGeometryPath()

            point_force_directions = osim.ArrayPointForceDirection()
            geom_path.getPointForceDirections(state, point_force_directions)

            # Last point
            insertion_index = point_force_directions.getSize() - 1

            pfd = point_force_directions.get(insertion_index)
            insertion_in_ground = [
                pfd.frame().findStationLocationInGround(state, pfd.point())[0],
                pfd.frame().findStationLocationInGround(state, pfd.point())[1],
                pfd.frame().findStationLocationInGround(state, pfd.point())[2],
            ]
            print(f"Insertion: {insertion_in_ground}")

            pfd2 = point_force_directions.get(insertion_index - 1)
            previous_in_ground = [
                pfd2.frame().findStationLocationInGround(state, pfd2.point())[0],
                pfd2.frame().findStationLocationInGround(state, pfd2.point())[1],
                pfd2.frame().findStationLocationInGround(state, pfd2.point())[2],
            ]
            print(f"Previous: {previous_in_ground}")

            vector = [
                v1 - v2 for v1, v2 in zip(previous_in_ground, insertion_in_ground)
            ]
            normalized_vector = vector / np.linalg.norm(vector)
            print(f"Normalized: {normalized_vector}")

            prev_in_insertion = pfd2.frame().findStationLocationInAnotherFrame(
                state, pfd2.point(), pfd.frame()
            )
            print(prev_in_insertion)
            changed_vector = pfd2.frame().expressVectorInAnotherFrame(
                state,
                pfd2.direction(),
                pfd.frame(),
            )
            print(normalized_vector, changed_vector)

            force_directions[muscle.getName()].append(
                [
                    math.degrees(normalized_vector[0]),
                    math.degrees(normalized_vector[1]),
                    math.degrees(normalized_vector[2]),
                ]
                # [
                #     math.degrees(pfd.direction()[0]),
                #     math.degrees(pfd.direction()[1]),
                #     math.degrees(pfd.direction()[2]),
                # ]
                # [
                #     math.degrees(transformed_direction[2]),
                #     math.degrees(transformed_direction[0]),
                #     math.degrees(transformed_direction[1]),
                # ]
            )

            if time_index == 0:
                force_origin[muscle.getName()] = [
                    prev_in_insertion.get(0),
                    prev_in_insertion.get(1),
                    prev_in_insertion.get(2),
                ]
            else:
                if force_origin[muscle.getName()] != [
                    prev_in_insertion.get(0),
                    prev_in_insertion.get(1),
                    prev_in_insertion.get(2),
                ]:
                    print("Warning - force vector origin has shifted!")
                    force_origin[muscle.getName()] = [
                        prev_in_insertion.get(0),
                        prev_in_insertion.get(1),
                        prev_in_insertion.get(2),
                    ]

    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(force_directions)

    return df, force_origin


# Call the function
muscle_lines_df, muscle_origin = extract_muscle_lines(
    model,
    state,
    sto_data,
    sto_to_coord_map,
)

# Save to a CSV file
output_path = "muscle_lines.csv"
muscle_lines_df.to_csv(output_path, index=False)
print(f"Muscle lines saved to {output_path}")


# visualize
def generate_force_vector_gif(
    osim_file,
    mesh_path,
    solution_path,
    df_line_of_action,
    muscle_origin,
    gif_path,
):
    print("Time for gif")
    mesh = pv.read(os.path.join(mesh_path))
    df, _ = read_input(solution_path)

    # Initiate plotter
    pl = pv.Plotter(off_screen=False)
    pl.view_xy()
    pl.camera.zoom(2.5)
    pl.background_color = "black"
    pl.add_axes(interactive=True)

    # Add actors - mesh
    actor = pl.add_mesh(mesh, color="white")

    # and vectors
    muscle_vector_data = parse_model_for_force_vector(osim_file, solution_path)
    muscle_names = list(muscle_vector_data.keys())
    colors = plt.cm.gist_rainbow(np.linspace(0, 1, len(muscle_names)))

    force_vectors = {}
    for muscle, color in zip(muscle_vector_data, colors):
        rgb_color = color[:3]

        pl.add_mesh(
            pv.PolyData(muscle_vector_data[muscle]["origin"]),
            color=rgb_color,
            point_size=20,
            render_points_as_spheres=True,
        )
        pl.add_mesh(
            pv.PolyData(muscle_origin[muscle]),
            color="blue",
            point_size=30,
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

    pl.open_gif(gif_path)
    # Generate steps and animation behaviour
    for step, force in enumerate(df["/forceset/FL_p_test/normalized_tendon_force"]):
        print(f"Generating gif: {step} / {len(df['time'])}", end="\r")
        for muscle in muscle_vector_data:
            force_vectors[muscle].scale = force
            # force_vectors[muscle].orientation = [
            #     0,
            #     0,
            #     math.degrees(
            #         df_line_of_action[muscle].loc[
            #             step % len(df["time"])
            #         ]
            #     ),
            # ]
            force_vectors[muscle].orientation = df_line_of_action[muscle].loc[
                step % len(df["time"])
            ]
            force_vectors[muscle].position = muscle_vector_data[muscle]["origin"]
        pl.write_frame()
    pl.close()

    print("\nGif succesfully generated.")


mesh_file = "./app/example/Geometry/tmet.vtp"

generate_force_vector_gif(
    osim_file,
    mesh_file,
    sto_file,
    muscle_lines_df,
    muscle_origin,
    "vectors.gif",
)
