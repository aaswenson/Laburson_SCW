axial_zones = 3
# Fuel pin dimensions 
pins = {'U': {
    'pitch': 1.2,
    'PD': 1.25,
    'clad_th': 0.06
                   },
    'M': {
        'pitch': 1.2,
        'PD': 1.25,
        'clad_th': 0.06
                },   
    'CR': {
        'meat_radius': 0.55,
        'guide_tube_th': 0.01,
        'pitch' : 1.2
          }
        }

assembly_pitch = 9

master_pins = {'U' : 10,
               'M' : 20,
               'CR' : 30
              }

# Pressure Vessel Data
PV_thickness    = 50
PV_height       = 600

Core_height     = 300
TC_radius       = 100  # Thermal core region radius
FC_rad_thick    = 75  # Fast core region radius
GR_rad_thick    = 50   # Graphite reflector thickness
Core_shroud_th  = 1    # Thickness of the core shroud

# shielding dimensions

shielding_thick = 300
containment_water_level = 1000

# geometric offsets
Core_bottom_position = -150
Flow_offset          = 50    # Room at top of core for flow to develop into outlet pipe
lattice_offset = 0.1

# miscellaneous 
bundle_radius = 1000 # large radius sphere for fuel bundles.
