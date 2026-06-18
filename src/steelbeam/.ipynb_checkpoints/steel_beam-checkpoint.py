"""
steel_beam - Eng. Rocco Raimo
---
Calculation of resistance and stability for steel beams, based on multiple national codes.
It is possible to show inside Jupyter Notebook the Latex output of calculations with the optional parameter "render" in every method of SteelBeam class.
"""

from handcalcs.decorator import handcalc
from math import pi
from math import sqrt
import os
import json

import forallpeople 
forallpeople.environment('structural', top_level=True)
from forallpeople import Physical

# Import the database of steel profiles
dirname = os.path.dirname(__file__)
database = json.load(open(os.path.join(dirname, 'steel_profilesdb_EC.json'), 'r'))

# Create lists of profile type and list                    
profile_type = []
for profile_t in database:
    profile_type.append(profile_t)
profile_list = []
for profile_t in profile_type:
    for prof in database[profile_t]:
        profile_list.append(prof) 

import analysis_EC

class SteelBeam:
    def __init__(self,
                 length,
                 elastic_modulus,
                 f_yk,
                 profile, 
                 section_area=0,
                 section_area_shear_y=0,
                 section_area_shear_z=0,
                 section_inertia_y=0,
                 section_inertia_z=0,
                 section_w_pl_y=0,
                 section_w_pl_z=0):
        """
        Class that represents the steel beam object.
        
        Parameters
        ------------
        length: Length of the beam;
        elastic_modulus: Elastic modulus of the steel;
        f_yk: yielding tension for the steel;
        profile: The name of the section considered. It is possible to assign a 'User defined' section or choose a profile contained in 'steel_profilesdb_EC' database.
            In case the variable profile is set to 'User defined' the following parameters can be defined: 
            section_area = gross area of the steel section
            section_area_shear_y = area for shear calculation along the y-axis
            section_area_shear_z = area for shear calculation along the z-axis
            section_inertia_y = inertia of the steel section around the y-axis (principal)
            section_inertia_z = inertia of the steel section around the z-axis (secondary)
            section_w_pl_y = plastic modulus of resistance around the y-axis
            section_w_pl_z = plastic modulus of resistance around the z-axis

        Methods
        ------------    
        The SteelBeam object has the following methods:
        
        --- RESISTANCE
            - SteelBeam.normal_force_tension: TO BE CONTINUED
        
        --- STABILITY
            - SteelBeam.: TO BE CONTINUED
        """
        self.length = length
        self.elastic_modulus = elastic_modulus
        self.f_yk = f_yk

        self.profile = profile
        if self.profile == 'User defined':
            self.section_area = section_area
            self.section_area_shear_y = section_area_shear_y
            self.section_area_shear_z = section_area_shear_z
            self.section_inertia_y = section_inertia_y
            self.section_inertia_z = section_inertia_z
            self.section_w_pl_y = section_w_pl_y
            self.section_w_pl_z = section_w_pl_z
        elif self.profile in profile_list:
            for value_type in database:
                for prof in database[value_type]:
                    if self.profile == prof:
                        # Check if the variables are unit-aware
                        if isinstance(self.length, Physical): 
                            self.section_area = float(database[value_type][prof]['A']) * mm**2
                            self.section_area_shear_y = float(database[value_type][prof]['Avy']) * mm**2
                            self.section_area_shear_z = float(database[value_type][prof]['Avz']) * mm**2
                            self.section_inertia_y = float(database[value_type][prof]['Iy']) * mm**4
                            self.section_inertia_z = float(database[value_type][prof]['Iz']) * mm**4
                            self.section_w_pl_y = float(database[value_type][prof]['Wpl_y']) * mm**3
                            self.section_w_pl_z = float(database[value_type][prof]['Wpl_z']) * mm**3
                        else:
                            self.section_area = float(database[value_type][prof]['A']) 
                            self.section_area_shear_y = float(database[value_type][prof]['Avy']) 
                            self.section_area_shear_z = float(database[value_type][prof]['Avz'])
                            self.section_inertia_y = float(database[value_type][prof]['Iy'])
                            self.section_inertia_z = float(database[value_type][prof]['Iz'])
                            self.section_w_pl_y = float(database[value_type][prof]['Wpl_y'])
                            self.section_w_pl_z = float(database[value_type][prof]['Wpl_z'])
        else:
            raise ValueError(f"""The profile is not present in the current database. Please use 'User defined'!""")

    def __repr__(self):
        return f"""SteelBeam(Profile='{self.profile}' | L={self.length} | E={self.elastic_modulus} | f_yk={self.f_yk}
        A={self.section_area} | Iy={self.section_inertia_y} | Iz={self.section_inertia_z}
        Wpl_y={self.section_w_pl_y} | Wpl_z={self.section_w_pl_z})"""   
    
