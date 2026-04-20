"""
Test per la stabilità - test_stability.py
"""

import pytest
import sys
import os

src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, os.path.abspath(src_path))

import steelbeam
from steelbeam.steelbeam import SteelBeam
from steelbeam import analysis_EC


class TestEulerianCriticalLoad:
    """Test per carico critico Euleriano - EC3 § 6.3.1"""
    
    @pytest.fixture
    def beam(self):
        return SteelBeam(
            length=5000,
            elastic_modulus=210000,  # MPa
            f_yk=275,
            profile="User defined",
            section_area=5000,
            section_area_shear_y=3500,
            section_area_shear_z=2500,
            section_inertia_y=8.5e7,  # mm⁴
            section_inertia_z=2.0e7,  # mm⁴
            section_w_pl_y=650000,
            section_w_pl_z=280000,
            h_w=200,
            t_w=8,
            b=150,
            t_f=12
        )
    
    def test_eulerian_critic_load(self, beam):
        """Test carico critico Euler"""
        result = analysis_EC.eulerian_critic_load(beam)
        # N_cr = π² * E * I / L²
        # Per y: π² * 210000 * 8.5e7 / 5000² = 22390000 N = 22390 kN
        # Per z: π² * 210000 * 2.0e7 / 5000² = 5270000 N = 5270 kN
        # Min = 5270 kN
        import math
        n_cr_y = (math.pi**2 * 210000 * 8.5e7) / (5000**2)
        n_cr_z = (math.pi**2 * 210000 * 2.0e7) / (5000**2)
        expected = min(n_cr_y, n_cr_z)
        assert abs(result - expected) < 1


class TestSlenderness:
    """Test per la snellezza"""
    
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
    
    def test_slenderness_relative(self, beam):
        """Test snellezza relativa"""
        result = analysis_EC.slenderness_relative(beam)
        # λ = sqrt(A * f_yk / N_cr)
        n_cr = analysis_EC.eulerian_critic_load(beam)
        n_pl_rd = 5000 * 275 / 1.05
        expected = (n_pl_rd / n_cr) ** 0.5
        assert abs(result - expected) < 0.01


class TestBucklingResistance:
    """Test per resistenza a instabilità - EC3 § 6.3.1"""
    
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
    
    def test_normal_force_buckling_curve_c(self, beam):
        """Test resistenza a buckling con curva c"""
        result = analysis_EC.normal_force_buckling(beam, buckling_curve='c')
        # Deve essere minore del carico plastico
        n_pl_rd = 5000 * 275 / 1.05
        assert result > 0
        assert result < n_pl_rd
    
    def test_normal_force_buckling_curve_b(self, beam):
        """Test resistenza a buckling con curva b"""
        result = analysis_EC.normal_force_buckling(beam, buckling_curve='b')
        n_pl_rd = 5000 * 275 / 1.05
        assert result > 0
        assert result < n_pl_rd
    
    def test_normal_force_buckling_curve_a(self, beam):
        """Test resistenza a buckling con curva a"""
        result = analysis_EC.normal_force_buckling(beam, buckling_curve='a')
        n_pl_rd = 5000 * 275 / 1.05
        assert result > 0
        assert result < n_pl_rd


class TestBendingBuckling:
    """Test per instabilità flessionale"""
    
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
    
    def test_bending_moment_buckling_y(self, beam):
        """Test resistenza a buckling flessionale asse y"""
        result = analysis_EC.bending_moment_buckling_y(beam)
        # Deve essere minore della capacità plastica
        m_pl = 650000 * 275 / 1.10 / 1000  # kN·m
        assert result > 0
        assert result < m_pl