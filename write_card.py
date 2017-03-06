import material_data as md
import computed_data as cd
comment_EOL = '$'
comment_mark = 'c'

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

    # Make a list of strings until each string satisfies the limit of line length.
    while len(string_list[-1]) > str_limit:

        # For an undivided string, find from the right a starting index number
        # that gives the first indicative string within the first 80 characters.
        split_index = string_list[-1].rfind(split_str, 0, str_limit)

        # Split current string into two strings.
        # Add given comment on the first string using right_align function.
        # Indent the second string.
        div_list = [right_align(string_list[-1][:split_index], comment, max_str_limit),
                    indent + string_list[-1][split_index + len(split_str):]]
        
        # Reset the limit of line length by removing the string of division.
        str_limit = max_str_limit + len(split_str) - len(comment) - len(comment_init)

        # Delete previous undivided string and append new list of strings.
        del string_list[-1]
        string_list += div_list

    # Add comment on the last string that already satisfies the limit of line length.
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
    # set the operator for every data container, list = intersection, tuple (else) = union
    if type(surface) == list:
        operator = 'intersection'
    else:
        operator = 'union'
    items = []
    for item in surface:
        items.append(build_surface_tree(item,state)[0])
    # call the MCNP-specific string function to write cell definition
    return apply_MCNP_operator(operator,items,state), state

def apply_MCNP_operator(operator,items,state):
    """Write cell definition in MCNP-specific format

    Args: operator (string): " " or ":" to set inter-surface delimiters
          item (list): surface id numbers to combine into string
          state (int): call for parentheses if depth surface container > 1 level
    Returns: MCNP cell string
    """
    delimiter = {'intersection':' ','union':':'}
    rh_p = lh_p = ""
    if state > 1:
        # assign extra parantheses delimiters for MCNP
        # rh = right hand, lh = left hand
        rh_p = ")"
        lh_p = "("
    return lh_p + delimiter[operator].join(items) + rh_p

def write_cell_card(number,data):
    cell_str = ''
    i = 0
    for cell in data:
        if type(cell['material']) == int:
            material_num = cell['material'] 
            density = 5
        else:
            material_num = md.material_dict[cell['material']]['mat_num']

        # check for provided density for fuels
        if 'density' in cell.keys():
            density = float(cell['density'])
        else:
            density = cd.pyne_mats[cell['material']].density
        surfaces = build_surface_tree(cell['surfs'])[0]
        if cell['material'] != 'void':
            if 'vol' in cell.keys():
                cell_list = cut_line(' ',  "{0} {1} {2} {3} imp:n={4} vol={5}".format(number+i, material_num, -density, surfaces, cell['imp'], cell['vol']), cell['comment'])
            else:
                cell_list = cut_line(' ',  "{0} {1} {2} {3} imp:n={4}".format(number+i, material_num, -density, surfaces, cell['imp']), cell['comment'])
        else:
            cell_list = cut_line(' ',"{0} {1} {2} imp:n={3}".format(number, 0, surfaces, cell['imp']), cell['comment'])
        cell_str += ' '.join(cell_list)
        i += 1
    return cell_str
    


def write_surf_card(data):
    surf_str = ''
    for surface in data:
        parameters = ''
        for surf_data in surface['inputs']:
            parameters += str(surf_data) + ' '
        surf_str += ' '.join(cut_line(' ', "{0} {1} {2}".format(surface['number'],surface['type'],
                            parameters),surface['comment']))
    return surf_str

def iterate_data_card(category,data):
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
        mt_str = "mt{0:<8} {1}".format(pyne_mat.metadata['mat_number'],data['mt'])
        data_list += cut_line('    ', mt_str, 'Thermal Treatment')
    return ' '.join(data_list)

def write_fuel_data(pyne_mat,material_num):
    pyne_mat = pyne_mat.expand_elements()
    del pyne_mat['8018']
    pyne_mat.metadata['mat_number'] = material_num
#   pyne_mat.metadata['table_ids'] = XS_library
    data_list = [str(pyne_mat.mcnp())]
    return ' '.join(data_list)


def write_general_data(data):
    
    if data['category'] == 'mode':
        data_str = data['category'] + ' ' + data['particle'] + '\nprint'
    elif data['category'] == 'kcode':
        data_str = "{0} {1} \n{2} {3}".format('kcode',data['kcode'],'ksrc',data['ksrc'])
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
        fuel_id (int)[#]: Fuel ID number of a pin.
        rad_div (int)[#]: Number of radial divisions in a pin active region.
        axi_div (int)[#]: Number of axial divisions in a pin active region.
        
    Returns:
        burn_str: Burnup material card strings.

    """
    
    burn_str = 'burn '  # Initialize string to write burnup card.
    burn_input = {"time": '54.75 9R',  # Incremental time duration for each burn step.
                  "pfrac": '9R',  # Fraction of total power applied to each burn step.
                  "power": 1,  # Total recoverable fission system power. [MW]
                  "bopt": '1 14 -1',  # Output control parameters.
                  "comment": "Burnup_input"}


    for key in sorted(burn_input.keys(), reverse=True):
        if key == 'time':
            burn_str += " time={0}".format(burn_input[key])
        elif key == 'pfrac':
            burn_str += " pfrac={0}".format(burn_input[key])
        elif key == 'power':
            burn_str += " power={0}".format(burn_input[key])
        elif key == 'bopt':
            burn_str += " bopt={0}".format(burn_input[key])
        else:
            continue

    burn_str = ''.join(cut_line(' ', burn_str, burn_input["comment"]))

    # Write material entries.
    burn_mat = '      mat='  # Initialize string to write material entries.
    
    file_obj = open('fuel_ids.csv')
    fuel_ids = file_obj.readlines()
    del fuel_ids[0]
    
    for fuel_region in fuel_ids:
        
        burn_mat += fuel_region.split(',')[1]+ ' '
    file_obj.close()    
    burn_str += ''.join(cut_line('  ', burn_mat, 'burn_mat'))
    # Write omit entries.
    # ZAIDs to be omitted.
    omit_list = [66159, 67163, 67164, 67166, 68163, 68165, 68169, 69166, 69167, 69171, 69172, 69173, 70168, 70169, 70170, 70171, 70172, 70173, 70174,
                 6014, 7016, 39087, 39092, 39093, 40089, 40097, 41091, 41092, 41096, 41097, 41098, 41099, 42091, 42093, 70175, 70176, 71173, 71174,
                 71177, 72175, 72181, 72182, 73179, 73183, 74179, 74181, 8018, 8019, 9018, 10021, 12027, 13026, 13028, 14027, 14031, 16031, 16035, 16037, 17034, 17036, 
                 17038, 18037, 18039, 22051, 23047, 23048, 23049, 23052, 23053, 23054, 24049, 24051, 24055, 24056, 25051, 25052, 25053, 25054, 25056, 25057, 25058, 26053, 
                 26055, 26059, 26060, 26061, 27057, 27060, 27061, 27062, 27063, 27064, 28057, 28063, 28065, 29062, 29064, 29066]
    omit_str = ''  # Initialize string to write omit entries.
    
    for ZAID in omit_list:
        omit_str += " {0}".format(ZAID)
        
    burn_omit = "      omit= -1 {0} {1}".format(len(omit_list), omit_str)
    
    burn_str += ''.join(cut_line(' ', burn_omit, 'burn_omit'))
        
    return burn_str



