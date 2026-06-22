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


# ==================== SECTION CLASSIFICATION ====================

def classify_section_AISC(self, cases:list[int], stress_type:str ='Axial Compression'):
    """
    Section classification based on Table B4.1a and Table B4.1b of AISC 360-22.

    Parameters
    case: number of the case defined in Tables, 1 to 21
    stress_type: Axial Compression or Flexure
    """
    if stress_type not in ['Axial Compression', 'Flexure']:
        raise ValueError("Stress type must be one of 'Axial Compression' or 'Flexure'")

    # Map of the width and thickness consideration and λ_r limits for each case (AISC 360-22 Table B4.1a and B4.1b)
    _LAMBD_ACTUAL_COMPRESSION = {
        1: ((self.b/2), self.t_f),
        2: (self.b, self.t_f),
        3: (self.b, self.t_f),
        4: (self.h_w, self.t_f),
        5: (self.h_w, self.t_w),
        6: ((self.b - 2*self.t_w), self.t_w),
        7: (self.b, self.t_f),
        8: (self.b, self.t_f),
        9: (self.b, self.t_f)
    }
    _LIMIT_FACTORS_COMPRESSION = {
        1: 0.56,
        2: None,
        3: 0.45,
        4: 0.75,
        5: 1.49,
        6: 1.40,
        7: 1.40,
        8: 1.49,
        9: 0.11
    }
    _LAMBD_ACTUAL_FLEXURE = {
        10: (self.b, self.t_f),
        11: (self.b, self.t_f),
        12: (self.b, self.t_f),
        13: (self.b, self.t_f),
        14: (self.b, self.t_f),
        15: (self.b, self.t_f),
        16: (self.b, self.t_f),
        17: (self.b, self.t_f),
        18: (self.b, self.t_f),
        19: (self.b, self.t_f),
        20: (self.b, self.t_f),
        21: (self.b, self.t_f)
    }
    _LIMIT_FACTORS_FLEXURE = {
        10: (0.38, 1.00),
        11: (0.38, 0.95),
        12: (0.54, 0.91),
        13: (0.38, 1.00),
        14: (0.84, 1.52),
        15: (3.76, 5.70),
        16: (0.38, 5.70),
        17: (1.12, 1.40),
        18: (1.12, 1.40),
        19: (2.42, 5.70),
        20: (0.07, 0.31),
        21: (1.12, 1.49)
    }

    valid_cases = list(_LIMIT_FACTORS_COMPRESSION.keys()) + list(_LIMIT_FACTORS_FLEXURE.keys())    
    for case in cases:
        if case not in valid_cases:
            raise ValueError(f"Case {case} not valid")
        
    results = {}
    verifications = []
    lambd_actual = {}

    if stress_type == 'Axial Compression':    
        for case in cases:
            lambd_actual[case] = {'case':case,
                'b': _LAMBD_ACTUAL_COMPRESSION[case][0],
                't': _LAMBD_ACTUAL_COMPRESSION[case][1],
                'lambd':_LAMBD_ACTUAL_COMPRESSION[case][0] / _LAMBD_ACTUAL_COMPRESSION[case][1]}
            
            factor_c = _LIMIT_FACTORS_COMPRESSION[case]

            if factor_c is None:
                results[case] = {'case_number': case, 'classification': 'Manual Required'}
                verifications.append('Manual')
                continue

            lambd_r = factor_c * sqrt(self.elastic_modulus / self.f_yk)
            classification = 'Slender' if lambd_actual[case]['lambd'] > lambd_r else 'Non-Slender'
            verifications.append(classification)
            
            results[case] = {
                'case_number': case,
                'stress_type': stress_type,
                'lambd_actual': round(float(lambd_actual[case]['lambd']), 3),
                'lambd_r-AISC_factor': factor_c,
                'lambd_r': round(float(lambd_r), 3),
                'classification': classification
            }
    
    elif stress_type == 'Flexure':
        for case in cases:
            lambd_actual[case] = {'case':case,
                'b': _LAMBD_ACTUAL_FLEXURE[case][0],
                't': _LAMBD_ACTUAL_FLEXURE[case][1],
                'lambd':_LAMBD_ACTUAL_FLEXURE[case][0] / _LAMBD_ACTUAL_FLEXURE[case][1]}
            
            factor_p, factor_r = _LIMIT_FACTORS_FLEXURE[case]
            lambd_p_computed = factor_p * sqrt(self.elastic_modulus / self.f_yk)
            lambd_r_computed = factor_r * sqrt(self.elastic_modulus / self.f_yk)
            
            if lambd_actual[case]['lambd'] <= lambd_p_computed:
                classification = 'Compact'
            elif lambd_actual[case]['lambd'] <= lambd_r_computed:
                classification = 'Non-Compact'
            else:
                classification = 'Slender'
            verifications.append(classification)
            
            results[case] = {
                'case_number': case,
                'stress_type': stress_type,
                'lambd_actual': round(float(lambd_actual[case]['lambd']),3),
                'lambd_p_factor': factor_p,
                'lambd_r_factor': factor_r,
                'lambd_p': round(float(lambd_p_computed),3),
                'lambd_r': round(float(lambd_r_computed),3),
                'classification': classification
            }
    
    # Determine overall classification (most restrictive)
    if 'Slender' in verifications:
        overall_classification = 'Slender'
    elif 'Non-Slender' in verifications or 'Compact' in verifications:
        overall_classification = 'Non-Slender/Compact'
    else:
        overall_classification = verifications[0] if verifications else 'Unknown'
    
    self.section_classification = overall_classification

    return results, overall_classification

# ==================== CALCULATION ====================

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

    if not hasattr(self, 'section_classification'):
        raise ValueError("The section is not classified yet, please run first classify_section_AISC")

    if self.section_classification == 'Non-Slender/Compact' or 'Manual':

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
