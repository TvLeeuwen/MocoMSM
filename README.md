# MocoMSM
## Dependencies

### Dedicated OpenSim virtual environment - Python 3.10
Assuming the use of Anaconda, create a dedicated conda env that runs Python 3.10
`conda create -n envMoco python=3.10`
Note that envMoco can replaced by any other prefered name.

### Install opensim
`conda install -c opensim-org opensim`

### Pip dependencies
`pip install pandas numpy pymatreader plotly lxml streamlit`

## Input
### Gait prediction
Run Moco Emu to predict Emu gait based on Pacha van Bijlert's Emu model
`Dromaius_model_v4_intermed.osim`

### Motion Tracking - example
Run Moco Track on Tom Wolf's Guinea Fowl model,
adapted based on [PennState's Cox Guinea Fowl model](doi: https://doi.org/10.1093/iob/obz022),
and Kavya Katugam-Dechene kinematic data.
Select the example model file `GuineaFowl_lumpmodel_new_2D_weldjoint_TvL.osim` 
and kinematic data file `Loaded_Toes.mat` for the `app/example` directory

## Moco app
Run the Moco track app using `streamlit run moco_app.py`.
Select or drag and drop the model / kinematics you want to run track.

## OR

## Run modules
Run individual methods by calling python -m. 
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


<sub>This repo is by no means a finished project and is therefore prone to bugs and errors.
In case you happen to run into any problems you are welcom to open an issue,
but there is no garanty that these will be addressed within a reasonable timespan.</sub>
