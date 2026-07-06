"""
Tests for the SteelBeam class - test_steelbeam.py
"""

import pytest
import sys
import os
from pathlib import Path

# Add the path to the src package
src_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(src_path))

# Import the src package as a module
from src.steelbeam import steelbeam as sb
from src.steelbeam.units import ureg

mm = ureg.mm
m = ureg.m
MPa = ureg.MPa

class TestSteelBeamInitialization:
    """Test for initialising the SteelBeam class"""
    
    def test_initialization_with_profile(self):
        """Initialisation test using a profile from the database"""
        beam = sb.SteelBeam(
            length=5.0,
            elastic_modulus=210000,  # MPa
            f_yk=275,  # MPa (S275)
            profile="HE200A"
        )
        assert beam.length == 5000 * mm
        assert beam.elastic_modulus == 210000 * MPa
        assert beam.f_yk == 275 * MPa
        assert beam.profile == "HE200A"
    
    def test_initialization_user_defined(self):
        """Initialisation test with a user-defined profile"""
        beam = sb.SteelBeam(
            length=6.0,
            elastic_modulus=210000,
            f_yk=355,
            profile="User defined",
            section_area=5000,  # mm²
            section_area_shear_y=3500,
            section_area_shear_z=2500,
            section_inertia_y=8.5e7,  # mm⁴
            section_inertia_z=2.0e7,  # mm⁴
            section_w_pl_y=650000,  # mm³
            section_w_pl_z=280000,  # mm³
            h_w=200,
            t_w=8,
            b=150,
            t_f=12
        )
        assert beam.length == 6000 * mm
        assert beam.section_area == 5000 * mm**2
        assert beam.h_w == 200 * mm
        assert beam.t_w == 8 * mm
        assert beam.b == 150 * mm
        assert beam.t_f == 12 * mm

    def test_analysis_render_output_preserved(self):
        beam = sb.SteelBeam(
            length=5000,
            elastic_modulus=210000,
            f_yk=275,
            profile='User defined',
            section_area=5000,
            section_area_shear_y=3500,
            section_area_shear_z=2500,
            section_inertia_y=8.5e7,
            section_inertia_z=2.0e7,
            section_w_pl_y=650000,
            section_w_pl_z=280000,
            h_w=200,
            t_w=8,
            b=150,
            t_f=12,
            units='SI'
        )
        beam.analysis('EC')
        rendered = beam.bending_moment_y(render=True)
        assert rendered is not None
        assert not isinstance(rendered, (int, float))

class TestSteelBeamDatabase:
    """Test for loading the profile database"""
    
    def test_profile_list_not_empty(self):
        """Check that the list of profiles is not empty"""
        from steelbeam import profile_list
        assert len(profile_list) > 0
    
    def test_profile_types_available(self):
        """Check whether the profile types are available"""
        from steelbeam import profile_type
        assert 'HEA' in profile_type
        assert 'HEB' in profile_type
        assert 'IPE' in profile_type


class TestSteelBeamPartialFactors:
    """Tests for partial safety factors"""
    
    def test_default_partial_factors(self):
        """Test fattori parziali di default"""
        beam = sb.SteelBeam(
            length=5000,
            elastic_modulus=210000,
            f_yk=275,
            profile="User defined",
            section_area=5000
        )
        assert beam._partial_factors.get('gamma_m0') == 1.05
        assert beam._partial_factors.get('gamma_m2') == 1.25
    
    def test_custom_partial_factors(self):
        """Customised partial factor tests"""
        beam = sb.SteelBeam(
            length=5000,
            elastic_modulus=210000,
            f_yk=275,
            profile="User defined",
            section_area=5000
        )
        beam.set_partial_factor('gamma_m0', 1.10)
        beam.set_partial_factor('gamma_m2', 1.30)
        assert beam._partial_factors.get('gamma_m0') == 1.10
        assert beam._partial_factors.get('gamma_m2') == 1.30


class TestSteelBeamSectionProperties:
    """"Cross-section property tests"""
    
    @pytest.fixture
    def sample_beam(self):
        """Fixtures for an example beam"""
        return sb.SteelBeam(
            length=5000,
            elastic_modulus=210000,
            f_yk=275,
            profile="User defined",
            section_area=5000,
            section_area_shear_y=3500,
            section_area_shear_z=2500,
            section_inertia_y=8.5e7,
            section_inertia_z=2.0e7,
            section_w_pl_y=650000,
            section_w_pl_z=280000,
            h_w=200,
            t_w=8,
            b=150,
            t_f=12
        )
    
    def test_section_area(self, sample_beam):
        """Section test area"""
        assert sample_beam.section_area == 5000
    
    def test_section_inertia_y(self, sample_beam):
        """Y-axis inertia test"""
        assert sample_beam.section_inertia_y == 8.5e7
    
    def test_section_inertia_z(self, sample_beam):
        """Z-axis inertia test"""
        assert sample_beam.section_inertia_z == 2.0e7
    
    def test_plastic_modulus_y(self, sample_beam):
        """Y-axis plastic module test"""
        assert sample_beam.section_w_pl_y == 650000
    
    def test_plastic_modulus_z(self, sample_beam):
        """Z-axis plastic module test"""
        assert sample_beam.section_w_pl_z == 280000

    def test_sectionproperties_geometry_dict(self):
        """Test sectionproperties geometry calculation from dictionary"""
        pytest.importorskip('sectionproperties')
        beam = sb.SteelBeam(
            length=6000,
            elastic_modulus=210000,
            f_yk=355,
            profile='User defined',
            section_properties_source='sectionproperties',
            section_geometry={
                'type': 'rectangular_section',
                'width': 100.0,
                'height': 200.0,
            },
            units='SI'
        )
        assert beam.section_area == pytest.approx(10000, rel=1e-3)
        assert beam.section_inertia_y == pytest.approx(66666666.6667, rel=1e-3)
        assert beam.section_inertia_z == pytest.approx(16666666.6667, rel=1e-3)

    def test_sectionproperties_geometry_dxf(self):
        """Test sectionproperties geometry calculation from DXF file"""
        pytest.importorskip('sectionproperties')
        dxf_path = Path(__file__).resolve().parents[1] / 'Sketch' / 'sectionproperties' / '_DXF' / '240314_Sez4_SEG 13ME.dxf'
        if not dxf_path.exists():
            pytest.skip(f"DXF test file not found: {dxf_path}")
        beam = sb.SteelBeam(
            length=6000,
            elastic_modulus=210000,
            f_yk=355,
            profile='User defined',
            section_properties_source='sectionproperties',
            section_geometry=str(dxf_path),
            units='SI'
        )
        assert beam.section_area > 0
        assert beam.section_inertia_y > 0
        assert beam.section_inertia_z > 0