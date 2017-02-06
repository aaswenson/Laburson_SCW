import write_card as wc
import computed_data as cd
from string import Template
class mcnp_card():
    def cell(self,number,data):
        
        card = wc.write_cell_card(number,data)
        
        return card
    def surf(self,data):

        card = wc.write_surf_card(data)

        return card

    def data(self,category,info):


        card = wc.iterate_data_card(category,info)

        return card

def make_core_shroud():

    string = mcnp_card()

    core_shroud_cell = string.cell(600,
        {'comment'  : 'Core_shroud', 
         'surfs'    : [([-601, 602],[-603, 602])],
         'material' : 'Steel, Stainless 304',
         'imp'      : 1
        })
    core_shroud_surf = string.surf([
        {'comment'  : 'Upper_shroud',
         'type'     : 'rcc',
         'inputs'   : [0, 0, cd.Upper_shroud_bottom, 0, 0, cd.Core_shroud_th, cd.PV_inner_radius],
         'number'   : 601},
        {'comment'  : 'TC_shroud_inner',
         'type'     : 'rcc',
         'inputs'   : [0, 0, cd.Core_bottom_position, 0, 0, cd.shroud_extent_z, cd.TC_radius],
         'number'   : 602},
        {'comment'  : 'TC_shroud_outer',
         'type'     : 'rcc',
         'inputs'   : [0, 0, cd.Core_bottom_position, 0, 0, cd.shroud_extent_z, cd.Thermal_shroud_outer],
         'number'   : 603}])
    
    return core_shroud_cell, core_shroud_surf

def make_core_level():
    
    string = mcnp_card()

    core_level_cell = string.cell(700,
        {'comment'  : 'Core Level', 
         'surfs'    : [(-602, [-802, 601, 603])],
         'material' : 'Water, Liquid',
         'imp'      : 1
        })
    return core_level_cell

def make_pressure_vessel():
    
    string = mcnp_card()

    pressure_vessel_cell = string.cell(800,
        {'comment'  : 'Pressure Vessel', 
         'surfs'    : [-801, 802],
         'material' : 'Steel, Stainless 304',
         'imp'      : 1
        })
    pressure_vessel_surf = string.surf([
        {'comment'  : 'outer_PV',
         'type'     : 'rcc',
         'inputs'   : [0, 0, cd.PV_bottom_outer, 0, 0, cd.PV_height_outer,
                       cd.PV_outer_radius ],
         'number'   : 801},
        {'comment'  : 'inner_PV',
         'type'     : 'rcc',
         'inputs'   : [0, 0, cd.PV_bottom_inner, 0, 0, cd.PV_height_inner, cd.PV_inner_radius],
         'number'   : 802}])

    return [pressure_vessel_cell, pressure_vessel_surf]

def make_outside_world():

    string = mcnp_card()

    outside_world_cell = string.cell(900,
        {'comment'  : 'Pressure Vessel', 
         'surfs'    : [801],
         'material' : 'void',
         'imp'      : 0
        })
    return outside_world_cell

def make_structural_data():
    string = mcnp_card()
    
    data_card = string.data('material',cd.material_dict)

    return data_card

def make_SCW():

    # Write cell and surface cards for each level of geometry.
    [cell_core_shroud, surf_core_shroud] = make_core_shroud()
    cell_core_lvl                        = make_core_level()
    [cell_reactor_lvl, surf_reactor_lvl] = make_pressure_vessel()
    cell_outside_wrld                    = make_outside_world()
    # Write general data cards.
    structural_materials = make_structural_data()
    # Write entire input file.
    input_tmpl = Template("""\
${comm_mk}  -------------------------------  CELL CARD  ------------------------------  ${comm_mk}
${comm_mk}  Core shroud          \n${core_shroud_cells}${comm_mk}
${comm_mk}  Core level           \n${core_level_cells}${comm_mk}
${comm_mk}  Reactor level        \n${reactor_level_cells}${comm_mk}
${comm_mk}  Outside World level  \n${outside_world_cells}
${comm_mk}  -----------------------------  SURFACE CARD  -----------------------------  ${comm_mk}
${comm_mk}  Core shroud          \n${core_shroud_surfs}${comm_mk}
${comm_mk}  Reactor level        \n${reactor_level_surfaces}
${comm_mk}  -------------------------------  DATA CARD  ------------------------------  ${comm_mk}
${comm_mk}  MATERIAL
${comm_mk}    General materials  \n${general_materials}${comm_mk}
${comm_mk}
${comm_mk}  ------------------------------  End of file  -----------------------------  ${comm_mk}
""")

    input_str = input_tmpl.substitute(core_shroud_cells   = cell_core_shroud,
                                      core_shroud_surfs   = surf_core_shroud,
                                      core_level_cells    = cell_core_lvl,
                                      reactor_level_cells = cell_reactor_lvl,
                                      outside_world_cells = cell_outside_wrld,
                                      reactor_level_surfaces = surf_reactor_lvl,
                                      general_materials = structural_materials,
                                      comm_mk = wc.comment_mark)

    return input_str
pin_resolution = {'radial_division' : 3,
                  'axial_division'  : 6}
# Write input file.
if __name__=="__main__":
    ifile = open("pynr_{0}by{1}.i".format(pin_resolution['radial_division'],
                                          pin_resolution['axial_division']), 'w')
    ifile.write(make_SCW())
    ifile.close()
    print("Input file is successfully generated as 'pynr_{0}by{1}.i'".format(
        pin_resolution['radial_division'],
        pin_resolution['axial_division']))
