from geometric_data import *
import material_data as md
from material_data import *

def import_core_map():

    map_file = open('core_map.txt')
    rows = []
    for row in map_file:
        row = row.replace(' ', '')
        row = row.replace('\n', '')
        rows.append(list(row))
    return rows


def get_master_bundles(core_map):
    """Get the master bundles to be replicated.

    Eventually this function will be converted to work with pins.1
    """
    master_bundles = {}
    bundle_map = {}
    for row, bundles in enumerate(core_map):
        for col, bundle in enumerate(bundles):
            bundle_map[(row, col)] = bundle
            if bundle not in master_bundles.keys():
                master_bundles[bundle] = (row, col)

    return master_bundles, bundle_map

def get_density(loc):
    """Calculate density of water as function of axial position in the core.
    """
    return 0.9987
# import core map, get master bundle map
core_map = import_core_map()
[master_bundles, bundle_map] = get_master_bundles(core_map)

# Fuel Pin Dimensions
pins['UOX_pin']['meat_radius'] = 0.5 * pins['UOX_pin']['pitch'] /  pins['UOX_pin']['PD'] 
pins['UOX_pin']['clad_radius'] = pins['UOX_pin']['meat_radius'] + pins['UOX_pin']['clad_th']

pins['MOX_pin']['meat_radius'] = 0.5 * pins['MOX_pin']['pitch'] / pins['MOX_pin']['PD']
pins['MOX_pin']['clad_radius'] = pins['MOX_pin']['meat_radius'] + pins['MOX_pin']['clad_th']

pins['CR']['clad_radius'] = pins['CR']['meat_radius'] + pins['CR']['guide_tube_th']

# Core Shroud Data
Thermal_shroud_outer = TC_radius + Core_shroud_th
FC_radius = Thermal_shroud_outer + FC_rad_thick
GR_radius = FC_radius + GR_rad_thick
Upper_shroud_bottom = Core_bottom_position + Core_height + Flow_offset
Upper_shroud_top = Upper_shroud_bottom + Core_shroud_th
shroud_extent_z = Upper_shroud_top + -Core_bottom_position

# Active Core Data
Active_core_top = Core_bottom_position + Core_height

# Pressure Vessel Data
PV_inner_radius = GR_radius
PV_outer_radius = PV_inner_radius + PV_thickness
PV_height_inner = PV_height
PV_height_outer = PV_height + 2 * PV_thickness
PV_bottom_inner = -PV_height / 2
PV_bottom_outer = PV_bottom_inner - PV_thickness
PV_top_outer = PV_bottom_outer + PV_height_outer

# Shielding Data
inner_concrete_radius = PV_outer_radius
outer_concrete_radius = PV_outer_radius + shielding_thick
shield_upper_height = PV_top_outer + containment_water_level
shield_lower_height = PV_bottom_outer - shielding_thick


# Load Material Library
pyne_mats = md.load_pyne_matlib()

mfrac_OinUO2 = 0.11856
mfrac_OinPuO2 = 0.11769
mfrac_OinAmO2 = 0.11636
mfrac_OinNpO2 = 0.11896
