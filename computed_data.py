from geometric_data import *
import material_data as md
from material_data import *

# Pressure Vessel Data
PV_outer_radius = PV_inner_radius + PV_thickness
PV_top_inner = PV_height/2
PV_top_outer = PV_height/2 + PV_thickness
PV_bottom_inner = -PV_height/2
PV_bottom_outer = -(PV_height/2 + PV_thickness)

# Load material library for all structural materials
pyne_mats = md.load_pyne_matlib()
