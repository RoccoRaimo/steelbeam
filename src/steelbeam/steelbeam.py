"""
steelbeam - Eng. Rocco Raimo
---
A python package for calculation of resistance and stability of steel beams, based on multiple national codes.
---

The module steelbeam.py contains the general SteelBeam class that represents the steel beam object.
"""

from . import units
from . import analysis_EC
from . import analysis_AISC
from . import analysis_NBR

import handcalcs
handcalcs.set_option("custom_symbols", {"C": ","})

from .geometry import load_sectionproperties_geometry, plot_sectionproperties_geometry
from .units import Quantity, m, mm, inch, MPa, ksi
from .units import convert_quantity_to_display
from .units import DISPLAY_UNITS

import os
import json
import types
import functools
import inspect
import pint
from pathlib import Path


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
    # ==================== CLASS CONSTANTS ====================
    # Attribute mapping -> quantity_type for automatic conversion
    ATTR_TO_QUANTITY_TYPE = {
        'elastic_modulus': 'stress',
        'f_yk': 'stress',
        'shear_modulus': 'stress',
        'length': 'length',
        'section_area': 'area',
        'section_area_shear_y': 'area',
        'section_area_shear_z': 'area',
        'section_inertia_y': 'inertia',
        'section_inertia_z': 'inertia',
        'section_inertia_torsional': 'inertia',
        'section_w_pl_y': 'section_modulus',
        'section_w_pl_z': 'section_modulus',
        'section_radius_gyration_y': 'length',
        'section_radius_gyration_z': 'length',
        'h_w': 'length',
        't_w': 'length',
        'b': 'length',
        't_f': 'length',
    }

    # Define default partial factors for the national codes
    _default_partial_factors = {
        'EC': {
            'gamma_m0': 1.05,
            'gamma_m1': 1.05,
            'gamma_m2': 1.25,
        },
        'AISC': {
            'phi_flexure': 1.00,
            'phi_shear': 1.00,
            'phi_compression': 0.95,
            'phi_tension_yield': 0.95
        },
        'NBR': {},
    }

    # ==================== INITIALIZATION ====================
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
                 section_properties_source='manual',
                 section_geometry=None,
                 section_mesh_size=100,
                 units='SI'):
        """
        Class that represents the steel beam object.
        
        Parameters
        ------------
        length: Length of the beam;
        elastic_modulus: Elastic modulus of the steel;
        f_yk: yielding tension for the steel;
        profile: The name of the considered section. It is possible to assign a 'User defined' section or choose a profile contained in the database.
            The list of profiles in the available database can be accessed with steelbeam.get_profiles_by_type('profile_type'), specifying one of the following type: 
                ['I_SECTION',
                'L_SECTION',
                'C_SECTION',
                'T_SECTION',
                'CHS_SECTION',
                'RHS_SECTION',
                '2L_SECTION',
                '2C_SECTION']
            
            In case of 'User defined' profile the following parameters can be defined: 

        section_properties_source: Source of user-defined section properties. Use 'manual' to provide properties directly or 'sectionproperties' to compute them from a section geometry using the sectionproperties library.
        section_geometry: Optional geometry specification for sectionproperties mode. Can be a sectionproperties Geometry object, a DXF file path, or a dictionary describing the section geometry. For DXF import use {'type': 'dxf', 'path': 'path/to/file.dxf'} or pass the file path directly.
        section_mesh_size: Optional mesh size for sectionproperties geometry mesh generation.

            USER DEFINED SECTION TEMPLATE (copy and paste as starting point):
            -------------------------------------------------------------------
            SteelBeam(
                length=6.0,                           # Length in meters (SI) or inches (Imperial)
                elastic_modulus=210000,               # E in MPa (SI) or ksi (Imperial)
                f_yk=355,                             # Yield strength in MPa (SI) or ksi (Imperial)
                profile='User defined',
                
                # Section properties (all values in SI units: mm, mm², mm³, mm⁴ or in, in², in³, in⁴)
                section_area=7808,                    # Gross area of the steel section [mm² or in²]
                section_area_shear_y=4800,            # Shear area along y-axis [mm² or in²]
                section_area_shear_z=2400,            # Shear area along z-axis [mm² or in²]
                section_inertia_y=35100000,           # Inertia around y-axis (principal) [mm⁴ or in⁴]
                section_inertia_z=2100000,            # Inertia around z-axis (secondary) [mm⁴ or in⁴]
                section_inertia_torsional=500000,     # Torsional inertia [mm⁴ or in⁴]
                section_w_pl_y=420000,                # Plastic modulus around y-axis [mm³ or in³]
                section_w_pl_z=85000,                 # Plastic modulus around z-axis [mm³or in³]
                
                # Geometric dimensions (optional, for detailed calculations)
                h_w=240,                              # Height of the web [mm or in]
                t_w=8,                                # Thickness of the web [mm or in]
                b=150,                                # Width of the flange [mm or in]
                t_f=12,                               # Thickness of the flange [mm or in]
                
                units='SI'                            # 'SI' or 'Imperial'
            )
            -------------------------------------------------------------------

            All 'User defined' parameters can be provided as plain numeric values or as
            unit-aware `Quantity` objects. When `units='SI'`, numeric inputs are
            interpreted as **meters** for length and **MPa** for stress. When
            `units='Imperial'`, numeric inputs are interpreted as **inches** for
            length and **ksi** for stress.

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

        # Store internally in SI (with the prefix _)
        self._units = self.units
        
        ni = 0.3

        # Normalise and store all attributes
        self._length = self._normalize_to_si(length, m, 1.0, 'length')
        self._elastic_modulus = self._normalize_to_si(elastic_modulus, MPa, 1.0, 'stress')
        self._f_yk = self._normalize_to_si(f_yk, MPa, 1.0, 'stress')
        self._shear_modulus = self._elastic_modulus / (2*(1+ni))
        
        self.profile = profile
        self._section_properties_source = section_properties_source
        self._section_geometry = section_geometry
        self._section_mesh_size = section_mesh_size
        self._sectionproperties_geom = None
        self._sectionproperties_section = None

        self._section_area = None
        self._section_area_shear_y = None
        self._section_area_shear_z = None
        self._section_inertia_y = None
        self._section_inertia_z = None
        self._section_inertia_torsional = None
        self._section_w_pl_y = None
        self._section_w_pl_z = None
        self._section_radius_gyration_y = None
        self._section_radius_gyration_z = None
        self._h_w = None
        self._t_w = None
        self._b = None
        self._t_f = None

        if self.profile == 'User defined':
            if self._section_properties_source == 'manual':
                self._normalize_section_properties(
                    section_area=section_area,
                    section_area_shear_y=section_area_shear_y,
                    section_area_shear_z=section_area_shear_z,
                    section_inertia_y=section_inertia_y,
                    section_inertia_z=section_inertia_z,
                    section_inertia_torsional=section_inertia_torsional,
                    section_w_pl_y=section_w_pl_y,
                    section_w_pl_z=section_w_pl_z,
                    h_w=h_w,
                    t_w=t_w,
                    b=b,
                    t_f=t_f,
                )
            elif self._section_properties_source == 'sectionproperties':
                self._load_from_sectionproperties()
            else:
                raise ValueError("section_properties_source must be either 'manual' or 'sectionproperties'")
            return

        self._load_from_database()

    # ==================== PRIVATE SECTION LOADING HELPERS ====================
    def _load_from_sectionproperties(self):
        """Load section properties from a sectionproperties geometry source."""
        geom, section, geometry_dims = load_sectionproperties_geometry(
            self._section_geometry,
            self._section_mesh_size,
            self.units,
        )
        self._sectionproperties_geom = geom
        self._sectionproperties_section = section

        area = section.get_area()
        ixx_c, iyy_c, ixy_c = section.get_ic()
        rx, ry = section.get_rc()
        sxx, syy = section.get_s()

        j = None
        try:
            section.calculate_warping_properties()
            j = section.get_j()
        except Exception:
            j = None

        self._section_area = float(area) * mm**2
        self._section_inertia_y = float(ixx_c) * mm**4
        self._section_inertia_z = float(iyy_c) * mm**4
        self._section_inertia_torsional = float(j) * mm**4 if j is not None else None
        self._section_w_pl_y = float(sxx) * mm**3
        self._section_w_pl_z = float(syy) * mm**3
        self._section_radius_gyration_y = float(rx) * mm
        self._section_radius_gyration_z = float(ry) * mm


        if geometry_dims:
            self._h_w = geometry_dims.get('h_w')
            self._t_w = geometry_dims.get('t_w')
            self._b = geometry_dims.get('b')
            self._t_f = geometry_dims.get('t_f')

    def _load_from_database(self):
        """Load section properties from the profile database."""
        profile_found_in_db = False
        target_value_type = None

        for value_type, profiles_dict in database.items():
            if self.profile in profiles_dict:
                profile_found_in_db = True
                target_value_type = value_type
                break
        if not profile_found_in_db:
            raise ValueError(f"Profile '{self.profile}' not found in the database. Please use 'User defined'!")

        db_entry = database[target_value_type][self.profile]

        try:
            self._section_area = float(db_entry['A']) * mm**2
            self._section_area_shear_y = float(db_entry.get('Avy', db_entry.get('Avz', 0))) * mm**2
            self._section_area_shear_z = float(db_entry.get('Avz', 0)) * mm**2
            self._section_inertia_y = float(db_entry['Iy']) * mm**4
            self._section_inertia_z = float(db_entry.get('Iz', db_entry.get('Iy', 0))) * mm**4
            self._section_inertia_torsional = float(db_entry.get('It', 0)) * mm**4
            self._section_w_pl_y = float(db_entry['Wpl_y']) * mm**3
            self._section_w_pl_z = float(db_entry.get('Wpl_z', db_entry.get('Wpl_y', 0))) * mm**3
            self._section_radius_gyration_y = float(db_entry['i_y']) * mm
            self._section_radius_gyration_z = float(db_entry['i_z']) * mm
            
            # Handling specific dimensions
            if target_value_type == 'CHS_SECTION':
                self._h_w = float(db_entry['OD']) * mm
                self._t_w = float(db_entry['TDES']) * mm
                self._b = float(db_entry['OD']) * mm
                self._t_f = float(db_entry['TDES']) * mm
            elif target_value_type == 'RHS_SECTION':
                # Make sure these keys exist in RHS database
                self._h_w = float(db_entry['Htot']) * mm
                self._t_w = float(db_entry['tw']) * mm
                self._b = float(db_entry['b']) * mm
                self._t_f = float(db_entry['tf']) * mm
            else:
                # I-sections and others
                self._h_w = (float(db_entry['h']) - 2 * float(db_entry['tf'])) * mm
                self._t_w = float(db_entry['tw']) * mm
                if target_value_type in ['L_SECTION', '2L_SECTION', '2C_SECTION']:
                    self._b = float(db_entry['b']) * mm
                else:
                    self._b = float(db_entry['bf']) * mm
                self._t_f = float(db_entry['tf']) * mm
                
        except KeyError as e:
            raise ValueError(f"Missing key '{e}' in database entry for profile '{self.profile}'. Check the database structure.")

    # ==================== PRIVATE SECTION LOADING HELPERS ====================
    def _normalize_to_si(self, value, si_unit, imperial_factor, quantity_type):
        """Normalize a value to the base SI unit."""
        if value is None:
            return None
        if isinstance(value, Quantity):
            if quantity_type == 'stress':
                return value.to(MPa)
            if quantity_type == 'length':
                return value.to(mm)
            if quantity_type == 'area':
                return value.to(mm**2)
            if quantity_type == 'inertia':
                return value.to(mm**4)
            if quantity_type == 'section_modulus':
                return value.to(mm**3)
            return value
        if self.units == 'SI':
            return value * si_unit
        return value * imperial_factor * si_unit

    def _normalize_section_properties(
        self,
        section_area,
        section_area_shear_y,
        section_area_shear_z,
        section_inertia_y,
        section_inertia_z,
        section_inertia_torsional,
        section_w_pl_y,
        section_w_pl_z,
        h_w,
        t_w,
        b,
        t_f,
    ):
        """Normalize section properties from user-defined input values."""
        self._section_area = self._normalize_to_si(section_area, mm**2, 645.16, 'area')
        self._section_area_shear_y = self._normalize_to_si(section_area_shear_y, mm**2, 645.16, 'area')
        self._section_area_shear_z = self._normalize_to_si(section_area_shear_z, mm**2, 645.16, 'area')
        self._section_inertia_y = self._normalize_to_si(section_inertia_y, mm**4, 416231.0597, 'inertia')
        self._section_inertia_z = self._normalize_to_si(section_inertia_z, mm**4, 416231.0597, 'inertia')
        self._section_inertia_torsional = self._normalize_to_si(section_inertia_torsional, mm**4, 416231.0597, 'inertia')
        self._section_w_pl_y = self._normalize_to_si(section_w_pl_y, mm**3, 16387.064, 'section_modulus')
        self._section_w_pl_z = self._normalize_to_si(section_w_pl_z, mm**3, 16387.064, 'section_modulus')
        self._section_radius_gyration_y = (
            (self._section_inertia_y / self._section_area) ** 0.5
            if self._section_area and self._section_inertia_y else None
        )
        self._section_radius_gyration_z = (
            (self._section_inertia_z / self._section_area) ** 0.5
            if self._section_area and self._section_inertia_z else None
        )
        self._h_w = self._normalize_to_si(h_w, mm, 25.4, 'length')
        self._t_w = self._normalize_to_si(t_w, mm, 25.4, 'length')
        self._b = self._normalize_to_si(b, mm, 25.4, 'length')
        self._t_f = self._normalize_to_si(t_f, mm, 25.4, 'length')

    # ==================== MAGIC METHODS & PROPERTIES ====================
    def __getattr__(self, name):
        """
        Intercept attribute access for automatic unit conversion.
        
        Returns a Quantity object in the beam's display units, preserving
        the ability to perform further calculations.
        """
        # Avoid infinite loops for private attributes
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        
        # Check whether it is an attribute that needs to be converted
        if name in self.ATTR_TO_QUANTITY_TYPE:
            private_attr = f'_{name}'
            value = object.__getattribute__(self, private_attr)
            
            if value is None:
                return None
            
            if isinstance(value, Quantity):
                quantity_type = self.ATTR_TO_QUANTITY_TYPE[name]
                
                # Convert the ‘Quantity’ to display units (whilst retaining the ‘Quantity’ field)
                target_unit_str = DISPLAY_UNITS[self.units].get(quantity_type)
                if target_unit_str and target_unit_str != '':
                    try:
                        return value.to(target_unit_str)
                    except pint.DimensionalityError:
                        # Fallback: if the conversion fails, return the original value
                        return value
                return value
            
            return value
        
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        """
        Intercept attribute setting for automatic normalization to SI.
        
        When setting attributes like beam.elastic_modulus = 30*ksi,
        this method normalizes the value to SI units for internal storage.
        """
        # For private attributes and 'units', set as normal
        if name.startswith('_') or name == 'units':
            object.__setattr__(self, name, value)
            return
        
        # For mapped attributes, normalise to SI
        if name in self.ATTR_TO_QUANTITY_TYPE:
            quantity_type = self.ATTR_TO_QUANTITY_TYPE[name]
            private_attr = f'_{name}'
            
            if isinstance(value, Quantity):
                # Normalise to the appropriate base SI unit
                if quantity_type == 'stress':
                    value = value.to(MPa)
                elif quantity_type == 'length':
                    value = value.to(mm)
                elif quantity_type == 'area':
                    value = value.to(mm**2)
                elif quantity_type == 'inertia':
                    value = value.to(mm**4)
                elif quantity_type == 'section_modulus':
                    value = value.to(mm**3)
            
            object.__setattr__(self, private_attr, value)
        else:
            # For other attributes (e.g. profile, _analysis_methods, etc.), set them as normal
            object.__setattr__(self, name, value)

    def __repr__(self):
        props = self.get_section_properties(self.units)
        
        def fmt(val):
            if val is None:
                return "None"
            if isinstance(val, float) and val.is_integer():
                return f"{int(val)}"
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

    # ==================== UNITS HANDLING ====================
    @property
    def input_units(self) -> dict:
        """Return the units used for input values when creating the beam"""
        return units.INPUT_UNITS[self.units]

    def get_input_unit(self, quantity_type: str) -> str:
        """Get the input unit for a specific quantity type"""
        return units.get_input_unit(quantity_type, self.units)

    def _unit_label(self, quantity_type: str, display_units: str = None) -> str:
        """Return the unit label string for display purposes"""
        return units.get_unit_label(quantity_type, self.units if display_units is None else display_units)

    def _convert_to_units(self, value, quantity_type: str, display_units: str = None):
        """Convert a value to the display unit system."""
        if value is None:
            return value
        
        target_units = self.units if display_units is None else display_units.upper()
        
        # If it is already a Quantity, convert the units but keep the Quantity object
        if isinstance(value, Quantity):
            return units.convert_quantity_to_display(value, quantity_type, target_units)
        
        # If it is a simple number, create a Quantity before converting
        if isinstance(value, (int, float)):
            return value
        
        return value

    def _analysis_quantity_type(self, method_name: str) -> str | None:
        """Map analysis method names to quantity types."""
        name = method_name.lower()
        if 'moment' in name or 'bending' in name or 'torsion' in name:
            return 'moment'
        if 'force' in name or 'load' in name or 'normal' in name or 'shear' in name:
            return 'force'
        if 'slenderness' in name or 'ratio' in name:
            return 'ratio'
        return None

    def _convert_analysis_output(self, value, quantity_type: str, preferred_units: str = None):
        """
        Convert analysis output to the desired unit system.
        
        Parameters
        ----------
        value : Quantity or float
            The calculated result
        quantity_type : str
            Type of quantity ('force', 'moment', 'stress', etc.)
        preferred_units : str, optional
            Target unit system ('SI', 'IMPERIAL', or None to use self.units)
        
        Returns
        -------
        Quantity
            The result converted to the target unit system (preserving Quantity type)
        """
        if quantity_type is None or value is None:
            return None
        
        # If `preferred_units` is not specified, use the instance’s units
        target_units = preferred_units.upper() if preferred_units else self.units
        
        if target_units not in ('SI', 'IMPERIAL'):
            raise ValueError(f"Invalid unit system: {target_units}. Must be 'SI' or 'IMPERIAL'.")
        
        # If the value is not a Quantity, return it as it is
        if not isinstance(value, Quantity):
            return value
        
        # Map `quantity_type` to target units
        target_unit_str = DISPLAY_UNITS[target_units].get(quantity_type)
        
        if not target_unit_str or target_unit_str == '':
            # If no conversion is defined, return the original result
            return value
        
        try:
            return value.to(target_unit_str)
        except pint.DimensionalityError:
            # If the conversion fails, return the original result
            return value

    # ==================== SECTION & GEOMETRY ====================
    def get_section_properties(self, output_units: str = None) -> dict:
        target_units = self.units if output_units is None else output_units.upper()
        return units.get_section_properties(self, target_units)

    def plot_section(self,
                     geometry_kwargs: dict | None = None,
                     centroid_kwargs: dict | None = None):
        """Plot the section geometry and centroids for sectionproperties-defined sections."""
        if self.profile != 'User defined' or self._section_properties_source != 'sectionproperties':
            raise ValueError(
                "plot_section is available only when profile='User defined' and section_properties_source='sectionproperties'."
            )
        if self._sectionproperties_geom is None or self._sectionproperties_section is None:
            raise ValueError("Sectionproperties geometry has not been loaded; cannot plot section.")

        geometry_kwargs = geometry_kwargs or {}
        centroid_kwargs = centroid_kwargs or {}

        ax = self._sectionproperties_geom.plot_geometry(**geometry_kwargs)
        self._sectionproperties_section.plot_centroids(**centroid_kwargs)
        return ax

    # ==================== ANALYSIS ====================
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
                            # Bind args and kwargs to obtain the actual render flag.
                            signature = inspect.signature(bound)
                            bound_args = signature.bind_partial(*args, **kwargs)

                            preferred_units_for_result = self.units
                            if 'preferred_units' in signature.parameters:
                                preferred = bound_args.arguments.get('preferred_units', None)
                                if preferred is None:
                                    kwargs['preferred_units'] = units.get_preferred_units(self.units)
                                elif isinstance(preferred, str):
                                    preferred_units_for_result = preferred.upper()
                                    kwargs['preferred_units'] = units.get_preferred_units(preferred_units_for_result)
                                else:
                                    # Preserve custom preferred unit lists for pint.to_preferred.
                                    pass

                            render = bound_args.arguments.get('render', False)
                            if not render:
                                return bound(*args, **kwargs)

                            result = bound(*args, **kwargs)
                            return self._convert_analysis_output(result, q_type, preferred_units_for_result)

                        return wrapper

                    setattr(self, name, make_wrapper(bound_method, quantity_type))
                else:
                    setattr(self, name, bound_method)

                self._analysis_methods.add(name)

        return


