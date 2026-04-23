"""
Test per la classe SteelBeam - test_steelbeam.py
"""

import pytest
import sys
import os

# Aggiungi il percorso del package src
src_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(src_path))

# Importa il package src come modulo
import src as steelbeam
from src import SteelBeam


class TestSteelBeamInitialization:
    """Test per l'inizializzazione della classe SteelBeam"""
    
    def test_initialization_with_profile(self):
        """Test inizializzazione con profilo dal database"""
        beam = SteelBeam(
            length=5000,
            elastic_modulus=210000,  # MPa
            f_yk=275,  # MPa (S275)
            profile="HEA 200"
        )
        assert beam.length == 5000
        assert beam.elastic_modulus == 210000
        assert beam.f_yk == 275
        assert beam.profile == "HEA 200"
    
    def test_initialization_user_defined(self):
        """Test inizializzazione con profilo definito dall'utente"""
        beam = SteelBeam(
            length=6000,
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
        assert beam.length == 6000
        assert beam.section_area == 5000
        assert beam.h_w == 200
        assert beam.t_w == 8
        assert beam.b == 150
        assert beam.t_f == 12

    def test_initialization_user_defined_imperial(self):
        """Test conversione delle unità imperiali per profilo definito dall'utente"""
        beam = SteelBeam(
            length=200,
            elastic_modulus=210000,
            f_yk=355,
            profile="User defined",
            units="imperial",
            section_area=7.0,  # in²
            section_area_shear_y=5.0,
            section_area_shear_z=5.0,
            section_inertia_y=0.5,  # in⁴
            section_inertia_z=0.3,  # in⁴
            section_w_pl_y=10.0,  # in³
            section_w_pl_z=8.0,  # in³
            h_w=8.0,  # in
            t_w=0.25,
            b=6.0,
            t_f=0.25
        )
        assert beam.length == 200 * 25.4
        assert beam.section_area == pytest.approx(7.0 * 645.16)
        assert beam.h_w == pytest.approx(8.0 * 25.4)
        assert beam.t_f == pytest.approx(0.25 * 25.4)

    def test_section_properties_output_units(self):
        beam = SteelBeam(
            length=6000,
            elastic_modulus=210000,
            f_yk=355,
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
        props = beam.get_section_properties()
        assert props['units'] == 'SI'
        assert props['section_area'] == 5000
        assert 'mm' in beam.__repr__()

    def test_analysis_output_unit_conversion(self):
        beam = SteelBeam(
            length=200,
            elastic_modulus=210000,
            f_yk=355,
            profile='User defined',
            units='imperial',
            section_area=7.0,
            section_area_shear_y=5.0,
            section_area_shear_z=5.0,
            section_inertia_y=0.5,
            section_inertia_z=0.3,
            section_w_pl_y=10.0,
            section_w_pl_z=8.0,
            h_w=8.0,
            t_w=0.25,
            b=6.0,
            t_f=0.25
        )
        beam.analysis('EC')
        moment_y = beam.bending_moment_y()
        assert moment_y == pytest.approx(3.38e6, rel=1e-2)

    def test_analysis_render_output_preserved(self):
        beam = SteelBeam(
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
    
    def test_shear_modulus_calculation(self):
        """Test calcolo modulo di taglio"""
        beam = SteelBeam(
            length=5000,
            elastic_modulus=210000,
            f_yk=275,
            profile="User defined",
            section_area=5000
        )
        # G = E / (2*(1+nu)) = 210000 / (2*1.3) = 80769 MPa
        expected_shear_modulus = 210000 / (2 * (1 + 0.3))
        assert abs(beam.shear_modulus - expected_shear_modulus) < 1


class TestSteelBeamDatabase:
    """Test per il caricamento del database profili"""
    
    def test_profile_list_not_empty(self):
        """Test che la lista profili non sia vuota"""
        from steelbeam import profile_list
        assert len(profile_list) > 0
    
    def test_profile_types_available(self):
        """Test che i tipi profilo siano disponibili"""
        from steelbeam import profile_type
        assert 'HEA' in profile_type
        assert 'HEB' in profile_type
        assert 'IPE' in profile_type


class TestSteelBeamPartialFactors:
    """Test per i fattori di sicurezza parziali"""
    
    def test_default_partial_factors(self):
        """Test fattori parziali di default"""
        beam = SteelBeam(
            length=5000,
            elastic_modulus=210000,
            f_yk=275,
            profile="User defined",
            section_area=5000
        )
        assert beam._partial_factors.get('gamma_m0') == 1.05
        assert beam._partial_factors.get('gamma_m2') == 1.25
    
    def test_custom_partial_factors(self):
        """Test fattori parziali personalizzati"""
        beam = SteelBeam(
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
    """Test per le proprietà della sezione"""
    
    @pytest.fixture
    def sample_beam(self):
        """Fixture per un beam di esempio"""
        return SteelBeam(
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
        """Test area della sezione"""
        assert sample_beam.section_area == 5000
    
    def test_section_inertia_y(self, sample_beam):
        """Test inerzia asse y"""
        assert sample_beam.section_inertia_y == 8.5e7
    
    def test_section_inertia_z(self, sample_beam):
        """Test inerzia asse z"""
        assert sample_beam.section_inertia_z == 2.0e7
    
    def test_plastic_modulus_y(self, sample_beam):
        """Test modulo plastico y"""
        assert sample_beam.section_w_pl_y == 650000
    
    def test_plastic_modulus_z(self, sample_beam):
        """Test modulo plastico z"""
        assert sample_beam.section_w_pl_z == 280000