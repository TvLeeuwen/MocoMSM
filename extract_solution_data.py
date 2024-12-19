# Imports ---------------------------------------------------------------------
import opensim as osim

model = osim.Model("./app/output/GuineaFowl_lumpmodel_new_2D_weldjoint_TvL.osim")
study = osim.MocoStudy()
problem = study.updProblem()
problem.setModel(model)

model.finalizeFromProperties()
model.initSystem()

sto_path = "./app/output/GuineaFowl_lumpmodel_new_2D_weldjoint_TvL_moco_track_states_solution_success.sto"
trajectory = osim.MocoTrajectory(sto_path)

trajectory.generateControlsFromModelControllers(model)

for i in range(0, model.getStateVariableNames().getSize()):
    print(model.getStateVariableNames().get(i))

print([state for state in trajectory.getStateNames()])

controls_table=trajectory.exportToControlsTable()
# print(controls_table)

fiber_combined_table = study.analyze(trajectory, [r".*fiber_length"])

# print(fiber_combined_table)
