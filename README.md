# MocoMSM
## Dependencies

### Install opensim
`conda install -c opensim-org opensim`

### Pip depen
`pip install pandas numpy pymatreader plotly lxml`

## Input
### Model
Run Moco to predict Emu gait based on Pacha van Bijlevelt's Emu model
`Dromaius_model_v4_intermed.osim`

## Modules
### generate_gait=False,
Predicts Emu gait from the model alone. Uses a Moco guess to initiate movement
and optimizes for metabolic cost.

### generate_kinematics_sto=True,
Generate a .sto file that extracts kinematic states only from the predicted gait solution.

### generate_moco_track=True,
Track kinematic states and run inverse kinematics using Moco.Track

### visualize=True,
Visualize a .sto file
