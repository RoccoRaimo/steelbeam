"""
steelbeam - Eng. Rocco Raimo
---
A python package for calculation of resistance and stability of steel beams, based on multiple national codes.
---

The module analysis_EC.py contains the beam analysis for the beam object based on Eurocodes.

"""

from handcalcs.decorator import handcalc
import handcalcs
handcalcs.set_option("custom_symbols", {"C": ","})

from math import pi
from numpy import sqrt

from .units import ureg

# ----- CLASSIFICATION

def classify_section_EC(self, cases:list[int], stress_type:str ='Compression', alpha = 0, psi = 0):
    """

    Section classification based on EC3 1993-1-1:2005 - § 5.5.

    Parameters
    case: number of the case defined in Tables, 1 to 21
    stress_type: 'Compression', 'Bending' or 'Compression-Bending'
    """

    if stress_type not in ['Compression', 'Bending', 'Compression-Bending']:
        raise ValueError("Stress type must be one of 'Compression', 'Bending' or 'Compression-Bending'")
    
    eps = sqrt(235 * ureg.MPa / self.f_yk)

    _COMPRESSION_PARTS = {
        1: (self.h_w, self.t_w),
        2: (self.h_w, self.t_w),
        3: (self.h_w, self.t_w),
        4: (self.h_w, self.t_w),
        5: (self.h_w, self.t_w),
        6: (self.h_w, self.t_w),
        7: (self.h_w, self.t_w),
        8: (self.h_w, self.t_w),
        9: ((self.b - self.t_w)/2 , self.t_f),
        10: (self.h_w, self.t_w),
        11: (self.h_w, self.t_w),
        12: (self.h_w, self.t_w),
        13: (self.h_w, self.t_w),
        14: (self.h_w, self.t_w)
    }

    valid_cases = list(_COMPRESSION_PARTS.keys())
    for case in cases:
        if case not in valid_cases:
            raise ValueError(f"Case {case} not valid")

    results = {}
    verifications_compression = []
    verifications_bending = []
    verifications_compressionbending = []
    slendernessratio_compression = {}
    slendernessratio_bending = {}
    slendernessratio_compressionbending = {}

    if stress_type == 'Compression':

        _SLENDERNESS_LIMIT_RATIOS_COMPRESSION = {
            1: {1:33*eps, 2: 38*eps, 3: 42*eps},
            2: {1:33*eps, 2: 38*eps, 3: 42*eps},
            3: {1:33*eps, 2: 38*eps, 3: 42*eps},
            4: {1:33*eps, 2: 38*eps, 3: 42*eps},
            5: {1:33*eps, 2: 38*eps, 3: 42*eps},
            6: {1:33*eps, 2: 38*eps, 3: 42*eps},
            7: {1:33*eps, 2: 38*eps, 3: 42*eps},
            8: {1:33*eps, 2: 38*eps, 3: 42*eps},
            9: {1:9*eps, 2: 10*eps, 3: 14*eps},
            10: {1:9*eps, 2: 10*eps, 3: 14*eps},
            11: {1:9*eps, 2: 10*eps, 3: 14*eps},
            12: {1:9*eps, 2: 10*eps, 3: 14*eps},
            13: {1:15*eps, 2: 15*eps, 3: 15*eps},
            14: {1:50*eps**2, 2: 70*eps**2, 3: 90*eps**2},
        }

        for case in cases:
            slendernessratio_compression[case] = {'case':case,
                'c': _COMPRESSION_PARTS[case][0],
                't': _COMPRESSION_PARTS[case][1],
                'slenderness ratio':_COMPRESSION_PARTS[case][0] / _COMPRESSION_PARTS[case][1]
            }

            if slendernessratio_compression[case]['slenderness ratio'] <= _SLENDERNESS_LIMIT_RATIOS_COMPRESSION[case][1]:
                classification = 1
            elif _SLENDERNESS_LIMIT_RATIOS_COMPRESSION[case][1] < slendernessratio_compression[case]['slenderness ratio'] <= _SLENDERNESS_LIMIT_RATIOS_COMPRESSION[case][2]:
                classification = 2
            elif _SLENDERNESS_LIMIT_RATIOS_COMPRESSION[case][2] < slendernessratio_compression[case]['slenderness ratio'] <= _SLENDERNESS_LIMIT_RATIOS_COMPRESSION[case][3]:
                classification = 3
            elif _SLENDERNESS_LIMIT_RATIOS_COMPRESSION[case][3] < slendernessratio_compression[case]['slenderness ratio']:
                classification = 4
            verifications_compression.append(classification)


            results[case] = {
                'case_number': case,
                'stress_type': stress_type,
                'slenderness limit ratios': {
                    str(limit_class): round(float(value.magnitude), 3) 
                    for limit_class, value in _SLENDERNESS_LIMIT_RATIOS_COMPRESSION[case].items()
                },
                'c': round(float(_COMPRESSION_PARTS[case][0].magnitude), 3),
                't': round(float(_COMPRESSION_PARTS[case][1].magnitude), 3),
                'slenderness ratio': round(float(slendernessratio_compression[case]['slenderness ratio']), 3),
                'classification': 'Class ' + str(classification)
            }
        
        if verifications_compression is not None and len(verifications_compression) > 0:
            classification_compression = str(max(verifications_compression))
            output = [results, 
                'Section Class for Compression: ' + classification_compression]
 
        self.section_class_compression = max(verifications_compression)

    elif stress_type == 'Bending':
        
        _SLENDERNESS_LIMIT_RATIOS_BENDING = {
            1: {1:72*eps, 2: 83*eps, 3: 124*eps},
            2: {1:72*eps, 2: 83*eps, 3: 124*eps},
            3: {1:72*eps, 2: 83*eps, 3: 124*eps},
            4: {1:72*eps, 2: 83*eps, 3: 124*eps},
            5: {1:72*eps, 2: 83*eps, 3: 124*eps},
            6: {1:72*eps, 2: 83*eps, 3: 124*eps},
            7: {1:72*eps, 2: 83*eps, 3: 124*eps},
            8: {1:72*eps, 2: 83*eps, 3: 124*eps},
            9: {1:9*eps, 2: 10*eps, 3: 14*eps},
            10: {1:9*eps, 2: 10*eps, 3: 14*eps},
            11: {1:9*eps, 2: 10*eps, 3: 14*eps},
            12: {1:9*eps, 2: 10*eps, 3: 14*eps},
            13: {1:15*eps, 2: 15*eps, 3: 15*eps},
            14: {1:50*eps**2, 2: 70*eps**2, 3: 90*eps**2},
        }

        for case in cases:
            slendernessratio_bending[case] = {'case':case,
                'c': _COMPRESSION_PARTS[case][0],
                't': _COMPRESSION_PARTS[case][1],
                'slenderness ratio':_COMPRESSION_PARTS[case][0] / _COMPRESSION_PARTS[case][1]
            }

            if slendernessratio_bending[case]['slenderness ratio'] <= _SLENDERNESS_LIMIT_RATIOS_BENDING[case][1]:
                classification = 1
            elif _SLENDERNESS_LIMIT_RATIOS_BENDING[case][1] < slendernessratio_bending[case]['slenderness ratio'] <= _SLENDERNESS_LIMIT_RATIOS_BENDING[case][2]:
                classification = 2
            elif _SLENDERNESS_LIMIT_RATIOS_BENDING[case][2] < slendernessratio_bending[case]['slenderness ratio'] <= _SLENDERNESS_LIMIT_RATIOS_BENDING[case][3]:
                classification = 3
            elif _SLENDERNESS_LIMIT_RATIOS_BENDING[case][3] < slendernessratio_bending[case]['slenderness ratio']:
                classification = 4
            verifications_bending.append(classification)

            results[case] = {
                'case_number': case,
                'stress_type': stress_type,
                'slenderness limit ratios': {
                    str(limit_class): round(float(value.magnitude), 3) 
                    for limit_class, value in _SLENDERNESS_LIMIT_RATIOS_BENDING[case].items()
                },
                'c': round(float(_COMPRESSION_PARTS[case][0].magnitude), 3),
                't': round(float(_COMPRESSION_PARTS[case][1].magnitude), 3),
                'slenderness ratio': round(float(slendernessratio_bending[case]['slenderness ratio']), 3),
                'classification': 'Class ' + str(classification)
            }

        if verifications_bending is not None and len(verifications_bending) > 0:
            classification_bending = str(max(verifications_bending))   
            output = [results, 
                    'Section Class for Bending: ' + classification_bending]

        self.section_class_bending = max(verifications_bending)

    elif stress_type == 'Compression-Bending':

        _SLENDERNESS_LIMIT_RATIOS_COMPRESSIONBENDING = {
            1: {1:[(396*eps)/(13*alpha-1), 36*eps/alpha], 2: [(456*eps)/(13*alpha-1), 41.5*eps/alpha], 3: [(42*eps)/(0.67+0.33*psi), 62*eps*(1-psi)*sqrt(-psi)]},
            2: {1:[(396*eps)/(13*alpha-1), 36*eps/alpha], 2: [(456*eps)/(13*alpha-1), 41.5*eps/alpha], 3: [(42*eps)/(0.67+0.33*psi), 62*eps*(1-psi)*sqrt(-psi)]},
            3: {1:[(396*eps)/(13*alpha-1), 36*eps/alpha], 2: [(456*eps)/(13*alpha-1), 41.5*eps/alpha], 3: [(42*eps)/(0.67+0.33*psi), 62*eps*(1-psi)*sqrt(-psi)]},
            4: {1:[(396*eps)/(13*alpha-1), 36*eps/alpha], 2: [(456*eps)/(13*alpha-1), 41.5*eps/alpha], 3: [(42*eps)/(0.67+0.33*psi), 62*eps*(1-psi)*sqrt(-psi)]},
            5: {1:[(396*eps)/(13*alpha-1), 36*eps/alpha], 2: [(456*eps)/(13*alpha-1), 41.5*eps/alpha], 3: [(42*eps)/(0.67+0.33*psi), 62*eps*(1-psi)*sqrt(-psi)]},
            6: {1:[(396*eps)/(13*alpha-1), 36*eps/alpha], 2: [(456*eps)/(13*alpha-1), 41.5*eps/alpha], 3: [(42*eps)/(0.67+0.33*psi), 62*eps*(1-psi)*sqrt(-psi)]},
            7: {1:[(396*eps)/(13*alpha-1), 36*eps/alpha], 2: [(456*eps)/(13*alpha-1), 41.5*eps/alpha], 3: [(42*eps)/(0.67+0.33*psi), 62*eps*(1-psi)*sqrt(-psi)]},
            8: {1:[(396*eps)/(13*alpha-1), 36*eps/alpha], 2: [(456*eps)/(13*alpha-1), 41.5*eps/alpha], 3: [(42*eps)/(0.67+0.33*psi), 62*eps*(1-psi)*sqrt(-psi)]},
            9: {1:(9*eps)/(alpha*sqrt(alpha)), 2: (10*eps)/(alpha*sqrt(alpha)), 3: None},
            10: {1:(9*eps)/(alpha*sqrt(alpha)), 2: (10*eps)/(alpha*sqrt(alpha)), 3: None},
            11: {1:(9*eps)/(alpha*sqrt(alpha)), 2: (10*eps)/(alpha*sqrt(alpha)), 3: None},
            12: {1:(9*eps)/(alpha*sqrt(alpha)), 2: (10*eps)/(alpha*sqrt(alpha)), 3: None},
            13: {1:None, 2: None, 3: None},
            14: {1:50*eps**2, 2: 70*eps**2, 3: 90*eps**2},
        }
        
        for case in cases:
            slendernessratio_compressionbending[case] = {'case':case,
                'c': _COMPRESSION_PARTS[case][0],
                't': _COMPRESSION_PARTS[case][1],
                'slenderness ratio':_COMPRESSION_PARTS[case][0] / _COMPRESSION_PARTS[case][1]
            }

            lim_1 = _SLENDERNESS_LIMIT_RATIOS_COMPRESSIONBENDING[case][1]
            val_1 = lim_1[0] if isinstance(lim_1, list) and alpha > 0.5 else (lim_1[1] if isinstance(lim_1, list) else lim_1)

            lim_2 = _SLENDERNESS_LIMIT_RATIOS_COMPRESSIONBENDING[case][2]
            val_2 = lim_2[0] if isinstance(lim_2, list) and alpha > 0.5 else (lim_2[1] if isinstance(lim_2, list) else lim_2)

            lim_3 = _SLENDERNESS_LIMIT_RATIOS_COMPRESSIONBENDING[case][3]
            val_3 = lim_3[0] if isinstance(lim_3, list) and alpha > 0.5 else (lim_3[1] if isinstance(lim_3, list) else lim_3)

            if slendernessratio_compressionbending[case]['slenderness ratio'] <= val_1:
                classification = 1
            elif slendernessratio_compressionbending[case]['slenderness ratio'] <= val_2:
                classification = 2
            elif slendernessratio_compressionbending[case]['slenderness ratio'] <= val_3:
                classification = 3
            else:
                classification = 4
            verifications_compressionbending.append(classification)

            results[case] = {
                'case_number': case,
                'stress_type': stress_type,
                'slenderness limit ratios': {
                    str(limit_class): [round(float(v.magnitude), 3) if hasattr(v, 'magnitude') else round(float(v), 3) for v in value] 
                                        if isinstance(value, list) and all(v is not None for v in value)
                                        else round(float(value.magnitude), 3) if value is not None and hasattr(value, 'magnitude')
                                        else round(float(value), 3) if value is not None
                                        else None
                    for limit_class, value in _SLENDERNESS_LIMIT_RATIOS_COMPRESSIONBENDING[case].items()
                },
                'c': round(float(_COMPRESSION_PARTS[case][0].magnitude), 3),
                't': round(float(_COMPRESSION_PARTS[case][1].magnitude), 3),
                'slenderness ratio': round(float(slendernessratio_compressionbending[case]['slenderness ratio']), 3),
                'classification': 'Class ' + str(classification)
            }

        if verifications_compressionbending is not None and len(verifications_compressionbending) > 0:
            classification_compressionbending = str(max(verifications_compressionbending))   
            output = [results, 
                    'Section Class for Compression-Bending: ' + classification_compressionbending]

        self.section_class_compressionbending = max(verifications_compressionbending)

    self.section_class = str(max(
        getattr(self, 'section_class_compression', 0),
        getattr(self, 'section_class_bending', 0),
        getattr(self, 'section_class_compressionbending', 0)
    ))

    return output


# ----- RESISTANCE

def normal_force_tension(self, a_net=None, render=False, preferred_units=None, precision=3):
    """

    EC3 1993-1-1:2005 - § 6.2.3
    
    """
    if a_net is None:
        a_net = self.section_area
    gamma_m0 = self._partial_factors.get('gamma_m0')
    gamma_m2 = self._partial_factors.get('gamma_m2')

    if render==False:
        n_pl = (self.section_area * self.f_yk / gamma_m0).to_preferred(preferred_units)
        n_u = (0.9 * a_net * self.f_yk / gamma_m2).to_preferred(preferred_units)
        normal_force_tension = (min(n_pl, n_u)).to_preferred(preferred_units)
        return normal_force_tension
        
    elif render==True:
        @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
        def render_instance(A, f_yk, A_net):
            """
            """
            N_plCRd = A * f_yk / gamma_m0; N_plCRd = (A * f_yk / gamma_m0).to_preferred(preferred_units)
            N_uCRd = 0.9 * A_net * f_yk / gamma_m2; N_uCRd = (0.9 * A_net * f_yk / gamma_m2).to_preferred(preferred_units)
            N_tCRd = min(N_plCRd, N_uCRd); N_tCRd = (min(N_plCRd, N_uCRd)).to_preferred(preferred_units)
        return render_instance(self.section_area, self.f_yk, a_net)
        

def normal_force_compression(self, override = 'No', render = False, preferred_units=None, precision: int = 3):
    """

    EC3 1993-1-1:2005 - § 6.2.4
    (ONLY CROSS-SECTIONS IN CLASS 1, 2 OR 3)

    """
    gamma_m0 = self._partial_factors.get('gamma_m0')

    if not hasattr(self, 'section_class') and override == 'No':
        raise ValueError("The section is not classified yet, please run first classify_section_EC")

    should_proceed = override == 'Yes' or getattr(self, 'section_class_compression', 999) <= 2
    if should_proceed:

        if render==False:
            normal_force_compression = (self.section_area * self.f_yk / gamma_m0).to_preferred(preferred_units)
            return normal_force_compression
        elif render==True:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(A, f_yk):
                """
                """
                N_cCRd = A * f_yk / gamma_m0; N_cCRd = (A * f_yk / gamma_m0).to_preferred(preferred_units)
            return render_instance(self.section_area, self.f_yk)  
    
    else:
       raise ValueError(f"The section is in class {self.section_class_compression}. Please, proceed with manual calculation") 

def bending_moment_y(self, render = False, preferred_units=None, precision: int = 3):
    """
    Bending moment around y axis (along z axis)
    EC3 1993-1-1:2005 - § 6.2.5
    (ONLY CROSS-SECTIONS IN CLASS 1 OR 2)

    """
    gamma_m0 = self._partial_factors.get('gamma_m0')
    if render==False:
        bending_moment_y = (self.section_w_pl_y * self.f_yk / gamma_m0).to_preferred(preferred_units)
        return bending_moment_y
    elif render==True:
        @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
        def render_instance(W_plCy, f_yk):
            """
            """
            M_cCRdCy = W_plCy * f_yk / gamma_m0; M_cCRdCy = (W_plCy * f_yk / gamma_m0).to_preferred(preferred_units)
        return render_instance(self.section_w_pl_y, self.f_yk)


def bending_moment_z(self, render = False, preferred_units=None, precision: int = 3):
    """
    Bending moment around z axis (along y axis)
    EC3 1993-1-1:2005 - § 6.2.5
    (ONLY CROSS-SECTIONS IN CLASS 1 OR 2)

    """
    gamma_m0 = self._partial_factors.get('gamma_m0', 1.05)
    if render==False:
        bending_moment_z = (self.section_w_pl_z * self.f_yk / gamma_m0).to_preferred(preferred_units)
        return bending_moment_z
    elif render==True:
        @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
        def render_instance(W_plCz, f_yk):
            """
            """
            M_cCRdCz = W_plCz * f_yk / gamma_m0; M_cCRdCz = (W_plCz * f_yk / gamma_m0 ).to_preferred(preferred_units)
        return render_instance(self.section_w_pl_z, self.f_yk)    

def shear_y(self, render = False, preferred_units=None, precision: int = 3):
    """

    EC3 1993-1-1:2005 - § 6.2.6

    """
    gamma_m0 = self._partial_factors.get('gamma_m0', 1.05)
    if render==False:
        shear_y = (self.section_area_shear_y * (self.f_yk / sqrt(3)) / gamma_m0).to_preferred(preferred_units)
        return shear_y
    elif render==True:
        @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
        def render_instance(A_vCy, f_yk):
            """
            """
            V_cCRdCy = A_vCy * (f_yk / sqrt(3)) / gamma_m0; V_cCRdCy = (A_vCy * (f_yk / sqrt(3)) / gamma_m0).to_preferred(preferred_units)
        return render_instance(self.section_area_shear_y, self.f_yk)            

def shear_z(self, render = False, preferred_units=None, precision: int = 3):
    """
    
    EC3 1993-1-1:2005 - § 6.2.6

    """
    gamma_m0 = self._partial_factors.get('gamma_m0', 1.05)
    if render==False:
        shear_z = (self.section_area_shear_z * (self.f_yk / sqrt(3)) / gamma_m0).to_preferred(preferred_units)
        return shear_z
    elif render==True:
        @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
        def render_instance(A_vCz, f_yk):
            """
            """
            V_cCRdCz = A_vCz * (f_yk / sqrt(3)) / gamma_m0; V_cCRdCz = (A_vCz * (f_yk / sqrt(3)) / gamma_m0).to_preferred(preferred_units)
        return render_instance(self.section_area_shear_z, self.f_yk)            

# INTERACTION BETWEEN STRESS CHARACTERISTICS

## Bending and axial force
def bending_moment_axial_y(self, render = False, preferred_units=None, precision: int = 3, n_ed: float = 0):
    """
    Bending moment around y axis (along z axis) with simultaneous axial force
    EC3 1993-1-1:2005 - § 6.2.9
    (ONLY CROSS-SECTIONS IN CLASS 1 OR 2)

    """
    if n_ed == 0:
        raise ValueError(f"The normal force cannot be 0")
    
    gamma_m0 = self._partial_factors.get('gamma_m0', 1.05)
    n_pl_rd = self.section_area * self.f_yk / gamma_m0
    if render==False:
        # Check for web dimensions (for I-sections)
        web_check = 0.5 * self.h_w * self.t_w * self.f_yk / gamma_m0 if self.h_w is not None and self.t_w is not None else float('inf')
        if n_ed <= 0.25 * n_pl_rd and n_ed <= web_check:
            bending_moment_y = (self.section_w_pl_y * self.f_yk / gamma_m0).to_preferred(preferred_units)
        else:
            # For higher axial forces, the moment capacity is reduced
            # This is a simplified implementation; full interaction should be implemented
            n = n_ed / n_pl_rd
            a = (self.section_area - 2*self.b*self.t_f) / self.section_area if self.b is not None and self.t_f is not None else 0
            k =  (1 - n) / (1 - 0.5*a) 
            m_pl_rd_y = self.section_w_pl_y * self.f_yk / gamma_m0 
            bending_moment_y = m_pl_rd_y * k
            if bending_moment_y > m_pl_rd_y:
                bending_moment_y = m_pl_rd_y
        return (bending_moment_y).to_preferred(preferred_units)
    elif render==True:
        m_pl_rd_y = self.section_w_pl_y * self.f_yk / gamma_m0 
        @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
        def render_instance(N_Ed, N_plCRd, W_plCy, f_yk, A, b, t_f):
            """
            """
            n = N_Ed / N_plCRd
            a = (A - 2*b*t_f) / A
            k =  (1 - n) / (1 - 0.5*a) 
            M_plCRdCy = W_plCy * f_yk / gamma_m0; M_plCRdCy = (W_plCy * f_yk / gamma_m0).to_preferred(preferred_units)
            M_NCy = M_plCRdCy * k; M_NCy = (M_plCRdCy * k).to_preferred(preferred_units)
        return render_instance(n_ed, n_pl_rd, self.section_w_pl_y, self.f_yk, self.section_area, self.b, self.t_f)

def bending_moment_axial_z(self, render = False, preferred_units=None, precision: int = 3, n_ed: float = 0):
    """
    Bending moment around z axis (along y axis) with simultaneous axial force
    EC3 1993-1-1:2005 - § 6.2.9
    (ONLY CROSS-SECTIONS IN CLASS 1 OR 2)

    """
    if n_ed == 0:
        raise ValueError(f"The normal force cannot be 0")

    gamma_m0 = self._partial_factors.get('gamma_m0', 1.05)
    n_pl_rd = self.section_area * self.f_yk / gamma_m0
    if render==False:
        web_check = 0.5 * self.h_w * self.t_w * self.f_yk / gamma_m0 if self.h_w is not None and self.t_w is not None else float('inf')
        if n_ed <= web_check:
            bending_moment_z = self.section_w_pl_z * self.f_yk / gamma_m0
        else:
            # For higher axial forces, the moment capacity is reduced
            # This is a simplified implementation; full interaction should be implemented
            n = n_ed / n_pl_rd
            a = (self.section_area - 2*self.b*self.t_f) / self.section_area if self.b is not None and self.t_f is not None else 0
            k =  1 - ((n - a) / (1 - a))**2 
            m_pl_rd_z = self.section_w_pl_y * self.f_yk / gamma_m0 
            if n <= a: bending_moment_z = m_pl_rd_z
            elif n > a: bending_moment_z = m_pl_rd_z * k
        return bending_moment_z
    elif render==True:
        m_pl_rd_z = self.section_w_pl_y * self.f_yk / gamma_m0 
        @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
        def render_instance(N_Ed, N_plCRd, W_plCz, f_yk, A, b, t_f):
            """
            """
            n = N_Ed / N_plCRd
            a = (A - 2*b*t_f) / A
            k =  1 - ((n - a) / (1 - a))**2 
            M_plCRdCz = W_plCz * f_yk / gamma_m0; M_plCRdCz = (W_plCz * f_yk / gamma_m0).to_preferred(preferred_units)
            M_NCz = M_plCRdCz * k; M_NCz = (M_plCRdCz * k).to_preferred(preferred_units)
        return render_instance(n_ed, n_pl_rd, self.section_w_pl_z, self.f_yk, self.section_area, self.b, self.t_f)

## Bending and shear

## Torsion

# ----- STABILITY

def eulerian_critic_load(self, render = False, preferred_units=None, precision: int = 3):
    """
    """
    if render==False:    
        n_cr_y = (pi**2 * self.elastic_modulus * self.section_inertia_y) / (self.length)**2
        n_cr_z = (pi**2 * self.elastic_modulus * self.section_inertia_z) / (self.length)**2
        n_cr = min(n_cr_y, n_cr_z)
        return n_cr
    elif render==True:
        @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
        def render_instance(E, I_y, I_z, L_0):
            """
            """
            N_crCy = ((pi**2 * E * I_y) / L_0**2); N_crCy = (((pi**2 * E * I_y) / L_0**2)).to_preferred(preferred_units)
            N_crCz = ((pi**2 * E * I_z) / L_0**2); N_crCz = (((pi**2 * E * I_z) / L_0**2)).to_preferred(preferred_units)
            N_cr = min(N_crCy, N_crCz); N_cr = (min(N_crCy, N_crCz)).to_preferred(preferred_units)
        return render_instance(self.elastic_modulus, self.section_inertia_y, self.section_inertia_z, self.length)            

def slenderness_relative(self):
    """"
    """
    lambda_relative = sqrt(self.section_area * self.f_yk / self.eulerian_critic_load())
    return lambda_relative

def normal_force_buckling(self, buckling_curve: str, render = False, preferred_units=None, precision: int = 3):
    """

    Buckling resistance for uniform members in compression
    EC3 1993-1-1:2005 - § 6.3.1
  
    """
    gamma_m1 = self._partial_factors.get('gamma_m0', 1.10)
    imperfection_factors = {
    'a0': 0.13,
    'a': 0.21,
    'b': 0.34,
    'c': 0.49,
    'd': 0.76
    }
    alpha = imperfection_factors.get(buckling_curve)
    lambd = self.slenderness_relative()
    if render==False:
        psi = 0.5*(1+alpha*(lambd-0.2)+lambd**2)
        chi = 1/ (psi+sqrt(psi**2 - lambd**2))
        N_bRd = (chi * self.section_area * self.f_yk / gamma_m1).to_preferred(preferred_units)
        return N_bRd
    if render==True:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(A, f_yk, alpha, lamb):
                """
                """
                Phi = 0.5*(1+alpha*(lamb-0.2)+lamb**2)
                chi = 1/ (Phi+sqrt(Phi**2 - lamb**2))
                N_bcRd = chi * A * f_yk / gamma_m1; N_bcRd = (chi * A * f_yk / gamma_m1).to_preferred(preferred_units)
            return render_instance(self.section_area, self.f_yk, alpha, lambd)


def bending_moment_buckling_y(self, psi_1:float = 1.0 , k_c: float = 1.0, buckling_curve_lt: str = 'a', beta:float = 1.0, render = False, preferred_units=None, precision: int = 3):
    """
    
    Buckling resistance for uniform members in bending with action along y axis
    EC3 1993-1-1:2005 - § 6.3.2
  
    """
    gamma_m1 = self._partial_factors.get('gamma_m0', 1.10)
    imperfection_factors = {
    'a': 0.21,
    'b': 0.34,
    'c': 0.49,
    'd': 0.76
    }
    alpha_lt = imperfection_factors.get(buckling_curve_lt)
    l_cr = self.length * beta
    lamb_lt_0 = 0.2
    if render==False:
        # Approximation without taking warping stiffness into account
        m_cr = psi_1 * (pi/l_cr) * sqrt(self.elastic_modulus * self.section_inertia_y * self.shear_modulus * self.section_inertia_torsional)
        lambd_lt = sqrt(self.section_w_pl_y* self.f_yk/m_cr)
        phi_lt = 0.5*(1+alpha_lt*(lambd_lt-lamb_lt_0)+beta*lambd_lt**2)
        f = 1-0.5*(1-k_c)*(1-2*(lambd_lt-0.8)**2)
        chi_lt = (1/f)* (1/ (phi_lt+sqrt(phi_lt**2 - beta*lambd_lt**2)))
        M_bRd = (chi_lt * self.section_w_pl_y * self.f_yk / gamma_m1).to_preferred(preferred_units)
        return M_bRd
    elif render==True:
        @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
        def render_instance(f_yk, E, G, I_y, I_T, W_plCy, L_cr, alpha_LT, lamb_LTc0):
            """
            """
            M_cr = psi_1 * (pi/L_cr) * sqrt(E * I_y * G * I_T)
            lamb_LT = sqrt(W_plCy* f_yk/M_cr)
            phi_LT = 0.5*(1+alpha_LT*(lamb_LT-lamb_LTc0)+beta*lamb_LT**2)
            f = 1-0.5*(1-k_c)*(1-2*(lamb_LT-0.8)**2)
            chi_LT = (1/f)* (1/ (phi_LT+sqrt(phi_LT**2 - beta*lamb_LT**2)))
            M_bCRd = chi_LT * W_plCy * f_yk / gamma_m1; M_bCRd = (chi_LT * W_plCy * f_yk / gamma_m1).to_preferred(preferred_units)
        return render_instance(self.f_yk, self.elastic_modulus, self.shear_modulus, self.section_inertia_y, self.section_inertia_torsional, self.section_w_pl_y, l_cr, alpha_lt, lamb_lt_0)
        

def bending_moment_buckling_z(self, psi_1:float = 1.0 , k_c: float = 1.0, buckling_curve_lt: str = 'a', beta:float = 1.0, render = False, preferred_units=None, precision: int = 3):
    """
    
    Buckling resistance for uniform members in bending with action along z axis
    EC3 1993-1-1:2005 - § 6.3.2

    """
    gamma_m1 = self._partial_factors.get('gamma_m0', 1.10)
    imperfection_factors = {
    'a': 0.21,
    'b': 0.34,
    'c': 0.49,
    'd': 0.76
    }
    alpha_lt = imperfection_factors.get(buckling_curve_lt)
    l_cr = self.length * beta
    lamb_lt_0 = 0.2
    if render==False:
        # Approximation without taking warping stiffness into account
        m_cr = psi_1 * (pi/l_cr) * sqrt(self.elastic_modulus * self.section_inertia_z * self.shear_modulus * self.section_inertia_torsional)
        lambd_lt = sqrt(self.section_w_pl_z* self.f_yk/m_cr)
        phi_lt = 0.5*(1+alpha_lt*(lambd_lt-lamb_lt_0)+beta*lambd_lt**2)
        f = 1-0.5*(1-k_c)*(1-2*(lambd_lt-0.8)**2)
        chi_lt = (1/f)* (1/ (phi_lt+sqrt(phi_lt**2 - beta*lambd_lt**2)))
        M_bRd = (chi_lt * self.section_w_pl_z * self.f_yk / gamma_m1).to_preferred(preferred_units)
        return M_bRd
    elif render==True:
        @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
        def render_instance(f_yk, E, G, I_z, I_T, W_plCz, L_cr, alpha_LT, lamb_LTc0):
            """
            """
            M_cr = psi_1 * (pi/L_cr) * sqrt(E * I_z * G * I_T)
            lamb_LT = sqrt(W_plCz* f_yk/M_cr)
            phi_LT = 0.5*(1+alpha_LT*(lamb_LT - lamb_LTc0)+beta*lamb_LT**2)
            f = 1-0.5*(1-k_c)*(1-2*(lamb_LT-0.8)**2)
            chi_LT = (1/f)* (1/ (phi_LT+sqrt(phi_LT**2 - beta*lamb_LT**2)))
            M_bCRd = chi_LT * W_plCz * f_yk / gamma_m1; M_bCRd = (chi_LT * W_plCz * f_yk / gamma_m1).to_preferred(preferred_units)
        return render_instance(self.f_yk, self.elastic_modulus, self.shear_modulus, self.section_inertia_z, self.section_inertia_torsional, self.section_w_pl_z, l_cr, alpha_lt, lamb_lt_0)