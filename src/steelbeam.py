"""
steelbeam - Eng. Rocco Raimo
---
A python package for calculation of resistance and stability of steel beams, based on multiple national codes.

--
It is possible to show the Latex output of calculations inside Jupyter Notebook with the optional parameter "render" in every analysis method of SteelBeam.
"""

from handcalcs.decorator import handcalc
import handcalcs
from math import pi
from math import sqrt
import os
import json
import types

handcalcs.set_option("custom_symbols", {"C": ","})

import forallpeople 
forallpeople.environment('structural', top_level=True)
from forallpeople import Physical

# Import the database of steel profiles
dirname = os.path.dirname(__file__)
database = json.load(open(os.path.join(dirname, 'profilesdb_EU.json'), 'r'))

# Create lists of profile type and list                    
profile_type = []
for profile_t in database:
    profile_type.append(profile_t)
profile_list = []
for profile_t in profile_type:
    for prof in database[profile_t]:
        profile_list.append(prof) 

from . import analysis_EC
from . import analysis_AISC
from . import analysis_NBR

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
                 section_w_pl_z=0,
                 h_w=0,
                 t_w=0,
                 b=0,
                 t_f=0):
        """
        Class that represents the steel beam object.
        
        Parameters
        ------------
        length: Length of the beam;
        elastic_modulus: Elastic modulus of the steel;
        f_yk: yielding tension for the steel;
        profile: The name of the section considered. It is possible to assign a 'User defined' section or choose a profile contained in 'steel_profilesdb_EU' database.
            In case the variable profile is set to 'User defined' the following parameters can be defined: 
            section_area = gross area of the steel section
            section_area_shear_y = area for shear calculation along the y-axis
            section_area_shear_z = area for shear calculation along the z-axis
            section_inertia_y = inertia of the steel section around the y-axis (principal)
            section_inertia_z = inertia of the steel section around the z-axis (secondary)
            section_w_pl_y = plastic modulus of resistance around the y-axis
            section_w_pl_z = plastic modulus of resistance around the z-axis
            h_w = height of the web (for I-sections: h - 2*tf)
            t_w = thickness of the web
            b = width of the flange (base)
            t_f = thickness of the flange

        Sign convention
        ------------

                 z ↑
                 │
                 │
            ┌────┼────┐
            │    │    │
        ────┼────●────┼────→ y
            │    │    │
            └────┴────┘
                 │
        
        
        """
        self.length = length
        self.elastic_modulus = elastic_modulus
        self.shear_modulus = self.elastic_modulus / (2*(1+0.3))
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
            self.h_w = h_w
            self.t_w = t_w
            self.b = b
            self.t_f = t_f
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
                            self.h_w = (float(database[value_type][prof]['h']) - 2 * float(database[value_type][prof]['tf'])) * mm
                            self.t_w = float(database[value_type][prof]['tw']) * mm
                            self.b = float(database[value_type][prof]['bf']) * mm
                            self.t_f = float(database[value_type][prof]['tf']) * mm
                        else:
                            self.section_area = float(database[value_type][prof]['A']) 
                            self.section_area_shear_y = float(database[value_type][prof]['Avy']) 
                            self.section_area_shear_z = float(database[value_type][prof]['Avz'])
                            self.section_inertia_y = float(database[value_type][prof]['Iy'])
                            self.section_inertia_z = float(database[value_type][prof]['Iz'])
                            self.section_w_pl_y = float(database[value_type][prof]['Wpl_y'])
                            self.section_w_pl_z = float(database[value_type][prof]['Wpl_z'])
                            self.h_w = float(database[value_type][prof]['h']) - 2 * float(database[value_type][prof]['tf'])
                            self.t_w = float(database[value_type][prof]['tw'])
                            self.b = float(database[value_type][prof]['bf'])
                            self.t_f = float(database[value_type][prof]['tf'])
        else:
            raise ValueError(f"""The profile is not present in the current database. Please use 'User defined'!""")

    def __repr__(self):
        return f"""SteelBeam(Profile='{self.profile}' | L={self.length} | E={self.elastic_modulus} | f_yk={self.f_yk}
        A={self.section_area} | Iy={self.section_inertia_y} | Iz={self.section_inertia_z}
        Wpl_y={self.section_w_pl_y} | Wpl_z={self.section_w_pl_z} | h_w={self.h_w} | t_w={self.t_w} | b={self.b} | t_f={self.t_f})"""   

    _default_partial_factors = {
        'EC': {
            'gamma_m0': 1.05,
            'gamma_m1': 1.05,
            'gamma_m2': 1.25,
        },
        'AISC': {},
        'NBR': {},
    }

    def analysis(self, code: str = 'EC', partial_factors = 'default'):
        """
        Attach the chosen analysis module methods to this beam instance.

        Parameters
        ------------
        code: national code to calculate resistance or stability for the profile
            Available codes:
            - 'EC':     Eurocodes
            - 'AISC':   USA code;
            - 'NBR':    Brazilian code;
        """
        valid_codes = ('EC', 'AISC', 'NBR')
        if code not in valid_codes:
            raise ValueError(f"code must be one of {valid_codes}")

        # Remove previous analysis methods if switching codes
        if hasattr(self, '_current_analysis_code') and self._current_analysis_code != code:
            if hasattr(self, '_analysis_methods'):
                for method_name in self._analysis_methods:
                    if hasattr(self, method_name):
                        delattr(self, method_name)
                self._analysis_methods.clear()

        # Set current code
        self._current_analysis_code = code

        # Configure partial safety factors
        if partial_factors == 'default' or partial_factors is None:
            self._partial_factors = dict(self._default_partial_factors.get(code, {}))
        elif isinstance(partial_factors, dict):
            defaults = dict(self._default_partial_factors.get(code, {}))
            defaults.update(partial_factors)
            self._partial_factors = defaults
        else:
            raise TypeError("partial_factors must be 'default', None, or a dict of factor names")

        # Initialize set for tracking methods
        if not hasattr(self, '_analysis_methods'):
            self._analysis_methods = set()

        # Add new methods based on code
        if code == 'EC':
            module = analysis_EC
        elif code == 'AISC':
            module = analysis_AISC
        elif code == 'NBR':
            module = analysis_NBR

        for name in dir(module):
            if name.startswith('_'):
                continue
            attr = getattr(module, name)
            if isinstance(attr, types.FunctionType):
                setattr(self, name, types.MethodType(attr, self))
                self._analysis_methods.add(name)

        return


