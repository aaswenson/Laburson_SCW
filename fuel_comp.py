"""This module defines fuel compositions
"""
import math 
import computed_data as cd
from pyne.material import Material
import pyne.data as pyne_data
def iterate_fuel_manifest():
    """Unpack fuel data.
    
    This function unpacks the fuel data in fuel_data.csv
    """
    file_obj = open('fuel_data.csv')
    fuel_manifest = file_obj.readlines()
    del fuel_manifest[0]
    fuel_data = {}

    for fuel_type in fuel_manifest:
        data = fuel_type.split(',')
        fuel_category = data[0]
        fuel_data[fuel_category] = {}
        [PD, pitch,clad_th, enrich_U, enrich_Pu, mfrac_Pu, mfrac_Np, mfrac_Am] = [float(value) for value in data[1:9]]

        fuel_data[fuel_category]['type']      = fuel_category
        fuel_data[fuel_category]['PD']        = PD
        fuel_data[fuel_category]['pitch']     = pitch
        fuel_data[fuel_category]['clad_th']   = clad_th
        fuel_data[fuel_category]['enrich_U']  = enrich_U
        fuel_data[fuel_category]['enrich_Pu'] = enrich_Pu
        fuel_data[fuel_category]['mfrac_Pu']  = mfrac_Pu
        fuel_data[fuel_category]['mfrac_Np']  = mfrac_Np
        fuel_data[fuel_category]['mfrac_Am']  = mfrac_Am
    
    return fuel_data


def make_fuel_composition(fuel_data):
    pyne_fuels = {}
    for fuel_type in fuel_data:
        data = fuel_data[fuel_type]
        A       = data['pitch']/math.sqrt(3)
        A_cell  = 1.5*A*A*math.sqrt(3)
        D_pin   = data['pitch']/data['PD']
        D_fuel  = D_pin - 2*data['clad_th']
        A_pin   = 3.1415*(D_pin*D_pin)/4
        A_fuel  = 3.1415*(D_fuel*D_fuel)/4
        A_clad  = A_pin - A_fuel
        A_mod   = A_cell - A_pin
    
        frac_fuel = A_fuel/A_cell
        frac_clad = A_clad/A_cell
        frac_mod  = A_mod/A_cell

        fuel_m    = {'U235'  : (1 - data['mfrac_Pu'] - data['mfrac_Np'] - data['mfrac_Am'])*data['enrich_U']/pyne_data.atomic_mass('U235'),
                     'U238'  : (1 - data['mfrac_Pu'] - data['mfrac_Np'] - data['mfrac_Am'])*(1-data['enrich_U'])/pyne_data.atomic_mass('U238'),
                     'Pu239' : data['mfrac_Pu']*data['enrich_Pu']/pyne_data.atomic_mass('Pu239'),
                     'Pu240' : data['mfrac_Pu']*(1 - data['enrich_Pu'])/pyne_data.atomic_mass('Pu240'),
                     'Np237' : data['mfrac_Np']/pyne_data.atomic_mass('Np237'),
                     'Am243' : data['mfrac_Am']/pyne_data.atomic_mass('Am243')
                     }
        MW_fuel =  2*pyne_data.atomic_mass('O') # add oxygen to the fuel
        m = 0          # intialize molecular fuel weight for future calculation
        for isotope in fuel_m:
                m  += fuel_m[isotope]
        # calculate N dens from atom frac
        fuel_afrac = {}
        for isotope in fuel_m:
            fuel_afrac[isotope] = fuel_m[isotope]/m
        # Get fuel mix atomic mass
        for isotope in fuel_afrac:
            MW_fuel += pyne_data.atomic_mass(isotope)*fuel_afrac[isotope]
        # calculate fuel isotope num dens
        fuel_ndens = {}
        for isotope in fuel_afrac:
            fuel_ndens[isotope] = frac_fuel*fuel_afrac[isotope]*6.022e23*cd.rho_fuel['U']/(MW_fuel*1e24)
        fuel_ndens['O'] = (frac_fuel*2*cd.rho_fuel['U']/MW_fuel + frac_mod*cd.rho_fuel['W']/(2*pyne_data.atomic_mass('H') + pyne_data.atomic_mass('O')))*6.022e-1
        fuel_ndens['H'] = frac_mod*2*cd.rho_fuel['W']*6.022e-1/(2*pyne_data.atomic_mass('H')+pyne_data.atomic_mass('O'))
        # calculate atom fracs for homogenized fuel region

        fuel_mod_pyne = Material()
        fuel_mod_pyne.from_atom_frac(fuel_ndens)
    
        clad_mat = cd.pyne_mats['Steel, Stainless 304']
    
        homog_fuel = fuel_mod_pyne + clad_mat*frac_clad
        homog_fuel.density = cd.rho_fuel[fuel_type] * frac_fuel + \
        cd.rho_fuel['W'] * frac_mod + clad_mat.density * frac_clad
        
        pyne_fuels[data['type']] = homog_fuel
        
    return pyne_fuels


