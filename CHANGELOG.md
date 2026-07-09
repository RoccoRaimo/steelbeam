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