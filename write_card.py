"""Module to write MCNP cards.

This module writes the cards for an MCNP6 input file.

The following functions are contained in this model.
  * cut_line 
  * right_align
  * build_surface_tree
  * apply_MCNP_operator
  * iterate_cell_cards
  * write_cell_card
  * write_surf_card
  * iterate_data_card
  * write_material_card
  * write_fuel_data
  * write_general_data
  * make_burnup_card
  * convert_core_lattice
  * make_lattice_map
  * like_but
"""

import material_data as md
import numpy as np
import fuel_comp as fc
import computed_data as cd
comment_EOL = '$'
comment_mark = 'c'

fuel_data = fc.iterate_fuel_manifest()
pyne_fuels = fc.make_fuel_composition(fuel_data)


def cut_line(split_str, undiv_str, comment):
    """Cut a string to meet maximum length of a line for MCNP.

    This function cuts a single undivided string into a list of strings.
    Indicative string of division is given as an input of the function
    so that user can choose how to divide each string separately.
    This function writes a comment string, if given, with a comment character
    at the end of each line.
    Maximum length of line is still satisfied with the added comment.

    Arguments:
        split_str (str)[-]: Indicative string of division.
        undiv_str (str)[-]: Single undivided string.
        comment (str)[-]: Additional comment string.

    Returns:
        string_list (str)[-]: List of strings that satisfy
                              the maximum length of line.
    """

    max_str_limit = 80  # MCNP-inherent maximum length of line.
    indent = '         '  # Set indentation for enhanced readability.
    comment_init = ' {0}'.format(comment_EOL)  # Affix for the comment.

    # Reduce the limit of line length due to the comment.
    str_limit = max_str_limit - len(comment) - len(comment_init)

    string_list = [undiv_str]

    # Make a list of strings until each string satisfies the limit of line
    # length.
    while len(string_list[-1]) > str_limit:

        # For an undivided string, find from the right a starting index number
        # that gives the first indicative string within the first 80
        # characters.
        split_index = string_list[-1].rfind(split_str, 0, str_limit)

        # Split current string into two strings.
        # Add given comment on the first string using right_align function.
        # Indent the second string.
        div_list = [right_align(string_list[-1][:split_index], comment, max_str_limit),
                    indent + string_list[-1][split_index + len(split_str):]]

        # Reset the limit of line length by removing the string of division.
        str_limit = max_str_limit + \
            len(split_str) - len(comment) - len(comment_init)

        # Delete previous undivided string and append new list of strings.
        del string_list[-1]
        string_list += div_list

    # Add comment on the last string that already satisfies the limit of line
    # length.
    string_end = string_list[-1]
    del string_list[-1]
    string_list += [right_align(string_end, comment, max_str_limit)]

    return string_list


def right_align(string, comment, max_limit):
    """Add right-aligned comment to a string with the maximum line length.

    This function adds given comment to the given string. For better readability, 
    it adds the comment further right until it reaches the maximum length of line.

    Arguments:
        string (str)[-]: A string to which given comment will be added.
        comment (str)[-]: Comment string.
        max_limit (int)[-]: Maximum length of line.

    Returns:
        oneline (str)[-]: One-line string with right-aligned comment.
    """
    num = len(string)

    if len(comment) == 0:  # If the given comment is blank.
        comment_str = ''
    else:
        comment_str = "{0}{1}".format(comment_EOL, comment)

    oneline = "{0}{1:>{2}}\n".format(string, comment_str, max_limit - num)
    return oneline


def build_surface_tree(surface, state=0):
    """Create surface algebra tree

    Args: surface (list): List of surfaces with interesection/union relationships
          state (int): initialize state to 0, state < 2 indicates a single-layer cell
    Returns: Calls "apply_MCNP_operator" to write and return an MCNP-specific cell definition string
    """
    if type(surface) == int or type(surface) == float:
        return str(surface), state
    # check for a simple cell (one "layer" of surface combinations)
    if state < 2:
        state = state + 1
    # set the operator for every data container, list = intersection, tuple
    # (else) = union
    if type(surface) == list:
        operator = 'intersection'
    else:
        operator = 'union'
    items = []
    for item in surface:
        items.append(build_surface_tree(item, state)[0])
    # call the MCNP-specific string function to write cell definition
    return apply_MCNP_operator(operator, items, state), state


def apply_MCNP_operator(operator, items, state):
    """Write cell definition in MCNP-specific format

    Args: operator (string): " " or ":" to set inter-surface delimiters
          item (list): surface id numbers to combine into string
          state (int): call for parentheses if depth surface container > 1 level
    Returns: MCNP cell string
    """
    delimiter = {'intersection': ' ', 'union': ':'}
    rh_p = lh_p = ""
    if state > 1:
        # assign extra parantheses delimiters for MCNP
        # rh = right hand, lh = left hand
        rh_p = ")"
        lh_p = "("

    return lh_p + delimiter[operator].join(items) + rh_p


def iterate_cell_cards(number, data):
    """Iterate through and write cell cards.

    This function unpacks cell data and calls function to write the cell cards.

    Args:
        number (int): base cell number
        data (dict): cell data used to write card
    Returns:
        cell_str (str): MCNP cell card
    """
    cell_list = []
    for idx, cell in enumerate(data):
        if 'fuel' in cell.keys():
            if cell['fuel']:
                cell['mat_num'] = cell['univ']
                mat = pyne_fuels[cell['material']]
            else:
                mat = cd.pyne_mats[cell['material']]
                cell['mat_num'] = md.material_dict[cell['material']]['mat_num']
        else:
            mat = cd.pyne_mats[cell['material']]
            cell['mat_num'] = md.material_dict[cell['material']]['mat_num']
        density = mat.density
      
        cell_list += write_cell_card(number + idx, cell, density)
    # concatenate all cell lists into one string
    cell_str = ''.join(cell_list)
    return cell_str


def write_cell_card(number, cell_data, density):
    """Write the cell card string.

    This function produces an MCNP6 cell card string.

    Args:
        number (int): cell number
        cell_data (dict): data required to right the cell
        density (float): cell density
    Returns:
        cell_list (list): list with MCNP cell strings.
    """
    # Check if it's void cell.
    if cell_data['material'] == 'void':
        cell_str = "{0} 0 ".format(number)
    else:
        cell_str = "{0} {1} {2} ".format(number,
                                         cell_data['mat_num'],
                                         density)

    # Make a cell geometry with given surface arguments.
    cell_str += build_surface_tree(cell_data['surfs'])[0]

    # Check if it has volume entry.
    if cell_data['vol']:
        cell_str += " vol={0}".format(cell_data['vol'])
    # Check if it has lattice card.
    if cell_data['lat']:
        cell_str += " lat={0}".format(cell_data['lat'])
    # Check if it has fill card.
    if cell_data['fill']:
        cell_str += " fill={0}".format(cell_data['fill'])
    # Check if it has universe number entry.
    if cell_data['univ']:
        cell_str += " u={0}".format(cell_data['univ'])

    # Write importance.
    cell_str += " imp:n={0}".format(cell_data['imp'])
    # Make list of strings to satisfy the limit of line length.
    cell_list = cut_line(' ', cell_str, cell_data['comment'])   
    
    return cell_list


def write_surf_card(data):
    """Write surface card.

    This function writes an MCNP6 surface card.

    Args:
        data (dict): dictionary with surface parameters.
    Returns:
        surf_str (str): MCNP surface string.
    """
    surf_str = ''
    for surface in data:
        parameters = ''
        for surf_data in surface['inputs']:
            parameters += str(surf_data) + ' '
        surf_str += ' '.join(cut_line(' ', "{0} {1} {2}".format(surface['number'], surface['type'],
                                                                parameters), surface['comment']))
    return surf_str

def iterate_data_card(category, data):
    data_card = ''
    if category == 'material':
        for material in data:
            if material != 'void':
                data_card += write_material_card(material)
    elif category == 'fuel':
        for fuel_mat in data:
            data_card += write_fuel_mat_card(data[fuel_mat])
    return data_card


def write_material_card(material_name):
    data = md.material_dict[material_name]
    pyne_mat = cd.pyne_mats[material_name]
    pyne_mat.metadata['comment'] = material_name
    del pyne_mat['8018']
    pyne_mat.metadata['mat_number'] = data['mat_num']
#   pyne_mat.metadata['table_ids'] = XS_library
    data_list = [str(pyne_mat.mcnp())]
    if data['mt']:
        mt_str = "mt{0:<8} {1}".format(
            pyne_mat.metadata['mat_number'], data['mt'])
        data_list += cut_line('    ', mt_str, 'Thermal Treatment')
    return ' '.join(data_list)

def write_fuel_data(mat, material_num):
    unexpanded_mat = pyne_fuels[mat]
    pyne_mat = unexpanded_mat.expand_elements()
    del pyne_mat['8018']
    pyne_mat.metadata['mat_number'] = material_num
#   pyne_mat.metadata['table_ids'] = XS_library
    data_list = [str(pyne_mat.mcnp())]
    return ' '.join(data_list)

def write_general_data(data):

    if data['category'] == 'mode':
        data_str = data['category'] + ' ' + data['particle'] + '\nprint'
    elif data['category'] == 'kcode':
        data_str = "{0} {1} \n{2} {3}".format(
            'kcode', data['kcode'], 'ksrc', data['ksrc'])
    else:
        pass
    return data_str


def make_burnup_card():
    """Make burnup cards.

    This module makes burnup cards for fuel pins.
    * burn_mat: Burnup material card. Material to be burned.
        Corresponds identically to material number
        specified on a material specification card.

    Arguments:
        none
    Returns:
        burn_str: Burnup material card strings.

    """

    burn_str = 'burn '  # Initialize string to write burnup card.
    burn_input = {"time": '54.75 9R',  # Incremental time duration for each burn step.
                  # Fraction of total power applied to each burn step.
                  "pfrac": '1 9R',
                  # Total recoverable fission system power. [MW]
                  "power": '1341',
                  "bopt": '1 14 -1',  # Output control parameters.
                  }

    for key in sorted(burn_input.keys(), reverse=True):

        burn_str += "{0}={1} ".format(key, burn_input[key])

    core_map = cd.import_core_map()
    bundle_map = cd.get_master_bundles(core_map)[1]

    # Write material entries.
    burn_mat = '\n        mat='  # Initialize string to write material entries.

    for fuel_id in sorted(bundle_map):  # For all fuel ID numbers.
        if bundle_map[fuel_id] != 'W':
            base_mat_id = 1000 * (fuel_id[0] + 1) + fuel_id[1]
            burn_mat += "  {0}".format(base_mat_id)
    burn_str += ''.join(cut_line('  ', burn_mat, 'burn_mat'))

    # ZAIDs to be omitted.
    omit_list = [66159, 67163, 67164, 67166, 68163, 68165, 68169, 69166, 69167, 69171, 69172, 69173, 70168, 70169, 70170, 70171, 70172, 70173, 70174,
                 6014, 7016, 39087, 39092, 39093, 40089, 40097, 41091, 41092, 41096, 41097, 41098, 41099, 42091, 42093, 70175, 70176, 71173, 71174,
                 71177, 72175, 72181, 72182, 73179, 73183, 74179, 74181, 8018, 8019, 9018, 10021, 12027, 13026, 13028, 14027, 14031, 16031, 16035, 16037, 17034, 17036,
                 17038, 18037, 18039, 22051, 23047, 23048, 23049, 23052, 23053, 23054, 24049, 24051, 24055, 24056, 25051, 25052, 25053, 25054, 25056, 25057, 25058, 26053,
                 26055, 26059, 26060, 26061, 27057, 27060, 27061, 27062, 27063, 27064, 28057, 28063, 28065, 29062, 29064, 29066]
    omit_str = ''  # Initialize string to write omit entries.

    for ZAID in omit_list:
        omit_str += "{0} ".format(ZAID)

    burn_omit = "      omit= -1 {0} {1}".format(len(omit_list), omit_str)

    burn_str += ''.join(cut_line(' ', burn_omit, 'burn_omit'))

    return burn_str


def convert_core_lattice(lattice_map, water_bundle):

    req_length = max(len(row) for row in lattice_map)

    x_extent = int(req_length / 2) + (req_length % 2 > 0)
    y_extent = int(len(lattice_map) / 2) + (len(lattice_map) % 2 > 0) - 1

    formatted_lattice_map = ''
    Top = True

    for row, bundles in enumerate(lattice_map):
        for col, bundle in enumerate(bundles):
            if bundle == 'W':
                bundles[col] = water_bundle
            else:
                bundles[col] = str(1000 * (row + 1) + col)
        row_str = ' '.join(bundles)
        n_water_bund = req_length - len(bundles)
        added_water = np.repeat(water_bundle, n_water_bund).tolist()
        water_str = ' '.join([str(i) for i in added_water])

        if (Top == True) and (len(bundles) < req_length):
            formatted_row = "{0} {1} {2} {0} ".format(
                water_bundle, water_str, row_str)
        elif len(bundles) == req_length:
            formatted_row = "{0} {1} {0} ".format(
                water_bundle, row_str, water_bundle)
            Top = False
        else:
            formatted_row = "{0} {1} {2} {0} ".format(
                water_bundle, row_str, water_str)

        formatted_lattice_map += formatted_row.replace('W', water_bundle)
    formatted_lattice_map += ' imp:n=1'
    return formatted_lattice_map, x_extent, y_extent


def make_lattice_map(formatted_lattice_map, univ, cell, surf, x_extent, y_extent):

    core_lattice_str = "{0} 0 {1} u={2} lat=2 fill=-{3}:{3} -{4}:{4} 0:0\n         {5}"\
        .format(cell,
                surf,
                univ,
                x_extent,
                y_extent,
                formatted_lattice_map)
    lat_list = cut_line(' ', core_lattice_str, '')
    lat_str = ''.join(lat_list)
    return lat_str


def like_but(base_cell, univ, water, vol):

    if water == False:
        mat = 'mat=' + str(univ)
    if vol:
        vol = 'vol=' + str(vol)
    else:
        mat = ''
    cell_str = "{0} like {1} but u={0} {2} {3} imp:n=1\n".format(univ,
                                                                 base_cell,
                                                                 mat,
                                                                 vol)

    return cell_str
