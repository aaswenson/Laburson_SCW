from pyne.material import MaterialLibrary, Material


def load_pyne_matlib():
    """Load the hdf5 material library.

    This function loads the pre-built hdf5 file with all structural materials
    found in UWNR.

    Arguments: None

    Returns: PyNE material library with structural materials + void material.
    """
    material_lib = MaterialLibrary()
    material_lib.from_hdf5('SCW_materials.h5')
    void = Material({'':0},0)
    void.metadata['density'] = 0
    void.metadata['name'] = 'void'
    material_lib['void'] = void

    return material_lib

material_dict =      { "Steel, Stainless 304"             :{'mat_num':80000, 'mt':''},
                       "Water, Liquid"                    :{'mat_num':1, 'mt':'lwtr.20t'},
                       "Carbon, Graphite (reactor grade)" :{'mat_num':1, 'mt':'grph.20t'}, 
                       "Boron Carbide"                    :{'mat_num':1, 'mt':''},
                       "Boral (65% Al-35% B4C)"           :{'mat_num':1, 'mt':''},
                       "Concrete, Portland"               :{'mat_num':90000,   'mt':''},
                       "void"                             :{'mat_num':0,     'mt':''},
                      }


