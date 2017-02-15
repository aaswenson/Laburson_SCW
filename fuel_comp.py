"""This module defines fuel compositions
"""
import math 
import computed_data as cd
from pyne.material import Material

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


def make_fuel_composition_pyne(fuel_data):
    pyne_fuels = {}
    for fuel_type in fuel_data:
        data = fuel_data[fuel_type]
        A_cell  = data['pitch']*data['pitch']
        D_pin   = data['pitch']/data['PD']
        D_fuel  = D_pin - 2*data['clad_th']
        A_pin   = 3.1415*(D_pin*D_pin)/4
        A_fuel  = 3.1415*(D_fuel*D_fuel)/4
        A_clad  = A_pin - A_fuel
        A_mod   = A_cell - A_pin

        frac_fuel = A_fuel/A_cell
        frac_clad = A_clad/A_cell
        frac_mod  = A_mod/A_cell

        m_fuel = cd.rho_UO2*frac_fuel
        m_clad = cd.rho_SS*frac_clad
        m_mod  = cd.rho_H2O*frac_mod
        
        m      = m_fuel + m_clad + m_mod

        mfrac_fuel = m_fuel/m
        mfrac_clad = m_clad/m
        mfrac_mod  = m_mod/m


        mfrac_U = mfrac_fuel*(1 - data['mfrac_Pu'] - data['mfrac_Np'] - data['mfrac_Am'])*0.333
        mfrac_U235 = mfrac_U*data['enrich_U']
        mfrac_U238 = mfrac_U*(1 - data['enrich_U'])
        mfrac_Pu239 = mfrac_fuel*data['mfrac_Pu']*data['enrich_Pu']*0.333
        mfrac_Pu240 = mfrac_fuel*data['mfrac_Pu']*(1.0-data['enrich_Pu'])*0.333
        mfrac_O     = mfrac_fuel*0.667 + mfrac_mod*0.333
        mfrac_H     = mfrac_mod*0.667

        fuel_composition = {'U235':mfrac_U235,'U238':mfrac_U238,'Pu239':mfrac_Pu239,'Pu240':mfrac_Pu240,'Np237':data['mfrac_Np']*0.333,'Am241':data['mfrac_Am']*0.333,'O':mfrac_O,'H':mfrac_H}
        fuel_mat = Material(fuel_composition)
        
        clad_mat = cd.pyne_mats['Steel, Stainless 304']
        
        homog_fuel = clad_mat*mfrac_clad + fuel_mat
        pyne_fuels[data['type']] = homog_fuel

    return pyne_fuels


