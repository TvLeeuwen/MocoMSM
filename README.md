# MocoMSM
## Install dependencies

### Instal MocoMSM virtual environment
Assuming Anaconda, run 

    `python install_envMocoMSM.py`

## Activate MocoMSM

    `conda activate envMocoMSM`

## Moco app
Run the Moco track app using 

    `streamlit run moco_app.py`.

Select or drag and drop the model / kinematics you want to run track.

## OR run modules individually

## Input
### Gait prediction
Run Pacha van Bijlert's [Emu model](https://doi.org/10.1126/sciadv.ado0936),
a major inspiration for this project, to run the Python version of his gait prediction. 
Download the publication's SimTK link.


Copy the `Dromaius_model_v4_intermed.osim` model to a location 
where you wish to run the analysis, and call 

    `python -m src.moco_emu -m /Path/to/Dromaius_model_v4_intermed.osim`

call

    `python -m src.moco_emu -h`

for help.


### Motion Tracking - example
Run 

    `python -m src.moco_track_kinematics -h`

on Tom Wolf's Guinea Fowl model, adapted based on 
[PennState's Cox Guinea Fowl model](doi: https://doi.org/10.1093/iob/obz022),
and Kavya Katugam-Dechene kinematic data.

Copy the `app/example` folder to a location where you wish to run the analysis, and 
Generate a .sto kinematics file for the track analysis based on the example model file
`GuineaFowl_lumpmodel_new_2D_weldjoint_TvL.osim` and kinematic data file `Loaded_Toes.mat`
by calling


    `python -m src.generate_sto -i=/Path/to/Loaded_Toes.mat -m=(/Path/to/)GuineaFowl_lumpmodel_new_2D_weldjoint_TvL`

using the `-m` and `-s` flags, respectively.

## Modules

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
