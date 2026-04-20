"""
Test per le funzioni di resistenza EC3 - test_resistance_EC3.py
"""

import pytest
import sys
import os

src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, os.path.abspath(src_path))

import steelbeam
from steelbeam.steelbeam import SteelBeam
from steelbeam import analysis_EC


class TestNormalForceTension:
    """Test per resistenza a trazione - EC3 § 6.2.3"""
    
    @pytest.fixture
    def beam(self):
        """Fixture per un beam di esempio"""
        return SteelBeam(
            length=5000,
            elastic_modulus=210000,
            f_yk=275,
            profile="User defined",
            section_area=5000,  # mm²
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
    
    def test_normal_force_tension_without_net_area(self, beam):
        """Test trazione senza area netta (usa area lorda)"""
        result = analysis_EC.normal_force_tension(beam)
        # N_plRd = A * f_yk / gamma_m0 = 5000 * 275 / 1.05 = 1309524 N
        expected = 5000 * 275 / 1.05
        assert abs(result - expected) < 1
    
    def test_normal_force_tension_with_net_area(self, beam):
        """Test trazione con area netta"""
        a_net = 4500  # mm²
        result = analysis_EC.normal_force_tension(beam, a_net=a_net)
        # N_plRd = 5000 * 275 / 1.05 = 1309524 N
        # N_uRd = 0.9 * 4500 * 275 / 1.25 = 891000 N
        # N_tRd = min(1309524, 891000) = 891000 N
        expected = 891000
        assert abs(result - expected) < 1
    
    def test_normal_force_tension_render_false(self, beam):
        """Test che render=False restituisca un valore numerico"""
        result = analysis_EC.normal_force_tension(beam, render=False)
        assert isinstance(result, (int, float))


class TestNormalForceCompression:
    """Test per resistenza a compressione - EC3 § 6.2.4"""
    
    @pytest.fixture
    def beam(self):
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
    
    def test_normal_force_compression(self, beam):
        """Test compressione semplice"""
        result = analysis_EC.normal_force_compression(beam)
        # N_cRd = A * f_yk / gamma_m0 = 5000 * 275 / 1.05 = 1309524 N
        expected = 5000 * 275 / 1.05
        assert abs(result - expected) < 1


class TestBendingMoment:
    """Test per resistenza a flessione - EC3 § 6.2.5"""
    
    @pytest.fixture
    def beam(self):
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
    
    def test_bending_moment_y(self, beam):
        """Test momento flettente asse y"""
        result = analysis_EC.bending_moment_y(beam)
        # M_cRd = W_pl * f_yk / gamma_m0 = 650000 * 275 / 1.05 = 170238 N·m
        expected = 650000 * 275 / 1.05 / 1000  # Converti in kN·m
        assert abs(result - expected) < 1
    
    def test_bending_moment_z(self, beam):
        """Test momento flettente asse z"""
        result = analysis_EC.bending_moment_z(beam)
        # M_cRd = W_pl * f_yk / gamma_m0 = 280000 * 275 / 1.05 = 73333 N·m
        expected = 280000 * 275 / 1.05 / 1000  # Converti in kN·m
        assert abs(result - expected) < 1


class TestShearResistance:
    """Test per resistenza a taglio - EC3 § 6.2.6"""
    
    @pytest.fixture
    def beam(self):
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
    
    def test_shear_y(self, beam):
        """Test resistenza a taglio asse y"""
        result = analysis_EC.shear_y(beam)
        # V_cRd = A_v * (f_yk / sqrt(3)) / gamma_m0
        # = 3500 * (275 / 1.732) / 1.05 = 526000 N
        expected = 3500 * (275 / 1.73205080757) / 1.05
        assert abs(result - expected) < 1
    
    def test_shear_z(self, beam):
        """Test resistenza a taglio asse z"""
        result = analysis_EC.shear_z(beam)
        # V_cRd = A_v * (f_yk / sqrt(3)) / gamma_m0
        # = 2500 * (275 / 1.732) / 1.05 = 375714 N
        expected = 2500 * (275 / 1.73205080757) / 1.05
        assert abs(result - expected) < 1


class TestBendingAxialInteraction:
    """Test per interazione flessione-axiale - EC3 § 6.2.9"""
    
    @pytest.fixture
    def beam(self):
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
    
    def test_bending_moment_axial_low_axial(self, beam):
        """Test interazione con bassa forza assiale"""
        # N_ed < 0.25 * N_plRd e N_ed < 0.5 * A_w * f_yk / gamma_m0
        n_ed = 100000  # N
        result = analysis_EC.bending_moment_axial_y(beam, n_ed=n_ed)
        # Deve restituire la capacità plastica completa
        expected = 650000 * 275 / 1.05 / 1000  # kN·m
        assert abs(result - expected) < 1
    
    def test_bending_moment_axial_high_axial(self, beam):
        """Test interazione con alta forza assiale"""
        n_ed = 500000  # N
        result = analysis_EC.bending_moment_axial_y(beam, n_ed=n_ed)
        # La capacità dovrebbe essere ridotta
        assert result > 0
        # M_NCy < M_plCy
        m_pl = 650000 * 275 / 1.05 / 1000
        assert result <= m_pl
    
    def test_bending_moment_axial_z_low_axial(self, beam):
        """Test interazione asse z con bassa forza assiale"""
        n_ed = 100000  # N
        result = analysis_EC.bending_moment_axial_z(beam, n_ed=n_ed)
        expected = 280000 * 275 / 1.05 / 1000  # kN·m
        assert abs(result - expected) < 1