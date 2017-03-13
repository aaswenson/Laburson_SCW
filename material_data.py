from pyne.material import MaterialLibrary, Material


def load_pyne_matlib():
    """Load the hdf5 material library.

    This function loads the pre-built hdf5 file with all structural materials
    found in UWNR.

    Arguments: None

    Returns: PyNE material library with structural materials + void material.
    """
    material_lib = MaterialLibrary()
    material_lib.from_json('SCW_materials.json')
    void = Material({'':0},0)
    void.metadata['density'] = 0
    void.metadata['name'] = 'void'
    material_lib['void'] = void

    return material_lib

material_dict =      { "Steel, Stainless 304"             :{'mat_num':80000, 'mt':''},
                       "Water, Liquid"                    :{'mat_num':1, 'mt':'lwtr.20t'},
                       "Carbon, Graphite (reactor grade)" :{'mat_num':2, 'mt':'grph.20t'}, 
                       "Boron Carbide"                    :{'mat_num':3, 'mt':''},
                       "Boral (65% Al-35% B4C)"           :{'mat_num':4, 'mt':''},
                       "Concrete, Portland"               :{'mat_num':90000,   'mt':''},
                       "void"                             :{'mat_num':0,     'mt':''},
                      }

# some nominal densities for homogenous fuel compositions
# from Duderstadt and Hamilton
rho_UO2 = 10
rho_H2O = 1

# from PyNE
rho_SS = 8

