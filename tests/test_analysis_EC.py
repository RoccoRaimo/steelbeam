"""
Test per la stabilità - test_stability.py
"""

import pytest
import sys
import os

src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, os.path.abspath(src_path))

from src.steelbeam import steelbeam as sb
from steelbeam import analysis_EC

class TestCustomPartialFactors:
    """Test for Partial Factors"""

    def test_custom_partial_factors(self):
        """Customised partial factor tests"""
        beam = sb.SteelBeam(
            length=5.0,
            elastic_modulus=210000,
            f_yk=275,
            profile="User defined",
            section_area=5000
        )
        custom_partial_factors = {
               'gamma_m0': 1.10,
               'gamma_m1': 1.20,
               'gamma_m2': 1.30}
        beam.analysis('EC', partial_factors = custom_partial_factors)

        assert beam._partial_factors.get('gamma_m0') == 1.10
        assert beam._partial_factors.get('gamma_m1') == 1.20
        assert beam._partial_factors.get('gamma_m2') == 1.30

class TestSectionClassification:

    def test_class_section_compression_1(self):
        """Section classification for stress type compression"""
        beam = sb.SteelBeam(
            length=5.0,
            elastic_modulus=210000,
            f_yk=275,
            profile="IPE200",
        )
        beam.analysis('EC')
        beam.classify_section_EC(cases=[1, 9], stress_type = 'Compression')

        assert beam.section_class_compression == pytest.approx(1, rel=1e-3)

    def test_class_section_compression_2(self):
        """Section classification for stress type compression

        Example E4.1 from 'Structural Steel Design to Eurocode 3 and AISC Specifications'
        by Bernuzzi Claudio, Cordova Benedetto  - page 121

        Steel Profile IPE 550 S 275 steel grade under compression load
        """
        beam = sb.SteelBeam(
            length=5.0,
            elastic_modulus=210000,
            f_yk=275,
            profile="IPE550",
        )
        beam.analysis('EC')
        classification = beam.classify_section_EC(cases=[1, 9], stress_type = 'Compression')
        
        assert classification[0][1]['classification'] == 'Class 4'      # for the web
        assert classification[0][9]['classification'] == 'Class 1'      # for the flanges
        assert beam.section_class_compression == pytest.approx(4, rel=1e-3)     # Global section class

    def test_class_section_compression_3(self):
        """Section classification for stress type compression

        Example A3.1 from  'Acciao - Manuale tecnico per il progetto delle strutture in acciaio e delle connessioni bullonate e saldate' 
        by Simone Caffè - 2nd Edition - page 114

        Steel Profile HE280B S 275 steel grade under compression load
        """
        beam = sb.SteelBeam(
            length=5.0,
            elastic_modulus=210000,
            f_yk=275,
            profile="HE280B",
        )
        beam.analysis('EC')
        classification = beam.classify_section_EC(cases=[1, 9], stress_type = 'Compression')
        
        # for the web
        assert classification[0][1]['c'] == pytest.approx(196, 0.1)    
        assert classification[0][1]['t'] == pytest.approx(10.5, 0.1)        
        assert classification[0][1]['slenderness ratio'] == pytest.approx(18.67, 0.1)         
        assert classification[0][1]['classification'] == 'Class 1'              

        assert classification[0][9]['c'] == pytest.approx(110.75, 0.1)    
        assert classification[0][9]['t'] == pytest.approx(18, 0.1)        
        assert classification[0][9]['slenderness ratio'] == pytest.approx(6.15, 0.1)         
        assert classification[0][9]['classification'] == 'Class 1'  

    def test_class_section_bending_1(self):
        """Section classification for stress type bending around y-axis

        Example A3.1 from  'Acciao - Manuale tecnico per il progetto delle strutture in acciaio e delle connessioni bullonate e saldate' 
        by Simone Caffè - 2nd Edition - page 114

        Steel Profile HE280B S 275 steel grade under compression load
        """
        beam = sb.SteelBeam(
            length=5.0,
            elastic_modulus=210000,
            f_yk=275,
            profile="IPE200",
        )
        beam.analysis('EC')
        classification = beam.classify_section_EC(cases=[1, 9], stress_type = 'Bending')

        assert classification[0][1]['classification'] == 'Class 1'  
        assert classification[0][9]['classification'] == 'Class 1'  


# class TestResistance:
#     def test_normal_force_compression_1(self):
#         """Beam resistance to normal force compression
# 
#         Example E5.1 from 'Structural Steel Design to Eurocode 3 and AISC Specifications'
#         by Bernuzzi Claudio, Cordova Benedetto  - page 140
# 
#         Steel Profile L 120x10 S 235 steel grade
#         """
#         beam = sb.SteelBeam(
#             length=5.0,
#             elastic_modulus=210000,
#             f_yk=235,
#             profile="L120X12",
#         )
#         beam.analysis('EC')

class TestBuckling:
    def test_normal_force_buckling(self):
        """Beam stability for compression load

        Example E6.1 from 'Structural Steel Design to Eurocode 3 and AISC Specifications'
        by Bernuzzi Claudio, Cordova Benedetto  - page 172

        Steel Profile  HE200B - S235 steel grade
        """
        beam = sb.SteelBeam(
            length=3.75,
            elastic_modulus=210000,
            f_yk=235,
            profile="HE200B",
        )
        beam.analysis('EC')
        normal_force_buckling = beam.normal_force_buckling(buckling_curve='a')
        assert normal_force_buckling.to('kN').magnitude == pytest.approx(1171.9, 10)


# class TestSlenderness:
#     """Test per la snellezza"""
#     
#     @pytest.fixture
#     def beam(self):
#         return SteelBeam(
#             length=5000,
#             elastic_modulus=210000,
#             f_yk=275,
#             profile="User defined",
#             section_area=5000,
#             section_area_shear_y=3500,
#             section_area_shear_z=2500,
#             section_inertia_y=8.5e7,
#             section_inertia_z=2.0e7,
#             section_w_pl_y=650000,
#             section_w_pl_z=280000,
#             h_w=200,
#             t_w=8,
#             b=150,
#             t_f=12
#         )
#     
#     def test_slenderness_relative(self, beam):
#         """Test snellezza relativa"""
#         result = analysis_EC.slenderness_relative(beam)
#         # λ = sqrt(A * f_yk / N_cr)
#         n_cr = analysis_EC.eulerian_critic_load(beam)
#         n_pl_rd = 5000 * 275 / 1.05
#         expected = (n_pl_rd / n_cr) ** 0.5
#         assert abs(result - expected) < 0.01
