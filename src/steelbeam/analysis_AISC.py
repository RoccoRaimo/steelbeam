"""
steelbeam - Eng. Rocco Raimo
---
A python package for calculation of resistance and stability of steel beams, based on multiple national codes.
---

The module analysis_AISC.py contains the beam analysis for the beam object based on AISC and AASHTO.

"""

from handcalcs.decorator import handcalc
import handcalcs
handcalcs.set_option("custom_symbols", {"C": ","})

from math import pi
from numpy import sqrt

def classify_section_AISC(self):
    """
    Section classification
    """

    # Compression elements members subjected to Axial Compression (I-Shaped)
    b_f = (self.b - self.t_w)/2

    if b_f / self.t_f < 0.56 * sqrt(self.elastic_modulus / self.f_yk):
        self.section_class_compression_f = "Non slender"
    else:
        self.section_class_compression_f = "Slender"

    if self.h_w / self.t_w < 1.49 * sqrt(self.elastic_modulus / self.f_yk):
        self.section_class_compression_w = "Non slender"
    else:
        self.section_class_compression_w = "Slender"

    # Compression elements members subjected to Flexure (I-Shaped)

    if b_f / self.t_f < 0.38 * sqrt(self.elastic_modulus / self.f_yk):
        self.section_class_flexure_f = "Compact"
    else:
        self.section_class_flexure_f = "Non-Compact"

    if self.h_w / self.t_w < 0.38 * sqrt(self.elastic_modulus / self.f_yk):
        self.section_class_flexure_w = "Compact"
    else:
        self.section_class_flexure_w = "Non-Compact"
    
    return

def normal_force_tension(self, a_net=None, u=1, render=False, preferred_units=None, precision=2):
    """

    AISC 360-22 - § D2
    AASHTO LRFD 10th Ed. - § 6.8.2
    
    """
    if a_net is None:
        a_net = self.section_area
    phi_y = self._partial_factors.get('phi_tension_yield')

    if render==False:
        a_e = a_net * u
        p_n = (a_e * self.f_yk).to_preferred(preferred_units)
        p_r = (phi_y * p_n).to_preferred(preferred_units)
        return p_r
    
    elif render==True:
        @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
        def render_instance(A_n, U, F_yk):
            """
            """
            A_e = A_n * U
            P_n = A_e * F_yk; P_n = (A_e * F_yk).to_preferred(preferred_units)
            P_r = phi_y * P_n; P_r = (phi_y * P_n).to_preferred(preferred_units)
        return render_instance(a_net, u, self.f_yk)         
        

def normal_force_compression(self, k = 1.0, render=False, preferred_units=None, precision=2):
    """

    AISC 360-22 - § E3
    AASHTO LRFD 10th Ed. - § 6.9.2
    
    """
    phi_c = self._partial_factors.get('phi_compression')

    if render==False:
        p_0 = (self.section_area * self.f_yk).to_preferred(preferred_units)
        p_e_y = ((pi**2 * self.elastic_modulus * self.section_area) / (k * self.length / self.section_radius_gyration_y)**2).to_preferred(preferred_units)
        p_e_z = ((pi**2 * self.elastic_modulus * self.section_area) / (k * self.length / self.section_radius_gyration_z)**2).to_preferred(preferred_units)
        p_e = (min(p_e_y, p_e_z)).to_preferred(preferred_units)
        if p_0 / p_e <= 2.25:
            p_n = (0.658**(p_0 / p_e ) * p_0).to_preferred(preferred_units)
        else:
            p_n = (0.877 * p_e).to_preferred(preferred_units)
        p_r = (phi_c * p_n).to_preferred(preferred_units)
        return p_r

    elif render==True:
        @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
        def render_instance(A, f_yk, E, L, r_y, r_z, k, phi_c):
            """
            """
            P_0 = A * f_yk; P_0 = (A * f_yk).to_preferred(preferred_units)
            P_eCy = (pi**2 * E * A) / (k * L / r_y)**2; P_eCy = ((pi**2 * E * A) / (k * L / r_y)**2).to_preferred(preferred_units)
            P_eCz = (pi**2 * E * A) / (k * L / r_z)**2; P_eCz = ((pi**2 * E * A) / (k * L / r_z)**2).to_preferred(preferred_units)
            P_e = min(P_eCy, P_eCz); P_e = (min(P_eCy, P_eCz)).to_preferred(preferred_units)
            if P_0 / P_e <= 2.25:
                P_n = 0.658**(P_0 / P_e) * P_0
            elif P_0 / P_e > 2.25:
                P_n = 0.877 * P_e
            P_r = phi_c * P_n; P_r = (phi_c * P_n).to_preferred(preferred_units)
        return render_instance(self.section_area, self.f_yk, self.elastic_modulus, self.length, self.section_radius_gyration_y, self.section_radius_gyration_z, k, phi_c)        
