from pyne.material import Material, MaterialLibrary, MultiMaterial, mats_latex_table
from pyne.nucname import  name
import os
from material_data import material_dict

matlib = MaterialLibrary()
matlib.from_hdf5('/home/alex/.local/lib/python2.7/site-packages/pyne-0.5.0rc1-py2.7.egg/pyne/nuc_data.h5',datapath="/material_library/materials",nucpath="/material_library/nucid")
new_matlib = MaterialLibrary()

for material in material_dict.keys():
    if material != 'void':
        pyne_obj = matlib[material]
        JSON_mat = pyne_obj.expand_elements()
        JSON_mat.metadata['name'] = material
        new_matlib[material] = JSON_mat

new_matlib.write_json('SCW_materials.json')
