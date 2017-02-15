from geometric_data import *
import material_data as md
from material_data import *

# Pressure Vessel Data
PV_outer_radius = PV_inner_radius + PV_thickness
PV_height_inner = PV_height
PV_height_outer = PV_height + 2*PV_thickness
PV_bottom_inner = -PV_height/2
PV_bottom_outer = PV_bottom_inner - PV_thickness
PV_top_outer = PV_bottom_outer + PV_height_outer

# Core Shroud Data

Thermal_shroud_outer = TC_radius + Core_shroud_th
Upper_shroud_bottom  = Core_bottom_position + Core_height + Flow_offset
Upper_shroud_top     = Upper_shroud_bottom + Core_shroud_th
shroud_extent_z      = Upper_shroud_top + -Core_bottom_position

# Active Core Data
Active_core_top      = Core_bottom_position + Core_height

# Shielding Data
inner_concrete_radius = PV_outer_radius
outer_concrete_radius = PV_outer_radius + shielding_thick
shield_upper_height   = PV_top_outer + containment_water_level
shield_lower_height   = PV_bottom_outer - shielding_thick

# Load Material Library
pyne_mats = md.load_pyne_matlib()
