import write_card as wc
import computed_data as cd
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
         'surfs'    : [([-601, 602],[-603, 602])],
         'material' : 'Steel, Stainless 304',
         'imp'      : 1
        }])
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
         'surfs'    : [([-803, 801], [-801.2, 601.2, -601.1], -602,
             [-601.1,-802.3, 602.3], [-601.1, 601.3, 603.1, -602.3], [801, -805], [-601.1, 802.3, -801.3])],
         'material' : 'Water, Liquid',
         'imp'      : 1
        }])

    [core_shroud_cell, core_shroud_surf] = make_core_shroud()

    cell_core_level_temp = Template("""\
${comm_mk}    Core Shroud                 \n${core_shroud}\
${comm_mk}    Core water                  \n${core_water}\
""")
    
    cell_core_level = cell_core_level_temp.substitute(core_shroud = core_shroud_cell,
                                                 core_water  = core_water_cell,
                                                 comm_mk     = wc.comment_mark)

    surf_core_level_temp = Template("""\
${comm_mk}    Core Shroud                  \n${core_shroud}\
""")
    
    surf_core_level = surf_core_level_temp.substitute(core_shroud = core_shroud_surf,
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
         'surfs'    : [([-801.1, 601.1, -801.3, -801.2], [-804, 803, 801.2], [-806, 805, 801.3])],
         'material' : 'Steel, Stainless 304',
         'imp'      : 1
        }])
    pressure_vessel_surf = string.surf([
        {'comment'  : 'Outer_PV',
         'type'     : 'rcc',
         'inputs'   : [0, 0, cd.PV_bottom_outer, 0, 0, cd.PV_height_outer,
                       cd.PV_outer_radius ],
         'number'   : 801},
        {'comment'  : 'Inner_PV',
         'type'     : 'rcc',
         'inputs'   : [0, 0, cd.PV_bottom_inner, 0, 0, cd.PV_height_inner, cd.PV_inner_radius],
         'number'   : 802},
        {'comment'  : 'Inner_dome_sphere',
         'type'     : 'S',
         'inputs'   : [0, 0, cd.PV_top_outer,cd.PV_inner_radius],
         'number'   : 803},
        {'comment'  : 'Outer_dome_sphere',
         'type'     : 'S',
         'inputs'   : [0, 0, cd.PV_top_outer,cd.PV_outer_radius],
         'number'   : 804},
        {'comment'  : 'Inner_dome_sphere',
         'type'     : 'S',
         'inputs'   : [0, 0, cd.PV_bottom_outer,cd.PV_inner_radius],
         'number'   : 805},
        {'comment'  : 'Outer_dome_sphere',
         'type'     : 'S',
         'inputs'   : [0, 0, cd.PV_bottom_outer,cd.PV_outer_radius],
         'number'   : 806}
        ])


    return [pressure_vessel_cell, pressure_vessel_surf]

def make_outside_world():
    """Make outside world cards.

    This function defines the world outside the problem space.

    Arguments: (none)

    Returns: string of the outside world cell card.
    """

    string = mcnp_card()

    outside_world_cell = string.cell(900,[
        {'comment'  : 'Pressure Vessel', 
         'surfs'    : [801, 804, 806],
         'material' : 'void',
         'imp'      : 0
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

def make_SCW():
    """Main level function to write the MCNP input file.

    Arguments: none

    Returns: full MCNP input file string.
    """

    # Write cell and surface cards for each level of geometry.
    [cell_core_level, surf_core_level]   = make_core_level()
    [cell_reactor_lvl, surf_reactor_lvl] = make_pressure_vessel()
    cell_outside_wrld                    = make_outside_world()
    # Write general data cards.
    structural_materials = make_structural_data()
    # Write entire input file.
    input_tmpl = Template("""\
${comm_mk}  -------------------------------  CELL CARD  ------------------------------  ${comm_mk}
${comm_mk}  Core level           \n${core_level_cells}${comm_mk}
${comm_mk}  Reactor level        \n${reactor_level_cells}${comm_mk}
${comm_mk}  Outside World level  \n${outside_world_cells}
${comm_mk}  -----------------------------  SURFACE CARD  -----------------------------  ${comm_mk}
${comm_mk}  Core level           \n${core_level_surfs}${comm_mk}
${comm_mk}  Reactor level        \n${reactor_level_surfaces}
${comm_mk}  -------------------------------  DATA CARD  ------------------------------  ${comm_mk}
${comm_mk}  MATERIAL
${comm_mk}    General materials  \n${general_materials}${comm_mk}
${comm_mk}
${comm_mk}  ------------------------------  End of file  -----------------------------  ${comm_mk}
""")

    input_str = input_tmpl.substitute(core_level_cells    = cell_core_level,
                                      core_level_surfs    = surf_core_level,
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
    ifile = open("scw_{0}by{1}.i".format(pin_resolution['radial_division'],
                                          pin_resolution['axial_division']), 'w')
    ifile.write(make_SCW())
    ifile.close()
    print("Input file is successfully generated as 'scw_{0}by{1}.i'".format(
        pin_resolution['radial_division'],
        pin_resolution['axial_division']))
