import write_card as wc
import computed_data as cd
import fuel_comp as fc
from string import Template
class mcnp_card():
    """Class to write MCNP cards.

    This class builds cell, surface, and data cards for an MCNP6 model.

    Methods.
        * cell: writes the cell cards.
        * surf: writes the surface cards.
        * data: writes the data cards.
    """

    def cell(self,number,data):
        """Cell writer.
        
        This method writes cell cards for the mcnp model.

        Arguments: number, cell number to define cell.
                   data, required data to write the cell.

        Returns: string of the cell card
        """
        
        card = wc.write_cell_card(number,data)

        return card

    def surf(self,data):
        """Surface writer.

        This method writes the surface cards for the mcnp model.

        Arguments: data, required data to write the surface.

        Returns: string of the surface card
        """

        card = wc.write_surf_card(data)

        return card

    def data(self,category,info):
        """Data writer.

        This method writes the data cards for the mcnp model.

        Arguments: category (string) defines the type of data.
                   data (dict) required data to write the card.
        
        Returns: string of the data card
        """

        card = wc.iterate_data_card(category,info)

        return card
def make_fuel_regions():
    core_map = cd.import_core_map()
    
    fc.make_core_lattice(core_map)

    bundle_surfs, bundle_cells, bundle_data = iterate_bundles(core_map)

    return bundle_surfs, bundle_cells, bundle_data, lattice

def iterate_bundles(core_map):
    """Read through all fuel materials and write surf, cell, and material cards.
    """
    string = mcnp_card()

    
    bundle_surfs = string.surf([
        {'comment' : 'Bundle_rpp',
         'type'    : 'SO',
         'inputs'  : [cd.bundle_radius],
         'number'  : 401}
    
    fuel_data = fc.iterate_fuel_manifest()
    pyne_fuels = fc.make_fuel_composition(fuel_data)
    bundle_cell_list = []

    for idx_row, row in enumerate(core_map):
    
        for idx_col, bundle in enumerate(row):
        
            bundle_cell_list, bundle_data += make_bundle(pyne_fuels[bundle], (idx_row, idx_col)) 
            
    return bundle_surfs, bundle_cells, bundle_data



def _make_bundle(mat, pos):
    
    string = mcnp_card()
    univ = 100*pos[0] + pos[1]
    mat_num = univ

    bundle_cells = string.cell([
        {'fuel'     : None,
         'comment'  : '',
         'surfs'    : -401,
         'material' : mat,
         'imp'      : 1, 
         'vol'      : 1500,
         'univ'     : univ}
        ])
    bundle_mats  = wc.write_fuel_data(mat, univ)

    return bundle_cells, bundle_mats
    
def make_active_core():
    """Define the cards to build the active core regions.
    """
    string = mcnp_card()

    [active_core_cell, active_core_data] = iterate_fuel_regions()

    active_core_surf = string.surf([
        {'comment' : 'Upper Active Core',
         'type'    : 'PZ',
         'inputs'  : [cd.Active_core_top],
         'number'  : 501,
         'imp'     : 1
        }])

    return active_core_cell, active_core_surf, active_core_data

def make_core_shroud():
    """Build the core region shroud.

    This function builds the stainless steel shroud seperating the two core
    regions.

    Arguments: none

    Returns: core_shroud_cell (string): MCNP cell card defining shroud.
             core_shroud_surf (string): MCNP surface card to build cells.

    """

    string = mcnp_card()

    core_shroud_cell = string.cell(600,[
        {'comment'  : 'Core_shroud', 
         'surfs'    : [([-802, -602, 603, 604],[601, -604, -602, 605])],
         'material' : 'Steel, Stainless 304',
         'imp'      : 1,
         'vol'      : None,
         'univ'     : None,
         'fill'     : None,
         'lat'      : None
        }])
    core_shroud_surf = string.surf([
        {'comment'  : 'TC_shroud_inner',
         'type'     : 'CZ',
         'inputs'   : [cd.TC_radius],
         'number'   : 601},
        {'comment'  : 'Shroud_upper_extent_top',
         'type'     : 'PZ',
         'inputs'   : [cd.Upper_shroud_top],
         'number'   : 602},
        {'comment'  : 'Shroud_upper_extent_bottom',
         'type'     : 'PZ',
         'inputs'   : [cd.Upper_shroud_bottom],
         'number'   : 603},
        {'comment'  : 'TC_shroud_outer',
         'type'     : 'CZ',
         'inputs'   : [cd.Thermal_shroud_outer],
         'number'   : 604},
        {'comment'  : 'Shroud_bottom',
         'type'     : 'PZ',
         'inputs'   : [cd.Core_bottom_position],
         'number'   : 605}
        ])
    
    return core_shroud_cell, core_shroud_surf

def make_reflector():
    """Build graphite reflector region cards.
    """

    string = mcnp_card()

    reflector_cell = string.cell(650, [
        {'comment'  : 'reflector',
         'surfs'    : [-802, 606, -501, 605],
         'material' : 'Carbon, Graphite (reactor grade)',
         'imp'      : 1,
         'vol'      : None,
         'univ'     : None,
         'fill'     : None,
         'lat'      : None
         }])
    reflector_surfs = string.surf([
        {'comment' : 'Graphite reflector',
         'type'    : 'CZ',
         'inputs'  : [cd.FC_radius],
         'number'  : 606}
        ])
    
    return reflector_cell, reflector_surfs

def make_core_level():
    """Build core level card.
    
    This function writes the surface and cell cards for all core level
    components. Core level components include, core water and the core shroud.

    Arguments: none

    Returns: cell_core_level (template object): template of core level cell card
             surf_core_level (template object): template of core level surface
             card.
    """
    
    string = mcnp_card()

    core_water_cell = string.cell(700,[
        {'comment'  : 'Core Level', 
         'surfs'    : [([-802, 602,-803],[803, -805], [-602, 501, -601], [-603, 501, -802,604],[-605, -802, 804], [-804, -802, -807])],
         'material' : 'Water, Liquid',
         'imp'      : 1,
         'vol'      : None,
         'univ'     : None,
         'fill'     : None,
         'lat'      : None
        }])

    [core_shroud_cell, core_shroud_surf] = make_core_shroud()
    [active_core_cell, active_core_surf, active_core_data] = make_active_core()
    [reflector_cell, reflector_surf] = make_reflector()
    cell_core_level_temp = Template("""\
${comm_mk}    Core Shroud                 \n${core_shroud}\
${comm_mk}    Core Water                  \n${core_water}\
${comm_mk}    Active Core                 \n${active_core}\
${comm_mk}    Reflector Region            \n${reflector}\
""")
    
    cell_core_level = cell_core_level_temp.substitute(core_shroud = core_shroud_cell,
                                                 core_water  = core_water_cell,
                                                 active_core = active_core_cell,
                                                 reflector   = reflector_cell,
                                                 comm_mk     = wc.comment_mark)

    surf_core_level_temp = Template("""\
${comm_mk}    Core Shroud                  \n${core_shroud}\
${comm_mk}                                 \n${active_core}\
${comm_mk}                                 \n${reflector}\
""")
    surf_core_level = surf_core_level_temp.substitute(core_shroud = core_shroud_surf,
                                                      active_core = active_core_surf,
                                                      reflector   = reflector_surf,
                                                      comm_mk     = wc.comment_mark)
    
    return cell_core_level, surf_core_level

def make_pressure_vessel():
    """Make pressure vessel cards.

    This function makes the cell and surface cards to define the pressure
    vessel.

    Arguments: none

    Returns: list of the cell and surface card strings
    """
    string = mcnp_card()

    pressure_vessel_cell = string.cell(800,[
        {'comment'  : 'Pressure Vessel', 
            'surfs'    : [([-801, 802, -803, 804], [-806, 805, 803], [-808, 807, -804])],
         'material' : 'Steel, Stainless 304',
         'imp'      : 1,
         'vol'      : None,
         'univ'     : None,
         'fill'     : None,
         'lat'      : None
        }])
    pressure_vessel_surf = string.surf([
        {'comment'  : 'Outer_PV',
         'type'     : 'CZ',
         'inputs'   : [cd.PV_outer_radius],
         'number'   : 801},
        {'comment'  : 'Inner_PV',
         'type'     : 'CZ',
         'inputs'   : [cd.PV_inner_radius],
         'number'   : 802},
        {'comment'  : 'PV_cyl_upper_extent',
         'type'     : 'PZ',
         'inputs'   : [cd.PV_height_inner],
         'number'   : 803},
        {'comment'  : 'PV_cyl_lower_extent',
         'type'     : 'PZ',
         'inputs'   : [cd.PV_bottom_inner],
         'number'   : 804},
        {'comment'  : 'Inner_dome_sphere',
         'type'     : 'S',
         'inputs'   : [0, 0, cd.PV_height_inner,cd.PV_inner_radius],
         'number'   : 805},
        {'comment'  : 'Outer_dome_sphere',
         'type'     : 'S',
         'inputs'   : [0, 0, cd.PV_height_inner,cd.PV_outer_radius],
         'number'   : 806},
        {'comment'  : 'Inner_dome_sphere',
         'type'     : 'S',
         'inputs'   : [0, 0, cd.PV_bottom_inner,cd.PV_inner_radius],
         'number'   : 807},
        {'comment'  : 'Outer_dome_sphere',
         'type'     : 'S',
         'inputs'   : [0, 0, cd.PV_bottom_inner,cd.PV_outer_radius],
         'number'   : 808}
        ])


    return [pressure_vessel_cell, pressure_vessel_surf]

def make_shielding():
    """Make concrete shielding cards

    This function defines the cards to make concrete reactor shielding.

    Arguments: none

    Returns: sring of the outside world cell, surf card.
    """

    string = mcnp_card()
    
    shielding_cell = string.cell(900,[
        {'comment'  : 'Concrete Shielding',
         'surfs'    : [-900, 801, -902, 903, 806],
         'material' : 'Concrete, Portland',
         'imp'      : 1,
         'vol'      : None,
         'univ'     : None,
         'fill'     : None,
         'lat'      : None
         } ,
        {'comment'  : 'Water Shielding',
         'surfs'    : [([-801, 806, -902, 803],[-801, 808, 903, -804])],
         'material' : 'Water, Liquid',
         'imp'      : 1,
         'vol'      : None,
         'univ'     : None,
         'fill'     : None,
         'lat'      : None
         }])

    shielding_surfs = string.surf([
        {'comment'  : 'Outer_shield_cyl',
         'type'     : 'CZ',
         'inputs'   : [cd.outer_concrete_radius],
         'number'   :  900},
        {'comment'  : 'Inner_shield_cyl',
         'type'     : 'CZ',
         'inputs'   : [cd.inner_concrete_radius],
         'number'   :  901},
        {'comment'  : 'Upper_shield_plane',
         'type'     : 'PZ',
         'inputs'   : [cd.shield_upper_height],
         'number'   :  902},
        {'comment'  : 'Lower_shield_plane',
         'type'     : 'PZ',
         'inputs'   : [cd.shield_lower_height],
         'number'   :  903}
        ])

    return [shielding_cell, shielding_surfs]
    
def make_outside_world():
    """Make outside world cards.

    This function defines the world outside the problem space.

    Arguments: (none)

    Returns: string of the outside world cell card.
    """

    string = mcnp_card()

    outside_world_cell = string.cell(990,[
        {'comment'  : 'Outside World', 
         'surfs'    : [(-903, 902,[900, 903, -902])],
         'material' : 'void',
         'imp'      : 0,
         'vol'      : None,
         'univ'     : None,
         'fill'     : None,
         'lat'      : None
        }])

    return outside_world_cell

def make_structural_data():
    """Make structural data cards.

    This function makes the data cards for the reactor structural material
    
    Arguments: none

    Returns: string of the structural material data card.
    """
    string = mcnp_card()
    
    data_card = string.data('material',cd.material_dict)

    return data_card

def write_material_card():
    """
    """
    
    string = mcnp_card()

    structural_data  = make_structural_data()
    active_fuel_data = make_active_core()[2]
    
    material_card_temp = Template("""\
${comm_mk}    Material Data                 \n${structural_materials}${comm_mk}
${comm_mk}    Fuel Data                     \n${fuel_data}${comm_mk}
""")
    material_card = material_card_temp.substitute(structural_materials = structural_data,
                                                  fuel_data            = active_fuel_data,
                                                  comm_mk              = wc.comment_mark)
    return material_card

def write_data_card():
    """Write the non-material data card.
    """
    mode = ''.join(wc.write_general_data({
                'category' : 'mode',
                'particle' : 'n',
                'comment'  : 'Problem Type'}))
    kcode = ''.join(wc.write_general_data({
                'category' : 'kcode',
                'kcode'    : '5000 1 15 25',
                'ksrc'     : '0 0 0\n         0 -250 0\n        -150 0 -100\n        150 0 0\n        0 150 0\n        -150 0 0\n        0 -150 0\n        150 0 100\n        0 150 100\n        0 0 100\n        -150 0 100',
                'comment'  : 'criticality card'}))

    return mode, kcode

def make_SCW():
    """Main level function to write the MCNP input file.

    Arguments: none

    Returns: full MCNP input file string.
    """

    # Write cell and surface cards for each level of geometry.
    [cell_core_lvl, surf_core_lvl]                        = make_core_level()
    [cell_reactor_lvl, surf_reactor_lvl]                  = make_pressure_vessel()
    [cell_shielding, surf_shielding]                      = make_shielding()
    cell_outside_wrld                                     = make_outside_world()
    # Write general data cards.
    materials_card = write_material_card()
    [mode, kcode]  = write_data_card()
    burnup_card    = wc.make_burnup_card()
    # Write entire input file.
    input_tmpl = Template("""\
${comm_mk}  -------------------------------  CELL CARD  ------------------------------  ${comm_mk}
${comm_mk}  Core level           \n${core_level_cells}${comm_mk}
${comm_mk}  Reactor level        \n${reactor_level_cells}${comm_mk}
${comm_mk}  Shielding            \n${shielding_cells}${comm_mk}
${comm_mk}  Outside World level  \n${outside_world_cells}
${comm_mk}  -----------------------------  SURFACE CARD  -----------------------------  ${comm_mk}
${comm_mk}  Core level           \n${core_level_surfs}${comm_mk}
${comm_mk}  Reactor level        \n${reactor_level_surfaces}${comm_mk}
${comm_mk}  Shielding level      \n${shielding_surfs} 
${comm_mk}  -------------------------------  DATA CARD  ------------------------------  ${comm_mk}
${comm_mk}  Burnup Card
${comm_mk}                       \n${burn_card}${comm_mk}
${comm_mk}  MATERIAL             \n${material_card}${comm_mk}
${comm_mk}  DATA
${comm_mk}    kcode              \n${kcode}
${comm_mk}                       \n${mode}
${comm_mk}
${comm_mk}  ------------------------------  End of file  -----------------------------  ${comm_mk}
""")

    input_str = input_tmpl.substitute(core_level_cells       = cell_core_lvl,
                                      core_level_surfs       = surf_core_lvl,
                                      reactor_level_cells    = cell_reactor_lvl,
                                      shielding_cells        = cell_shielding,
                                      shielding_surfs        = surf_shielding,
                                      outside_world_cells    = cell_outside_wrld,
                                      reactor_level_surfaces = surf_reactor_lvl,
                                      material_card          = materials_card,
                                      burn_card              = burnup_card,
                                      kcode                  = kcode,
                                      mode                   = mode,
                                      comm_mk                = wc.comment_mark)

    return input_str
pin_resolution = {'radial_division' : 1,
                  'axial_division'  : 1}
model_info = '2_region_homog'
# Write input file.
if __name__=="__main__":
    ifile = open("scwr_{0}.i".format(model_info), 'w')
    ifile.write(make_SCW())
    ifile.close()
    print("Input file is successfully generated as 'scw_{0}.i'".format(model_info))
