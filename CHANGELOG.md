## Changelog for v0.2.2
- Update European database with warping constant;
- Enhanced the bending_moment_buckling calculation with the use of warping constant into the critical elastic bending moment, for flexural-torsional stability check.

## Changelog for v0.2.1
- Update European database with the following:
  - Added missing 'r' key to the IPExxxO, IPExxxV for I_SECTION type;
  - Removed HxxxXxxx profiles for I_SECTION type;
  - Added missing key in L_SECTION and 2L_SECTION types and trimmed unused profiles;
  - Added missing key to the UPNxx profiles for C_SECTION and 2C_SECTION type and trimmed unused profiles.

## Changelog for v0.2.0

- Introduced the section classification, both for Eurocode and AISC
- Populated the AISC analysis with the following:
  - Normal force tension
  - Normal force compression
  - Flexure along y-axis
  - Shear along y-axis
- Introduced the plastic and warping analysis under the hood for section imported with the dxf through `sectionproperties` library
- Update the European profiles database
- General re-organization of the steelbeam module. 
  Now the loading of section geometry is handled with separated functions (for simpler debugging)
- Bumped tests for steelbeam and analysis_EC modules (in progress)
- First approach to the app GUI (still under development)