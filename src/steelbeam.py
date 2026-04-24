"""
steelbeam - Eng. Rocco Raimo
---
A python package for calculation of resistance and stability of steel beams, based on multiple national codes.

--
It is possible to show the Latex output of calculations inside Jupyter Notebook with the optional parameter "render" in every analysis method of SteelBeam.
"""

from . import units
from . import analysis_EC
from . import analysis_AISC
from . import analysis_NBR

from handcalcs.decorator import handcalc
import handcalcs
handcalcs.set_option("custom_symbols", {"C": ","})

from forallpeople import Physical

from math import pi
from math import sqrt
import os
import json
import types
import functools





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
                 section_inertia_torsional=0,
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
            section_inertia_torsional = torsional inertia of the steel section
            section_w_pl_y = plastic modulus of resistance around the y-axis
            section_w_pl_z = plastic modulus of resistance around the z-axis
            h_w = height of the web (for I-sections: h - 2*tf)
            t_w = thickness of the web
            b = width of the flange (base)
            t_f = thickness of the flange
            units = unit system for plain numeric inputs ('SI' or 'Imperial')

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
            raise ValueError("units must be either 'SI' or 'Imperial'")

        if isinstance(length, Physical):
            self.length = length
        elif self.units == 'SI':
            self.length = length * mm  # Assume input is in meters, convert to mm
        else:  # IMPERIAL
            self.length = length * inch  # Assume input is in inches

        if isinstance(elastic_modulus, Physical):
            self.elastic_modulus = elastic_modulus
        elif self.units == 'SI':
            self.elastic_modulus = elastic_modulus * MPa
        else:  # IMPERIAL
            self.elastic_modulus = elastic_modulus * ksi

        if isinstance(f_yk, Physical):
            self.f_yk = f_yk
        elif self.units == 'SI':
            self.f_yk = f_yk * MPa
        else:  # IMPERIAL
            self.f_yk = f_yk * ksi

        ni = 0.3
        self.shear_modulus = self.elastic_modulus / (2*(1+ni))

        self.profile = profile

        def _unit_value(value, si_unit, imperial_factor):
            if value is None:
                return None
            if isinstance(value, Physical):
                return value
            if self.units == 'SI':
                return value * si_unit
            return value * imperial_factor * si_unit

        self.section_area = _unit_value(section_area, mm**2, 645.16)
        self.section_area_shear_y = _unit_value(section_area_shear_y, mm**2, 645.16)
        self.section_area_shear_z = _unit_value(section_area_shear_z, mm**2, 645.16)
        self.section_inertia_y = _unit_value(section_inertia_y, mm**4, 416231.0597)
        self.section_inertia_z = _unit_value(section_inertia_z, mm**4, 416231.0597)
        self.section_inertia_torsional = _unit_value(section_inertia_torsional, mm**4, 416231.0597)
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
                        self.section_area = float(database[value_type][prof]['A']) * mm**2
                        self.section_area_shear_y = float(database[value_type][prof].get('Avy', database[value_type][prof].get('Avz', 0))) * mm**2
                        self.section_area_shear_z = float(database[value_type][prof]['Avz']) * mm**2
                        self.section_inertia_y = float(database[value_type][prof]['Iy']) * mm**4
                        self.section_inertia_z = float(database[value_type][prof].get('Iz', database[value_type][prof]['Iy'])) * mm**4
                        self.section_inertia_torsional = float(database[value_type][prof].get('It', database[value_type][prof]['It'])) * mm**4
                        self.section_w_pl_y = float(database[value_type][prof]['Wpl_y']) * mm**3
                        self.section_w_pl_z = float(database[value_type][prof].get('Wpl_z', database[value_type][prof]['Wpl_y'])) * mm**3
                    
                    # Handle dimensions based on section type
                    if value_type == 'CHS_SECTION':
                        self.h_w = float(database[value_type][prof]['OD']) * mm
                        self.t_w = float(database[value_type][prof]['TDES']) * mm
                        self.b = float(database[value_type][prof]['OD']) * mm
                        self.t_f = float(database[value_type][prof]['TDES']) * mm
                    elif value_type == 'RHS_SECTION':
                        self.h_w = float(database[value_type][prof]['Htot']) * mm
                        self.t_w = float(database[value_type][prof]['tw']) * mm
                        self.b = float(database[value_type][prof]['b']) * mm
                        self.t_f = float(database[value_type][prof]['tf']) * mm
                    else:
                        # For I-sections and others
                        self.h_w = (float(database[value_type][prof]['h']) - 2 * float(database[value_type][prof]['tf'])) * mm
                        self.t_w = float(database[value_type][prof]['tw']) * mm
                        if value_type in ['L_SECTION', '2L_SECTION', '2C_SECTION']:
                            self.b = float(database[value_type][prof]['b']) * mm
                        else:
                            self.b = float(database[value_type][prof]['bf']) * mm
                        self.t_f = float(database[value_type][prof]['tf']) * mm
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

    @property
    def input_units(self) -> dict:
        """
        Return the units used for the input values when creating the beam.
        
        Returns
        -------
        dict
            Dictionary with the unit labels for each quantity type as provided by the user.
        """
        if self.units == 'SI':
            return {
                'length': 'm',
                'area': 'mm²',
                'inertia': 'mm⁴',
                'section_modulus': 'mm³',
                'stress': 'MPa',
                'force': 'kN',
                'moment': 'kNm',
            }
        else:  # IMPERIAL
            return {
                'length': 'in',
                'area': 'in²',
                'inertia': 'in⁴',
                'section_modulus': 'in³',
                'stress': 'ksi',
                'force': 'lbf',
                'moment': 'lbf*in',
            }

    def get_input_unit(self, quantity_type: str) -> str:
        """Get the input unit for a specific quantity type."""
        return self.input_units.get(quantity_type, '')

    def _unit_label(self, quantity_type: str, units: str = None) -> str:
        """Return the unit label string for display purposes."""
        units = self.units if units is None else units.upper()
        if units not in ('SI', 'IMPERIAL'):
            raise ValueError("units must be either 'SI' or 'IMPERIAL'")
        
        info = self._unit_conversion.get(quantity_type)
        if info is None:
            return ''
        
        # Return formatted string representation
        unit_str = info['si_unit'] if units == 'SI' else info['imp_unit']
        # Convert ** to superscript for display
        return unit_str.replace('**2', '²').replace('**3', '³').replace('**4', '⁴')

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
                # Convert to the target unit string (e.g., 'mm**2')
                return value.to(target_unit)
            except Exception as e:
                # Fallback: try to interpret as base unit if conversion fails
                # This handles cases where the unit string might be slightly off
                return value
        
        # If value is numeric (shouldn't happen with fixed __init__), treat as base unit
        # and convert to target
        if units == 'SI':
            return value * eval(info['si_unit'])
        else:
            # Convert from SI base to Imperial
            si_val = value * eval(info['si_unit'])
            return si_val.to(info['imp_unit'])

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

        def get_val(attr, si_factor, imp_factor):
            """
            Helper to convert Physical object values to display units.
            si_factor: Multiplier to convert from Base (m, Pa) to SI Display (mm, MPa)
            imp_factor: Multiplier to convert from Base (m, Pa) to Imp Display (in, ksi)
            """
            val = getattr(self, attr)
            if val is None:
                return None
            
            if isinstance(val, Physical):
                base_value = val.value  # This is always in base units (m, Pa, etc.)
                
                if units == 'SI':
                    return base_value * si_factor
                else: # IMPERIAL
                    return base_value * imp_factor
            else:
                # Fallback if not a Physical object (shouldn't happen with fixed init)
                return val

        # Conversion Factors from Base Units (m, m2, m3, m4, Pa) to Display Units
        # SI Display: mm, mm2, mm3, mm4, MPa
        # Imp Display: in, in2, in3, in4, ksi
        
        # Length: m -> mm (x1000) | m -> in (/0.0254)
        len_si = 1000.0
        len_imp = 1.0 / 0.0254
        
        # Area: m2 -> mm2 (x1e6) | m2 -> in2 (/0.00064516)
        area_si = 1e6
        area_imp = 1.0 / 0.00064516
        
        # Inertia: m4 -> mm4 (x1e12) | m4 -> in4 (/4.16231e-10 approx)
        # 1 m = 39.3701 in. 1 m4 = 39.3701^4 in4 = 240250000 in4 approx
        # Actually: 1 m = 1000 mm. 1 m = 39.3700787 in.
        # 1 m4 = (39.3700787)^4 in4 = 240250000.0...
        # Let's use the exact conversion: 1 m = 39.37007874015748 in
        # 1 m4 = (39.37007874015748)**4
        inertia_si = 1e12
        inertia_imp = (1.0 / 0.0254) ** 4
        
        # Section Modulus: m3 -> mm3 (x1e9) | m3 -> in3
        mod_si = 1e9
        mod_imp = (1.0 / 0.0254) ** 3
        
        # Stress: Pa -> MPa (x1e-6) | Pa -> ksi (x1e-6 / 6.89476)
        # 1 ksi = 6.89476 MPa = 6.89476e6 Pa
        stress_si = 1e-6
        stress_imp = 1e-6 / 6.894757293168361

        return {
            'length': get_val('length', len_si, len_imp),
            'elastic_modulus': get_val('elastic_modulus', stress_si, stress_imp),
            'f_yk': get_val('f_yk', stress_si, stress_imp),
            'section_area': get_val('section_area', area_si, area_imp),
            'section_area_shear_y': get_val('section_area_shear_y', area_si, area_imp),
            'section_area_shear_z': get_val('section_area_shear_z', area_si, area_imp),
            'section_inertia_y': get_val('section_inertia_y', inertia_si, inertia_imp),
            'section_inertia_z': get_val('section_inertia_z', inertia_si, inertia_imp),
            'section_inertia_torsional': get_val('section_inertia_torsional', inertia_si, inertia_imp),
            'section_w_pl_y': get_val('section_w_pl_y', mod_si, mod_imp),
            'section_w_pl_z': get_val('section_w_pl_z', mod_si, mod_imp),
            'h_w': get_val('h_w', len_si, len_imp),
            't_w': get_val('t_w', len_si, len_imp),
            'b': get_val('b', len_si, len_imp),
            't_f': get_val('t_f', len_si, len_imp),
            'units': units,
            'input_units': self.input_units,
        }
    
    def __repr__(self):
        props = self.get_section_properties(self.units)
        
        def fmt(val):
            if val is None:
                return "None"
            # Check if the value is effectively an integer
            if isinstance(val, float) and val.is_integer():
                return f"{int(val)}"
            # If it's a float, format with up to 3 decimal places, stripping trailing zeros
            # This avoids scientific notation
            formatted = f"{val:.3f}".rstrip('0').rstrip('.')
            return formatted
        
        return (
            f"SteelBeam(Profile='{self.profile}' | units={props['units']} | "
            f"L={fmt(props['length'])} {self._unit_label('length')} | "
            f"E={fmt(props['elastic_modulus'])} {self._unit_label('stress')} | "
            f"f_yk={fmt(props['f_yk'])} {self._unit_label('stress')} | "
            f"A={fmt(props['section_area'])} {self._unit_label('area')} | "
            f"Iy={fmt(props['section_inertia_y'])} {self._unit_label('inertia')} | "
            f"Iz={fmt(props['section_inertia_z'])} {self._unit_label('inertia')} | "
            f"It={fmt(props['section_inertia_torsional'])} {self._unit_label('inertia')} | "
            f"Wpl_y={fmt(props['section_w_pl_y'])} {self._unit_label('section_modulus')} | "
            f"Wpl_z={fmt(props['section_w_pl_z'])} {self._unit_label('section_modulus')} | "
            f"h_w={fmt(props['h_w'])} {self._unit_label('length')} | "
            f"t_w={fmt(props['t_w'])} {self._unit_label('length')} | "
            f"b={fmt(props['b'])} {self._unit_label('length')} | "
            f"t_f={fmt(props['t_f'])} {self._unit_label('length')})"
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
        partial_factors: partial factors values can be modified. Default ones are:
            'EC': {
                'gamma_m0': 1.05,
                'gamma_m1': 1.05,
                'gamma_m2': 1.25}
            'AISC': {},
            'NBR': {}
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


