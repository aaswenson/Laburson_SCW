"""Fuel composition library.
"""

from pyne.material import Material
import material_data as md
import math

pyne_lib = md.load_pyne_matlib()

def make_hmg_UOX_fuel():
    """Build a homogenous fuel library for initial criticality calc.
    """

    enrich    = 0.035
    frac_fuel = 0.265
    frac_clad = 0.1664
    frac_mod  = 0.569

    frac_U    = frac_fuel*(2/3)
    frac_O    = (frac_fuel + frac_mod)*(1/3)
    frac_H    = frac_mod*(1/3)
    frac_SS   = frac_clad

    pyne_ss = pyne_lib['Steel, Stainless 304'] 
    pyne_ss.mass = frac_SS

    frac_U235 = frac_U*enrich
    frac_U238 = frac_U*(1-enrich)

    fuel      = Material({'U235':enrich*0.333,'U238':(1-enrich)*0.333,'O':0.667},frac_fuel)
    mod       = Material({'H':0.667,'O':0.333},frac_mod)
    ss        = pyne_ss

    fuel_mat = fuel + mod + ss*frac_clad
    fuel_mat = fuel_mat.expand_elements()
    fuel_mat.metadata['mat_number'] = 100000

    return fuel_mat.expand_elements()

def write_fuel_library():
    fuel_library = {}
    fuel_library['fissile_homogenous'] = make_hmg_UOX_fuel()
    return fuel_library
    
