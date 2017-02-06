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
    material_num = md.material_dict[data['material']]['mat_num']
    density = cd.pyne_mats[data['material']].density
    surfaces = build_surface_tree(data['surfs'])[0]

    cell_list = cut_line(' ', "{0} {1} {2} {3}".format(number,
        material_num,-density,surfaces), data['comment'])

    return ' '.join(cell_list)
    


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
    return data_card

def write_material_card(material_name):
    data = md.material_dict[material_name]
    pyne_mat = cd.pyne_mats[material_name]
    pyne_mat.metadata['comment'] = material_name
    pyne_mat.metadata['mat_number'] = data['mat_num']
#   pyne_mat.metadata['table_ids'] = XS_library
    data_list = [str(pyne_mat.mcnp())]
    if data['mt']:
        mt_str = "mt{0:<8} {1}".format(pyne_mat.metadata['mat_number'],data['mt'])
        data_list += cut_line('    ', mt_str, 'Thermal Treatment')
    return ' '.join(data_list)







