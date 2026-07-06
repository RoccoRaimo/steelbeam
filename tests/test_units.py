#def test_initialization_user_defined_imperial(self):
#    """Imperial units conversion test for a user-defined profile"""
#    beam = sb.SteelBeam(
#        length=200,
#        elastic_modulus=210000,
#        f_yk=355,
#        profile="User defined",
#        units="imperial",
#        section_area=7.0,  # in²
#        section_area_shear_y=5.0,
#        section_area_shear_z=5.0,
#        section_inertia_y=0.5,  # in⁴
#        section_inertia_z=0.3,  # in⁴
#        section_w_pl_y=10.0,  # in³
#        section_w_pl_z=8.0,  # in³
#        h_w=8.0,  # in
#        t_w=0.25,
#        b=6.0,
#        t_f=0.25
#    )
#    assert beam.length == 200 * 25.4
#    assert beam.section_area == pytest.approx(7.0 * 645.16)
#    assert beam.h_w == pytest.approx(8.0 * 25.4)
#    assert beam.t_f == pytest.approx(0.25 * 25.4)
#
#def test_section_properties_output_units(self):
#    beam = sb.SteelBeam(
#        length=6000,
#        elastic_modulus=210000,
#        f_yk=355,
#        profile='User defined',
#        section_area=5000,
#        section_area_shear_y=3500,
#        section_area_shear_z=2500,
#        section_inertia_y=8.5e7,
#        section_inertia_z=2.0e7,
#        section_w_pl_y=650000,
#        section_w_pl_z=280000,
#        h_w=200,
#        t_w=8,
#        b=150,
#        t_f=12,
#        units='SI'
#    )
#    props = beam.get_section_properties()
#    assert props['units'] == 'SI'
#    assert props['section_area'] == 5000
#    assert 'mm' in beam.__repr__()
#
#def test_analysis_output_unit_conversion(self):
#    beam = sb.SteelBeam(
#        length=200,
#        elastic_modulus=210000,
#        f_yk=355,
#        profile='User defined',
#        units='imperial',
#        section_area=7.0,
#        section_area_shear_y=5.0,
#        section_area_shear_z=5.0,
#        section_inertia_y=0.5,
#        section_inertia_z=0.3,
#        section_w_pl_y=10.0,
#        section_w_pl_z=8.0,
#        h_w=8.0,
#        t_w=0.25,
#        b=6.0,
#        t_f=0.25
#    )
#    beam.analysis('EC')
#    moment_y = beam.bending_moment_y()
#    assert moment_y == pytest.approx(3.38e6, rel=1e-2)