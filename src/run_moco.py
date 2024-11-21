"""
Run full MSM Moco.track optim workflow
"""

# Imports ---------------------------------------------------------------------
import os
from pathlib import Path

from src.moco_emu import moco_predict_kinematics
from src.sto_generator import generate_sto
from src.moco_track_kinematics import moco_track_states
from src.sto_visualizer import visualize_sto

from utils.md_logger import log_md
try:
    from utils.get_paths import model_file
except ImportError:
    model_file = None
try:
    from utils.get_paths import md_log_file
except ImportError:
    md_log_file = None


# Main ------------------------------------------------------------------------
@log_md(md_log_file)
def run_moco_modules(
    model_file,
    filter_params,
    generate_gait=False,
    generate_kinematics_sto=False,
    generate_moco_track=False,
    visualize=False,
):

    if generate_gait:
        # generate Pasha's gait prediction (Python version)
        gait_prediction_file = moco_predict_kinematics(model_file)
    else:
        gait_prediction_file = Path(f"{model_file.stem}_predicted_gait_success.sto")

    if generate_kinematics_sto:
        # Filter states of interest (kinematics) from the gait prediction .sto
        track_states_file = generate_sto(
            gait_prediction_file,
            filter_params,
            visualize=visualize,
        )
    else:
        track_states_file = Path(
            f"{model_file.stem}_predicted_gait_success_moco_track_states.sto"
        )

    if generate_moco_track:
        # Run filtered states through Moco.track optimization to generate inverse dynamics
        tracked_states_solution_file = moco_track_states(
            model_file,
            track_states_file,
            filter_params,
        )
    else:
        tracked_states_solution_file = Path(
            f"{model_file.stem}_predicted_gait_success_moco_track_states_solution.sto"
        )

    if visualize:
        # visualizer
        visualize_sto(
            tracked_states_solution_file,
            filter_params,
        )


if __name__ == "__main__":
    model_file = Path(model_file) if model_file else Path("Dromaius_model_v4_intermed.osim")

    if model_file.parents[0]:
        os.chdir(model_file.parents[0])

    filter_params = {
        "state_filters": ["jointset"],
        "invert_filter": False,
    }
    run_moco_modules(
        model_file,
        filter_params,
        generate_gait=False,
        generate_kinematics_sto=True,
        generate_moco_track=False,
        visualize=False,
    )
