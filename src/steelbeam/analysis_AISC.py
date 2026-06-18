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

# ----- RESISTANCE

def normal_force_tension(self, a_net=None, u=1, render=False, preferred_units=None, precision=3):
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
        

def normal_force_compression(self, render=False, preferred_units=None, precision=3):
    """

    AISC 360-22 - § E3
    AASHTO LRFD 10th Ed. - § 6.9.2
    
    """
    phi_c = self._partial_factors.get('phi_compression')

    if render==False:
        f_e = (pi**2 * self.elastic_modulus) / (l_c / r)**2
        if self.f_yk / f_e <= 2.25:
            p_n = (a_e * self.f_yk).to_preferred(preferred_units)
            
        p_r = (phi_c * p_n).to_preferred(preferred_units)
        return p_r
    
    elif render==True:
        @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
        def render_instance(A_n, U, F_yk):
            """
            """

            P_n = A_e * F_yk; P_n = (A_e * F_yk).to_preferred(preferred_units)
            P_r = phi_c * P_n; P_r = (phi_c * P_n).to_preferred(preferred_units)
        return render_instance(a_net, u, self.f_yk)        

# ----- STABILITY