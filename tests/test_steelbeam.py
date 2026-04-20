"""
Test per la classe SteelBeam - test_steelbeam.py
"""

import pytest
import sys
import os

# Aggiungi il percorso del modulo src
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, os.path.abspath(src_path))

# Importa i moduli direttamente
import steelbeam
from steelbeam.steelbeam import SteelBeam


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