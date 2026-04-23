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
import functools

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

# Helper function to get profiles by type
def get_profiles_by_type(profile_type_name: str) -> list:
    """
    Get list of profiles for a specific type.
    
    Parameters
    ----------
    profile_type_name : str
        The type of profile (e.g., 'IPE_SECTION', 'HE_SECTION', 'IPE_SECTION')
    
    Returns
    -------
    list
        List of profile names belonging to the specified type
    """
    if profile_type_name not in database:
        raise ValueError(f"Type '{profile_type_name}' not found. Available types: {list(database.keys())}")
    return list(database[profile_type_name].keys()) 

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
                 h_w=None,
                 t_w=None,
                 b=None,
                 t_f=None,
                 units='SI'):
        """
        Class that represents the steel beam object.
        
        Parameters
        ------------
        length: Length of the beam;
        elastic_modulus: Elastic modulus of the steel;
        f_yk: yielding tension for the steel;
        profile: The name of the section considered. It is possible to assign a 'User defined' section or choose a profile contained in the database.
            The list of profiles in the available database can be accessed with the ......
            In case of 'User defined' profile the following parameters can be defined: 
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
            units = unit system for plain numeric inputs ('SI' or 'imperial')

            All 'User defined' parameters can be provided as plain numeric values or as
            unit-aware `Physical` objects. When `units='SI'`, numeric inputs are
            interpreted as mm/mm²/mm³/mm⁴ and `elastic_modulus`/`f_yk` as MPa.
            When `units='imperial'`, numeric inputs are interpreted as
            inches/in²/in³/in⁴ and `elastic_modulus`/`f_yk` as ksi; they are
            converted internally to mm-based units and MPa.

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
        self.units = units.upper() if isinstance(units, str) else units
        if self.units not in ('SI', 'IMPERIAL'):
            raise ValueError("units must be either 'SI' or 'imperial'")

        if isinstance(length, Physical):
            self.length = length
        else:
            self.length = length * 25.4 if self.units == 'IMPERIAL' else length

        if isinstance(elastic_modulus, Physical):
            self.elastic_modulus = elastic_modulus
        else:
            self.elastic_modulus = elastic_modulus * 6.895 if self.units == 'IMPERIAL' else elastic_modulus

        if isinstance(f_yk, Physical):
            self.f_yk = f_yk
        else:
            self.f_yk = f_yk * 6.895 if self.units == 'IMPERIAL' else f_yk

        self.shear_modulus = self.elastic_modulus / (2*(1+0.3))

        self.profile = profile

        def _unit_value(value, si_unit, imperial_factor):
            if value is None:
                return None
            if isinstance(value, Physical):
                return value
            if self.units == 'SI':
                return value * si_unit if isinstance(self.length, Physical) else value
            return value * imperial_factor * si_unit if isinstance(self.length, Physical) else value * imperial_factor

        self.section_area = _unit_value(section_area, mm**2, 645.16)
        self.section_area_shear_y = _unit_value(section_area_shear_y, mm**2, 645.16)
        self.section_area_shear_z = _unit_value(section_area_shear_z, mm**2, 645.16)
        self.section_inertia_y = _unit_value(section_inertia_y, mm**4, 416231.0597)
        self.section_inertia_z = _unit_value(section_inertia_z, mm**4, 416231.0597)
        self.section_w_pl_y = _unit_value(section_w_pl_y, mm**3, 16387.064)
        self.section_w_pl_z = _unit_value(section_w_pl_z, mm**3, 16387.064)
        self.h_w = _unit_value(h_w, mm, 25.4)
        self.t_w = _unit_value(t_w, mm, 25.4)
        self.b = _unit_value(b, mm, 25.4)
        self.t_f = _unit_value(t_f, mm, 25.4)
        if self.profile == 'User defined':
            return
        elif self.profile in profile_list:
            for value_type in database:
                for prof in database[value_type]:
                    if self.profile == prof:
                        # Check if the variables are unit-aware
                        unit_factor_area = mm**2 if isinstance(self.length, Physical) else 1
                        unit_factor_inertia = mm**4 if isinstance(self.length, Physical) else 1
                        unit_factor_modulus = mm**3 if isinstance(self.length, Physical) else 1
                        unit_factor_length = mm if isinstance(self.length, Physical) else 1
                        
                        self.section_area = float(database[value_type][prof]['A']) * unit_factor_area
                        self.section_area_shear_y = float(database[value_type][prof].get('Avy', database[value_type][prof].get('Avz', 0))) * unit_factor_area
                        self.section_area_shear_z = float(database[value_type][prof]['Avz']) * unit_factor_area
                        self.section_inertia_y = float(database[value_type][prof]['Iy']) * unit_factor_inertia
                        self.section_inertia_z = float(database[value_type][prof].get('Iz', database[value_type][prof]['Iy'])) * unit_factor_inertia
                        self.section_w_pl_y = float(database[value_type][prof]['Wpl_y']) * unit_factor_modulus
                        self.section_w_pl_z = float(database[value_type][prof].get('Wpl_z', database[value_type][prof]['Wpl_y'])) * unit_factor_modulus
                        
                        # Handle dimensions based on section type
                        if value_type == 'CHS_SECTION':
                            self.h_w = float(database[value_type][prof]['OD']) * unit_factor_length
                            self.t_w = float(database[value_type][prof]['TDES']) * unit_factor_length
                            self.b = float(database[value_type][prof]['OD']) * unit_factor_length
                            self.t_f = float(database[value_type][prof]['TDES']) * unit_factor_length
                        elif value_type == 'RHS_SECTION':
                            self.h_w = float(database[value_type][prof]['Htot']) * unit_factor_length
                            self.t_w = float(database[value_type][prof]['tw']) * unit_factor_length
                            self.b = float(database[value_type][prof]['b']) * unit_factor_length
                            self.t_f = float(database[value_type][prof]['tf']) * unit_factor_length
                        else:
                            # For I-sections and others
                            self.h_w = (float(database[value_type][prof]['h']) - 2 * float(database[value_type][prof]['tf'])) * unit_factor_length
                            self.t_w = float(database[value_type][prof]['tw']) * unit_factor_length
                            if value_type in ['L_SECTION', '2L_SECTION', '2C_SECTION']:
                                self.b = float(database[value_type][prof]['b']) * unit_factor_length
                            else:
                                self.b = float(database[value_type][prof]['bf']) * unit_factor_length
                            self.t_f = float(database[value_type][prof]['tf']) * unit_factor_length
        else:
            raise ValueError(f"""The profile is not present in the current database. Please use 'User defined'!""")

    _unit_conversion = {
        'length': {'imp_factor': 25.4, 'si_unit': 'mm', 'imp_unit': 'in'},
        'area': {'imp_factor': 645.16, 'si_unit': 'mm**2', 'imp_unit': 'in**2'},
        'inertia': {'imp_factor': 416231.0597, 'si_unit': 'mm**4', 'imp_unit': 'in**4'},
        'section_modulus': {'imp_factor': 16387.064, 'si_unit': 'mm**3', 'imp_unit': 'in**3'},
        'stress': {'imp_factor': 6.895, 'si_unit': 'MPa', 'imp_unit': 'ksi'},
        'force': {'imp_factor': 4.4482216152605, 'si_unit': 'N', 'imp_unit': 'lbf'},
        'moment': {'imp_factor': 112.984829018, 'si_unit': 'Nmm', 'imp_unit': 'lbf*in'},
        'ratio': {'imp_factor': 1, 'si_unit': '', 'imp_unit': ''},
    }

    def _unit_label(self, quantity_type: str, units: str = None) -> str:
        units = self.units if units is None else units.upper()
        if units not in ('SI', 'IMPERIAL'):
            raise ValueError("units must be either 'SI' or 'IMPERIAL'")
        info = self._unit_conversion.get(quantity_type)
        if info is None:
            return ''
        return info['si_unit'] if units == 'SI' else info['imp_unit']

    def convert_to_units(self, value, quantity_type: str, units: str = None):
        units = self.units if units is None else units.upper()
        if units not in ('SI', 'IMPERIAL'):
            raise ValueError("units must be either 'SI' or 'IMPERIAL'")
        info = self._unit_conversion.get(quantity_type)
        if info is None:
            raise ValueError(f"Unknown quantity_type '{quantity_type}'")

        if value is None:
            return None
        if isinstance(value, Physical):
            target_unit = info['si_unit'] if units == 'SI' else info['imp_unit']
            try:
                converted = value.to(target_unit)
                return float(converted.value)
            except Exception:
                return float(value.value)

        return value if units == 'SI' else value / info['imp_factor']

    def _analysis_quantity_type(self, method_name: str) -> str | None:
        name = method_name.lower()
        if 'moment' in name or 'bending' in name or 'torsion' in name:
            return 'moment'
        if 'force' in name or 'load' in name or 'normal' in name or 'shear' in name:
            return 'force'
        if 'slenderness' in name or 'ratio' in name:
            return 'ratio'
        return None

    def _convert_analysis_output(self, value, quantity_type: str):
        if quantity_type is None or value is None:
            return value
        if isinstance(value, (Physical, int, float)):
            return self.convert_to_units(value, quantity_type, self.units)
        return value

    def get_section_properties(self, units: str = None) -> dict:
        units = self.units if units is None else units.upper()
        if units not in ('SI', 'IMPERIAL'):
            raise ValueError("units must be either 'SI' or 'IMPERIAL'")

        return {
            'length': self.convert_to_units(self.length, 'length', units),
            'elastic_modulus': self.convert_to_units(self.elastic_modulus, 'stress', units),
            'f_yk': self.convert_to_units(self.f_yk, 'stress', units),
            'section_area': self.convert_to_units(self.section_area, 'area', units),
            'section_area_shear_y': self.convert_to_units(self.section_area_shear_y, 'area', units),
            'section_area_shear_z': self.convert_to_units(self.section_area_shear_z, 'area', units),
            'section_inertia_y': self.convert_to_units(self.section_inertia_y, 'inertia', units),
            'section_inertia_z': self.convert_to_units(self.section_inertia_z, 'inertia', units),
            'section_w_pl_y': self.convert_to_units(self.section_w_pl_y, 'section_modulus', units),
            'section_w_pl_z': self.convert_to_units(self.section_w_pl_z, 'section_modulus', units),
            'h_w': self.convert_to_units(self.h_w, 'length', units),
            't_w': self.convert_to_units(self.t_w, 'length', units),
            'b': self.convert_to_units(self.b, 'length', units),
            't_f': self.convert_to_units(self.t_f, 'length', units),
            'units': units,
        }

    def __repr__(self):
        props = self.get_section_properties(self.units)
        return (
            f"SteelBeam(Profile='{self.profile}' | units={props['units']} | "
            f"L={props['length']} {self._unit_label('length')} | "
            f"E={props['elastic_modulus']} {self._unit_label('stress')} | "
            f"f_yk={props['f_yk']} {self._unit_label('stress')} | "
            f"A={props['section_area']} {self._unit_label('area')} | "
            f"Iy={props['section_inertia_y']} {self._unit_label('inertia')} | "
            f"Iz={props['section_inertia_z']} {self._unit_label('inertia')} | "
            f"Wpl_y={props['section_w_pl_y']} {self._unit_label('section_modulus')} | "
            f"Wpl_z={props['section_w_pl_z']} {self._unit_label('section_modulus')} | "
            f"h_w={props['h_w']} {self._unit_label('length')} | "
            f"t_w={props['t_w']} {self._unit_label('length')} | "
            f"b={props['b']} {self._unit_label('length')} | "
            f"t_f={props['t_f']} {self._unit_label('length')})"
        )

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
                bound_method = types.MethodType(attr, self)
                quantity_type = self._analysis_quantity_type(name)

                if quantity_type is not None:
                    def make_wrapper(bound, q_type):
                        @functools.wraps(bound)
                        def wrapper(*args, **kwargs):
                            result = bound(*args, **kwargs)
                            return self._convert_analysis_output(result, q_type)
                        return wrapper

                    setattr(self, name, make_wrapper(bound_method, quantity_type))
                else:
                    setattr(self, name, bound_method)

                self._analysis_methods.add(name)

        return


