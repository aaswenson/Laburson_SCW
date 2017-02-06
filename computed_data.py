from geometric_data import *
import material_data as md
from material_data import *

# Pressure Vessel Data
PV_outer_radius = PV_inner_radius + PV_thickness
PV_height_inner = PV_height
PV_height_outer = PV_height + 2*PV_thickness
PV_bottom_inner = -PV_height/2
PV_bottom_outer = PV_bottom_inner - PV_thickness

pyne_mats = md.load_pyne_matlib()
