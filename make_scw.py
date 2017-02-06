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

   

def make_pressure_vessel():
    
    string = mcnp_card()

    pressure_vessel_cell = string.cell(800,
        {'comment'  : 'Pressure Vessel', 
         'surfs'    : [-801, 802],
         'material' : 'Steel, Stainless 304'
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


def make_structural_data():
    string = mcnp_card()
    
    data_card = string.data('material',cd.material_dict)
    return data_card
def make_SCW():

    # Write cell and surface cards for each level of geometry.
    [cell_reactor_lvl, surf_reactor_lvl] = make_pressure_vessel()

    # Write general data cards.
    structural_materials = make_structural_data()
    # Write entire input file.
    input_tmpl = Template("""\
${comm_mk}  -------------------------------  CELL CARD  ------------------------------  ${comm_mk}
${comm_mk}  Reactor level        \n${reactor_level_cells}
${comm_mk}  -----------------------------  SURFACE CARD  -----------------------------  ${comm_mk}
${comm_mk}  Reactor level        \n${reactor_level_surfaces}
${comm_mk}  -------------------------------  DATA CARD  ------------------------------  ${comm_mk}
${comm_mk}  MATERIAL
${comm_mk}    General materials  \n${general_materials}${comm_mk}
${comm_mk}
${comm_mk}  ------------------------------  End of file  -----------------------------  ${comm_mk}
""")

    input_str = input_tmpl.substitute(reactor_level_cells = cell_reactor_lvl,
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
