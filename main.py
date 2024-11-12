"""
Run Moco
"""

# Imports ---------------------------------------------------------------------
import os
from pathlib import Path
from src.run_moco import run_moco_modules

try:
    from utils.get_paths import model_file
except ImportError:
    model_file = None

# Parameters ------------------------------------------------------------------
model_file = Path(model_file) if model_file else Path("Dromaius_model_v4_intermed.osim")

if model_file.parents[0]:
    os.chdir(model_file.parents[0])

filter_params = {
    "state_filters": ["jointset"],
    "invert_filter": False,
}

# Main ------------------------------------------------------------------------
run_moco_modules(
    model_file,
    filter_params,
    generate_gait=False,
    generate_kinematics_sto=True,
    generate_moco_track=False,
    visualize=False,
)
