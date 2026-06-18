"""
steelbeam - Eng. Rocco Raimo
---
A python package for calculation of resistance and stability of steel beams, based on multiple national codes.
---

The package can handle the use of units with the use of the library `pint`. 
The possible import options to use units are:

    # Explicit approach 
    import steelbeam as sb
    length = 10 * sb.m
    beam = sb.SteelBeam(...)

    # Direct approach
    from steelbeam import SteelBeam, m, MPa
    length = 10 * m
    beam = SteelBeam(...)

    # Native `pint` approach
    import steelbeam as sb
    from steelbeam.units import ureg
    length = 10 * ureg.m
    beam = sb.SteelBeam(...)
"""
__version__ = "0.1.0"

from .steelbeam import SteelBeam, profile_type, profile_list, database, get_profiles_by_type
from .units import (ureg, Quantity, m, mm, inch, MPa, ksi,)
import handcalcs

__all__ = [
    'SteelBeam',
    'profile_type',
    'profile_list',
    'database',
    'get_profiles_by_type',
    'Quantity',
    'ureg',
    'm','mm','inch',
    'MPa', 'ksi',
]

# GLOBAL FORMATTING CONFIGURATION

# Configure Pint for compact and scientific formatting (~#P)
# "~" = abbreviated (e.g. "m" instead of "meter"), "#" = scientific notation, "P" = pretty
ureg.formatter.default_format = "~#P"
# Configure handcalcs for your preferred LaTeX formatting (~L)
handcalcs.set_option("preferred_string_formatter", "~L")


