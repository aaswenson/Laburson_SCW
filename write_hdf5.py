from pyne.material import Material, MaterialLibrary, MultiMaterial, mats_latex_table
from pyne.nucname import  name
import os
from material_data import material_dict

matlib = MaterialLibrary()
matlib.from_hdf5('/home/alex/.local/lib/python2.7/site-packages/pyne-0.5.0rc1-py2.7.egg/pyne/nuc_data.h5',datapath="/material_library/materials",nucpath="/material_library/nucid")
new_matlib = MaterialLibrary()

for material in material_dict.keys():
    if material != 'void':
        hdf5_mat = matlib[material]
        hdf5_mat = hdf5_mat.expand_elements()
        hdf5_mat.metadata['name'] = material
        new_matlib[material] = hdf5_mat

new_matlib.write_hdf5('SCW_materials.h5')
