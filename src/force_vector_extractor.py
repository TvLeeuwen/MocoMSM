"""Extract muscle force vector and orientation"""

# Imports ---------------------------------------------------------------------
import os
import math
import numpy as np
import pandas as pd
import opensim as osim
from pathlib import Path


# Defs ------------------------------------------------------------------------
def extract_force_vectors(osim_path, sto_path, output_path):
    # Load input
    model = osim.Model(osim_path)
    sto_data = osim.TimeSeriesTable(sto_path)

    # Initiate output
    force_origins = {}
    force_directions = {"time": []}

    muscles = model.getMuscles()
    for muscle_name in [muscles.get(i).getName() for i in range(muscles.getSize())]:
        force_origins[muscle_name] = []
        force_directions[muscle_name] = []

    # Initiate model state
    state = model.initSystem()

    # Build a coordinate map to track and update model states through time
    model_coordinates = {coord.getName(): coord for coord in model.getCoordinateSet()}
    sto_to_coord_map = {}
    for label in sto_data.getColumnLabels():
        if "/value" in label:
            coord_name = label.split("/")[-2]
            if coord_name in model_coordinates:
                sto_to_coord_map[label] = coord_name

    # Iterate through time steps in the .sto file
    for time_index in range(sto_data.getNumRows()):
        time = sto_data.getIndependentColumn()[time_index]
        force_directions["time"].append(time)

        # Update model states
        for sto_label, coord_name in sto_to_coord_map.items():
            value = sto_data.getDependentColumn(sto_label)[time_index]
            coord = model.updCoordinateSet().get(coord_name)
            coord.setValue(state, math.degrees(value))
        model.realizeDynamics(state)

        # Extract muscle path points in current state
        for i in range(muscles.getSize()):
            muscle = muscles.get(i)
            geom_path = muscle.getGeometryPath()

            point_force_directions = osim.ArrayPointForceDirection()
            geom_path.getPointForceDirections(state, point_force_directions)

            # Last point = point of muscle insertion
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

            insertion_vector = [
                v1 - v2 for v1, v2 in zip(previous_in_ground, insertion_in_ground)
            ]
            normalized_vector = insertion_vector / np.linalg.norm(insertion_vector)
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

            force_origins[muscle.getName()].append(
                [
                    prev_in_insertion.get(0),
                    prev_in_insertion.get(1),
                    prev_in_insertion.get(2),
                ]
            )

    # Save to a CSV file
    force_origin_paths = os.path.join(
        output_path, f"{Path(sto_path).stem}_muscle_origins.json"
    )
    force_vector_paths = os.path.join(
        output_path, f"{Path(sto_path).stem}_muscle_vectors.json"
    )

    pd.DataFrame(force_origins).to_json(
        force_origin_paths, orient="records", lines=True
    )
    pd.DataFrame(force_directions).to_json(
        force_vector_paths, orient="records", lines=True
    )

    return force_origin_paths, force_vector_paths
