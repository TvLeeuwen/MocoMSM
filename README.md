# MocoMSM
## Dependencies

### Install opensim
`conda install -c opensim-org opensim`

### Pip dependencies
`pip install pandas numpy pymatreader plotly lxml streamlit`

## Input
### Model
Run Moco to predict Emu gait based on Pacha van Bijleveld's Emu model
`Dromaius_model_v4_intermed.osim`

## Modules
Run individual methods by calling python -m 
(e.g. `python -m src.moco_track_inverse_dynamics -h`)

### generate_gait
Predicts Emu gait from the model alone. Uses a Moco guess to initiate movement
and optimizes for metabolic cost.

### generate_kinematics_sto
Generate a .sto file that extracts kinematic states only from the predicted gait solution.

### generate_moco_track
Track kinematic states and run inverse kinematics using Moco.Track

### visualize
Visualize a .sto file

