import write_card as wc
import computed_data as cd
import material_data as md
import fuel_comp as fc
from assembly_maps import assemblies
from string import Template
import copy


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
        
        card = wc.iterate_cell_cards(number, data)

        return card

    def surf(self,data):
        """Surface writer.

        This method writes the surface cards for the mcnp model.

        Arguments: data, required data to write the surface.

        Returns: string of the surface card
        """

        card = wc.write_surf_card(data)

        return card

    def data(self, category, info):
        """Data writer.

        This method writes the data cards for the mcnp model.

        Arguments: category (string) defines the type of data.
                   data (dict) required data to write the card.
        
        Returns: string of the data card
        """

        card = wc.iterate_data_card(category, info)

        return card

def make_fuel_regions():
    """Create the two core regions that contain fuel.

    This function produces the necessary cards to create the inner and outer
    fuel regions of the MCNP model.

    Args:
        None
    Returns:
        bundle_surfs (str): required surf cards to build core/bundle lattices
        bundle_cells (str): cell and lattice cards to build all fuel assemblies
        bundle_data  (str): data card for cells, material and translation (CRs)
        lattice      (str): core lattice map 
    """
    string = mcnp_card()

    bundle_cells = ''
    bundle_data = ''
    bundle_surfs = make_master_fuel_pin_surf()[0]
    
    
    [bundle_cells, 
     bundle_data, 
     master_bundles, 
     updated_bundle_map] = get_master_bundles(cd.bundle_id_map)
    
    core_map_save = cd.import_core_map()
    core_map = copy.deepcopy(core_map_save)
    
    formatted_core_map, row, col = wc.convert_core_lattice(core_map, master_bundles)
    
    lattice = wc.make_lattice_map(formatted_core_map,
                                  500, 500, 
                                 '-500', row, col)
    lattice  += string.cell(501, [
                {'fuel'     : None,
                 'comment'  : 'Active_core',
                 'surfs'    : [([-501, -601, 605, 606, -607],[-610, 605, 604,
                     -501, 606, -607])],
                 'material' : 'void',
                 'imp'      : 1,
                 'univ'     : None,
                 'fill'     : 500,
                 'vol'      : None,
                 'lat'      : None
                 }])



    return bundle_surfs, bundle_cells, bundle_data, lattice

def get_master_bundles(bundle_location_data):
    """ This function builds master fuel assemblies to be repeated throughout
    the core.
    """
    bundle_cells = ''
    bundle_data = ''
    master_bundles = {}

    # get surfaces to build pins, surface numbers for reference
    surf_nums = make_master_fuel_pin_surf()[1]

    for bundle_coords in sorted(bundle_location_data):
        assembly_id = bundle_location_data[bundle_coords] 
        assembly = assemblies[assembly_id]

        if assembly_id not in master_bundles:
            density = cd.get_density(bundle_coords)
            univ = 100 * bundle_coords[2] + 10 * bundle_coords[0] + bundle_coords[1] 
            cells, data, lattice = make_bundle(assembly_id, univ, density, surf_nums) 
            master_bundles[assembly_id] = univ
            
            bundle_cells += cells + lattice
            bundle_data += data
        
            del bundle_location_data[bundle_coords]
        
    return bundle_cells, bundle_data, master_bundles, bundle_location_data

    
def make_bundle(assembly, univ, density, surf_nums):
    """This function builds the repeated lattice structure required to build a
    fuel assembly with fuel pins.
    """
    cell_data = ''
    lattice = ''
    string = mcnp_card()
    if assembly != 'W':
        
        # get master cells to build pins
        master_cells, master_cell_univ, data = make_master_fuel_pin_cells(assembly,\
                10 * univ, surf_nums, density)
        cell_data += data
        assembly_copy = copy.deepcopy(assemblies[assembly]) 
        formatted_assembly_map, row, col =\
        wc.convert_core_lattice(assembly_copy, master_cell_univ)
        
        lattice += wc.make_lattice_map(formatted_assembly_map,
                                      univ, univ, 
                                     -surf_nums['pitch'], row, col)
        lattice  += string.cell(univ + 1, [
                    {'fuel'     : None,
                     'comment'  : 'Assembly',
                     'surfs'    : surf_nums['bundle'],
                     'material' : 'void',
                     'imp'      : 1,
                     'univ'     : None,
                     'fill'     : univ,
                     'vol'      : None,
                     'lat'      : None
                     }])

        

    else:
        water_cell_data = {'material' : 'Water, Liquid',
                           'mat_num'  : 1,
                           'comment'  : 'Water',
                           'imp'      : 1,
                           'univ'     : univ,
                           'surfs'    : [-surf_nums['W'] ],
                           'vol' : None,
                           'fill' : None,
                           'lat'  : None
                          }
        master_cells = wc.write_cell_card(univ, water_cell_data,
                -density)[0]
        
    return master_cells, cell_data, lattice

def make_master_fuel_pin_surf():
    """Make master surfaces for fuel pins and control rods.
    """
    print 'surf_ran'
    string = mcnp_card()
    
    master_surf_nums = {}
    for pin in cd.pins:
        master_surf_nums[pin] = {}
    
    master_pin_surf = ''
    for pin_type in cd.pins:
        
        # make master surfaces
        master_pin_surf += string.surf([
        {'comment' : 'master_'+pin_type+'_meat',
         'type'    : 'CZ',
         'inputs'  : [cd.pins[pin_type]['meat_radius']],
         'number'  : cd.master_pins[pin_type] + 1},

        {'comment' : 'master_'+pin_type+'clad',
         'type'    : 'CZ',
         'inputs'  : [cd.pins[pin_type]['clad_radius']],
         'number'  : cd.master_pins[pin_type] + 2}
        ])
        # make master surface to define bundles.
        master_pin_surf += string.surf([
        {'comment' : 'bundle rhp',
         'type'    : 'rhp',
         'inputs'  : [0, 0, -150, 0, 0, 300, 9, 0],
         'number'  : 500}
        ])
        
        # make master surface to define pin_cells.
        master_pin_surf += string.surf([
        {'comment' : 'pin rhp',
         'type'    : 'rhp',
         'inputs'  : [0, 0, -150, 0, 0, 300, cd.pins[pin_type]['pitch'], 0],
         'number'  : 502}
        ])
        # make master surface to define water in bundles.
        master_pin_surf += string.surf([
        {'comment' : 'lattice water',
         'type'    : 'SO',
         'inputs'  : [cd.PV_height],    # arbitrarily large number
         'number'  : 2}
        ])

        master_surf_nums[pin_type]['meat'] = cd.master_pins[pin_type] + 1
        master_surf_nums[pin_type]['clad'] = cd.master_pins[pin_type] + 2
        master_surf_nums['pitch'] = 502
        master_surf_nums['bundle'] = 500
        master_surf_nums['W'] = 2
    
    return master_pin_surf, master_surf_nums

def make_master_fuel_pin_cells(assembly_id, univ, surfs, density):
    """Produce master fuel pin cells.
    """
    
    string = mcnp_card()
    assembly = copy.deepcopy(assemblies[assembly_id])
    master_pin_cells = ''
    master_pin_data = ''
    unique_pins = list(set(sum(assembly, [])))
    master_cell_univ = {}

    for pin in unique_pins:
        master_cell_univ[pin] = {}
 
    for idx, pin in enumerate(unique_pins):

        pin_num = univ + 10 * idx
        
        if pin != 'W':

            if pin == 'CR':
                
                master_pin_cells += string.cell(pin_num,[
                    {'comment'  : pin + ' meat',
                     'surfs'    : [-(surfs[pin]['meat']), -501, 602],
                     'material' : 'Boron Carbide',
                     'imp'      : 1,
                     'vol'      : None,
                     'univ'     : pin_num,
                     'fill'     : None,
                     'lat'      : None
                    }])
                master_pin_cells += string.cell(pin_num + 1,[
                    {'comment'  : pin+' clad',
                     'surfs'    : [(surfs[pin]['meat']),-(surfs[pin]['clad']), -501, 602],
                     'material' : 'Steel, Stainless 304',
                     'imp'      : 1,
                     'vol'      : None,
                     'univ'     : pin_num,
                     'fill'     : None,
                     'lat'      : None
                    }])
            else:
                master_pin_cells += string.cell(pin_num, [
                    {'comment'  : pin + ' meat',
                     'fuel'     : 'yes',
                     'surfs'    : [-(surfs[pin]['meat']), -501, 602],
                     'material' : pin,
                     'imp'      : 1,
                     'vol'      : None,
                     'univ'     : pin_num,
                     'fill'     : None,
                     'lat'      : None
                    }])
                

                master_pin_data +=  wc.write_fuel_data(pin, pin_num)

                master_pin_cells += string.cell(pin_num + 1,[
                    {'comment'  : pin+' clad',
                     'surfs'    : [(surfs[pin]['meat']),-(surfs[pin]['clad']), -501, 602],
                     'material' : 'Steel, Stainless 304',
                     'imp'      : 1,
                     'vol'      : None,
                     'univ'     : pin_num,
                     'fill'     : None,
                     'lat'      : None
                    }])
            water_cell_data = {'material' : 'Water, Liquid',
                               'mat_num'  : 1,
                               'comment'  : 'Water',
                               'imp'      : 1,
                               'univ'     : pin_num,
                               'surfs'    : [surfs[pin]['clad'], -surfs['W'] ],
                               'vol' : None,
                               'fill' : None,
                               'lat'  : None
                              }
            master_pin_cells += wc.write_cell_card(pin_num + 2,
                                                   water_cell_data, 
                                                   -density)[0]
            master_cell_univ[pin] = univ 
        
    water_cell_data = {'material' : 'Water, Liquid',
                       'mat_num'  : 1,
                       'comment'  : 'Water',
                       'imp'      : 1,
                       'univ'     : univ + 1,
                       'surfs'    : [-surfs['W'] ],
                       'vol' : None,
                       'fill' : None,
                       'lat'  : None
                      }
    master_pin_cells += wc.write_cell_card(univ + 3, water_cell_data,
            -density)[0]
    master_cell_univ['W'] = univ + 1

    return master_pin_cells, master_cell_univ, master_pin_data



def make_active_core():
    """Define the cards to build the active core regions.
    """
    string = mcnp_card()

    [active_core_surfs, 
     active_core_cells, 
     active_core_data, 
     lattice
     ] = make_fuel_regions()

    active_core_surfs += string.surf([
        {'comment' : 'Upper Active Core',
         'type'    : 'PZ',
         'inputs'  : [cd.Active_core_top],
         'number'  : 501,
         'imp'     : 1
        }])
    
    return active_core_cells, active_core_surfs, active_core_data, lattice

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
         'surfs'    : [([-802, -602, 603, 604, 606, -607],[601, -604, -602, 605,
             606, -607])],
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
         'number'   : 605},
        # planes for core symmetry
        {'comment'  : 'x_symmetry',
         'type'     : 'PY',
         'number'   : '+606',
         'inputs'   : [0]},
        {'comment'  : 'y_symmetry',
         'type'     : 'PX',
         'number'   : '+607',
         'inputs'   : [0]}
        ])
    
    return core_shroud_cell, core_shroud_surf

def make_reflector():
    """Build graphite reflector region cards.
    """

    string = mcnp_card()

    reflector_cell = string.cell(650, [
        {'comment'  : 'reflector',
         'surfs'    : [-802, 610, -501, 605, 606, -607],
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
         'number'  : 610}
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
         'surfs'    : [([-802, 602,-803, 606, -607],[803, -805, 606, -607], [-602,
             501, -601, 606, -607], [-603, 501, -802, 604, 606, -607],[-605, -802,
                 804, 606, -607], [-804, -802, -807, 606, -607])],
         'material' : 'Water, Liquid',
         'imp'      : 1,
         'vol'      : None,
         'univ'     : None,
         'fill'     : None,
         'lat'      : None
        }])

    [core_shroud_cell, core_shroud_surf] = make_core_shroud()
    [active_core_cell, 
     active_core_surf, 
     active_core_data, 
     active_core_lattice] = make_active_core()
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
    
    return cell_core_level, surf_core_level, active_core_lattice, active_core_data

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
            'surfs'    : [([-801, 802, -803, 804, 606, -607], [-806, 805, 803,
                606, -607], [-808, 807, -804, 606, -607])],
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
         'surfs'    : [-900, 801, -902, 903, 806, 606, -607],
         'material' : 'Concrete, Portland',
         'imp'      : 1,
         'vol'      : None,
         'univ'     : None,
         'fill'     : None,
         'lat'      : None
         } ,
        {'comment'  : 'Water Shielding',
         'surfs'    : [([-801, 806, -902, 803, 606, -607],[-801, 808, 903, -804,
             606, -607])],
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
         'surfs'    : [(-606, 607, [900, 903, -902, 606, -607], 902, -903)],
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
    active_fuel_data = make_core_level()[3]
    
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
    [cell_core_lvl, surf_core_lvl, active_core_lattice, active_core_data] = make_core_level()
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
${comm_mk}  Core lattice         \n${core_lattice}${comm_mk}
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
                                      core_lattice           = active_core_lattice,
                                      shielding_cells        = cell_shielding,
                                      shielding_surfs        = surf_shielding,
                                      outside_world_cells    = cell_outside_wrld,
                                      reactor_level_surfaces = surf_reactor_lvl,
                                      material_card          = materials_card,
                                      fuel_data              = active_core_data,
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
