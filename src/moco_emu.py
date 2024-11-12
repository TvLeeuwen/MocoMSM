"""
kjgasjh
"""
# Imports ---------------------------------------------------------------------
import os, sys
import argparse
from pathlib import Path
import opensim as osim
import numpy as np
import math

from md_logger import log_md
try:
    from get_md_log_file import md_log_file
except ImportError:
    md_log_file = None


# Parse args ------------------------------------------------------------------
def parse_arguments():
    """
    Parse CLI arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate an initial mesh for mmg based mesh adaptation",
        add_help=False,
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help='Use switches followed by "=" to use CLI file autocomplete, example "-i="',
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        help="Path to input .osim model",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Filename for output .sto file",
    )
    return parser.parse_args()


# Main ------------------------------------------------------------------------
@log_md(md_log_file)
def moco_predict_kinematics(
    input_model_file: Path,
    output_file: Path | None = None,
):
    """
    return name of output file
    """

    output_file = Path(input_model_file.stem + "_predicted_gait.sto") if output_file is None else Path(output_file)

    model = osim.Model(str(input_model_file))
    model.setName(input_model_file.stem)

    study = osim.MocoStudy()
    study.setName(input_model_file.stem)

    problem = study.updProblem()

    # see original model for speed variants
    u = 1
    vel_desired = 0.75 + 0.5 * u
    n_muscles = model.getMuscles().getSize()
    slow_twitch_ratio = 0.5
    specific_tension = 3e5

    metabolics = osim.Bhargava2004SmoothedMuscleMetabolics()
    metabolics.setName("metabolic_cost")
    metabolics.set_use_smoothing(True)
    metabolics.set_basal_coefficient(0.92)

    for muscle in model.getMuscles():
        metabolics.addMuscle(
            muscle.getName(),
            muscle,
            slow_twitch_ratio,
            specific_tension,
        )

    model.addComponent(metabolics)
    model.finalizeConnections()

    modelProcessor = osim.ModelProcessor(model)
    modelProcessor.append(osim.ModOpTendonComplianceDynamicsModeDGF("implicit"))
    problem.setModelProcessor(modelProcessor)

    model = modelProcessor.process()

    # Goals -------------------------------------------------------------------
    symmetry_goal = osim.MocoPeriodicityGoal("symmetry_goal")
    problem.addGoal(symmetry_goal)

    state = model.initSystem()

    for i in range(0, model.getNumStateVariables()):
        current = model.getStateVariableNames().get(i)

        # Symmetric coordinate values and speeds (except for pelvis_tx)
        if "jointset" in current:
            if "pelvis_tx/value" in current:
                continue
            elif (
                "pelvis_list" in current
                or "pelvis_rotation" in current
                or "pelvis_tz" in current
            ):
                symmetry_goal.addNegatedStatePair(osim.MocoPeriodicityGoalPair(current))
            elif "_r" in current:
                if "inversion" in current or "abduction" in current:
                    symmetry_goal.addNegatedStatePair(
                        osim.MocoPeriodicityGoalPair(
                            current,
                            current.replace("_r", "_l"),
                        )
                    )
                else:
                    symmetry_goal.addStatePair(
                        osim.MocoPeriodicityGoalPair(
                            current,
                            current.replace("_r", "_l"),
                        )
                    )
            elif "_l" in current:
                if "inversion" in current or "abduction" in current:
                    symmetry_goal.addNegatedStatePair(
                        osim.MocoPeriodicityGoalPair(
                            current,
                            current.replace("_l", "_r"),
                        )
                    )
                else:
                    symmetry_goal.addStatePair(
                        osim.MocoPeriodicityGoalPair(
                            current,
                            current.replace("_l", "_r"),
                        )
                    )
        # Symmetric muscle activations and normalized tendon forces (i.e. forceset)
        elif "forceset" in current:
            if "_r" in current and "pelvis_rotation" not in current:
                symmetry_goal.addStatePair(
                    osim.MocoPeriodicityGoalPair(
                        current,
                        current.replace("_r", "_l"),
                    )
                )
            if "_l" in current and "pelvis_list" not in current:
                symmetry_goal.addStatePair(
                    osim.MocoPeriodicityGoalPair(
                        current,
                        current.replace("_l", "_r"),
                    )
                )
    # Symmetric controls
    for control_name in problem.createRep().createControlInfoNames():
        if "_r" in control_name:
            symmetry_goal.addControlPair(
                osim.MocoPeriodicityGoalPair(
                    control_name,
                    control_name.replace("_r", "_l"),
                )
            )
        if "_l" in control_name:
            symmetry_goal.addControlPair(
                osim.MocoPeriodicityGoalPair(
                    control_name,
                    control_name.replace("_l", "_r"),
                )
            )

    # Prescribed average gait speed
    speed_goal = osim.MocoAverageSpeedGoal("speed")
    problem.addGoal(speed_goal)
    speed_goal.set_desired_average_speed(vel_desired)

    # Fatigue
    fatigue_goal = osim.MocoControlGoal("fatigue", 90 / n_muscles)
    problem.addGoal(fatigue_goal)
    fatigue_goal.setExponent(3)
    fatigue_goal.setDivideByDisplacement(True)

    # Coordinate bounds -------------------------------------------------------

    # Values
    pi = math.pi

    pelvis_tilt_val = [-15 * pi / 180, 15 * pi / 180]
    pelvis_tx_val = [0, 5]
    pelvis_ty_val = [0.6, 1]

    hip_flexion_val = [0 * pi / 180, 85 * pi / 180]
    knee_angle_val = [-130 * pi / 180, -10 * pi / 180]
    ankle_angle_val = [0 * pi / 180, 110 * pi / 180]

    # Speeds
    pelvis_tilt_speed = np.array([-5, 5]) / 15
    pelvis_tx_speed = [vel_desired / 2, 2 * vel_desired]
    pelvis_ty_speed = np.array([-2, 2]) / 8

    hip_flexion_speed = [-15, 15]
    knee_angle_speed = [-25, 25]
    ankle_angle_speed = [-20, 20]

    problem.setTimeBounds(0, [0.1, 1])

    # Values
    problem.setStateInfo("/jointset/groundPelvis/pelvis_tilt/value", pelvis_tilt_val)
    problem.setStateInfo("/jointset/groundPelvis/pelvis_tx/value", pelvis_tx_val)
    problem.setStateInfo("/jointset/groundPelvis/pelvis_ty/value", pelvis_ty_val)
    problem.setStateInfo("/jointset/hip_r/hip_flexion_r/value", hip_flexion_val)
    problem.setStateInfo("/jointset/hip_l/hip_flexion_l/value", hip_flexion_val)
    problem.setStateInfo("/jointset/knee_r/knee_angle_r/value", knee_angle_val)
    problem.setStateInfo("/jointset/knee_l/knee_angle_l/value", knee_angle_val)
    problem.setStateInfo("/jointset/ankle_r/ankle_angle_r/value", ankle_angle_val)
    problem.setStateInfo("/jointset/ankle_l/ankle_angle_l/value", ankle_angle_val)

    # Speed
    problem.setStateInfo("/jointset/groundPelvis/pelvis_tilt/speed", pelvis_tilt_speed)
    problem.setStateInfo("/jointset/groundPelvis/pelvis_tx/speed", pelvis_tx_speed)
    problem.setStateInfo("/jointset/groundPelvis/pelvis_ty/speed", pelvis_ty_speed)
    problem.setStateInfo("/jointset/hip_l/hip_flexion_l/speed", hip_flexion_speed)
    problem.setStateInfo("/jointset/hip_r/hip_flexion_r/speed", hip_flexion_speed)
    problem.setStateInfo("/jointset/knee_r/knee_angle_r/speed", knee_angle_speed)
    problem.setStateInfo("/jointset/knee_l/knee_angle_l/speed", knee_angle_speed)
    problem.setStateInfo("/jointset/ankle_r/ankle_angle_r/speed", ankle_angle_speed)
    problem.setStateInfo("/jointset/ankle_l/ankle_angle_l/speed", ankle_angle_speed)

    # Solver
    solver = study.initCasADiSolver()
    nodes = 50
    solver.set_num_mesh_intervals(nodes)
    solver.set_verbosity(2)
    solver.set_optim_solver("ipopt")
    solver.set_optim_convergence_tolerance(1e-3)
    solver.set_optim_constraint_tolerance(1e-4)
    solver.set_optim_max_iterations(3000)

    solver.set_multibody_dynamics_mode("implicit")
    solver.set_minimize_implicit_multibody_accelerations(True)

    solver.set_minimize_implicit_auxiliary_derivatives(True)
    solver.set_implicit_auxiliary_derivatives_weight(
        0.1250 * 1 / n_muscles / vel_desired
    )

    guess = None
    if vel_desired == 1.25:
        # Quasi random guess
        guess = solver.createGuess("bounds")

        time_end = 0.45
        guess.setTime(np.linspace(0, time_end, 101))

        guess.setState(
            "/jointset/groundPelvis/pelvis_tilt/value",
            np.deg2rad(0) * np.ones(101),
        )
        guess.setState(
            "/jointset/groundPelvis/pelvis_tx/value",
            np.linspace(0, time_end * vel_desired, 101),
        )
        guess.setState(
            "/jointset/groundPelvis/pelvis_ty/value",
            0.85 * np.ones(101),
        )
        guess.setState(
            "/jointset/hip_r/hip_flexion_r/value",
            np.deg2rad(65) * np.ones(101),
        )
        guess.setState(
            "/jointset/hip_l/hip_flexion_l/value",
            np.deg2rad(65) * np.ones(101),
        )
        guess.setState(
            "/jointset/knee_r/knee_angle_r/value",
            np.linspace(np.deg2rad(-60), np.deg2rad(-110), 101),
        )
        guess.setState(
            "/jointset/knee_l/knee_angle_l/value",
            np.linspace(np.deg2rad(-95), np.deg2rad(-45), 101),
        )
        guess.setState(
            "/jointset/ankle_r/ankle_angle_r/value",
            np.linspace(np.deg2rad(30), np.deg2rad(35), 101),
        )
        guess.setState(
            "/jointset/ankle_l/ankle_angle_l/value",
            np.linspace(np.deg2rad(70), np.deg2rad(30), 101),
        )
        guess.setState(
            "/jointset/groundPelvis/pelvis_tx/speed",
            vel_desired * np.ones(101),
        )
        guess.write(output_file.stem + "_quasirandom_guess.sto")

    solver.setGuess(guess)

    # Solve -----------------------------------------------------------------------
    gait_predication_solution = study.solve()

    if gait_predication_solution.success() is False:
        output_file = Path(output_file.stem + "_failed.sto")
        gait_predication_solution.unseal()
        gait_predication_solution.write(output_file.stem + "_failed.sto")

        sys.exit(f"-- Gait prediction failed, writing:\n - {output_file}")
    else:
        output_file = Path(output_file.stem + "_success.sto")
        gait_predication_solution.write(str(output_file))
        full_stride = osim.createPeriodicTrajectory(gait_predication_solution)
        full_stride.write(output_file.stem + "_fullstride.sto")

        model.printToXML(input_model_file.stem + "_python.osim")

        print(f"-- Gait prediction successful, writing:\n - {output_file}")

        return output_file


if __name__ == "__main__":

    args = parse_arguments()

    os.chdir(Path(args.model).parents[0])

    model_file = args.model
    output_file = args.output

    moco_predict_kinematics(
        Path(model_file),
        Path(output_file),
    )
