"""
steelbeam - Eng. Rocco Raimo

---

ANALYSIS BASED ON EUROCODES

"""

from handcalcs.decorator import handcalc
from math import pi, sqrt

# ----- RESISTANCE

def normal_force_tension(self, a_net=None, render=False, prefix='', precision=3):
    """

    EC3 1993-1-1:2005 - § 6.2.3
    
    """
    if a_net is None:
        a_net = self.section_area
    gamma_m0 = self._partial_factors.get('gamma_m0', 1.05)
    gamma_m2 = self._partial_factors.get('gamma_m2', 1.25)

    if render==False:
        n_pl = self.section_area * self.f_yk / gamma_m0
        n_u = 0.9 * a_net * self.f_yk / gamma_m2
        normal_force_tension = min(n_pl, n_u)
        return normal_force_tension
        
    elif render==True:
        try:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(A, f_yk, A_net):
                """
                """
                N_plCRd = (A * f_yk / gamma_m0).prefix(prefix)
                N_uCRd = (0.9 * A_net * f_yk / gamma_m2).prefix(prefix)
                N_tCRd = min(N_plCRd, N_uCRd)
            return render_instance(self.section_area, self.f_yk, a_net)
        except:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(A, f_yk, A_net):
                """
                """
                N_plCRd = A * f_yk / gamma_m0
                N_uCRd = 0.9 * A_net * f_yk / gamma_m2
                N_tCRd = min(N_plCRd, N_uCRd)
            return render_instance(self.section_area, self.f_yk, a_net)

def normal_force_compression(self, render = False, prefix: str = '', precision: int = 3):
    """

    EC3 1993-1-1:2005 - § 6.2.4
    (ONLY CROSS-SECTIONS IN CLASS 1, 2 OR 3)

    """
    gamma_m0 = self._partial_factors.get('gamma_m0', 1.05)

    if render==False:
        normal_force_compression = self.section_area * self.f_yk / gamma_m0
        return normal_force_compression
    elif render==True:
        try:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(A, f_yk):
                """
                """
                N_cCRd = (A * f_yk / gamma_m0).prefix(prefix)
            return render_instance(self.section_area, self.f_yk)
        except:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(A, f_yk):
                """
                """
                N_cCRd = A * f_yk / gamma_m0
            return render_instance(self.section_area, self.f_yk)  

def bending_moment_y(self, render = False, prefix: str = '', precision: int = 3):
    """
    Bending moment around y axis (along z axis)
    EC3 1993-1-1:2005 - § 6.2.5
    (ONLY CROSS-SECTIONS IN CLASS 1 OR 2)

    """
    gamma_m0 = self._partial_factors.get('gamma_m0', 1.05)
    if render==False:
        bending_moment_y = self.section_w_pl_y * self.f_yk / gamma_m0
        return bending_moment_y
    elif render==True:
        try:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(W_plCy, f_yk):
                """
                """
                M_cCRdCy = (W_plCy * f_yk / gamma_m0).prefix(prefix)
            return render_instance(self.section_w_pl_y, self.f_yk)
        except:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(W_plCy, f_yk):
                """
                """
                M_cCRdCy = W_plCy * f_yk / gamma_m0
            return render_instance(self.section_w_pl_y, self.f_yk)

def bending_moment_z(self, render = False, prefix: str = '', precision: int = 3):
    """
    Bending moment around z axis (along y axis)
    EC3 1993-1-1:2005 - § 6.2.5
    (ONLY CROSS-SECTIONS IN CLASS 1 OR 2)

    """
    gamma_m0 = self._partial_factors.get('gamma_m0', 1.05)
    if render==False:
        bending_moment_z = self.section_w_pl_z * self.f_yk / gamma_m0
        return bending_moment_z
    elif render==True:
        try:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(W_plCz, f_yk):
                """
                """
                M_cCRdCz = (W_plCz * f_yk / gamma_m0).prefix(prefix)
            return render_instance(self.section_w_pl_z, self.f_yk)
        except:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(W_plCz, f_yk):
                """
                """
                M_cCRdCz = W_plCz * f_yk / gamma_m0
            return render_instance(self.section_w_pl_z, self.f_yk)    

def shear_y(self, render = False, prefix: str = '', precision: int = 3):
    """

    EC3 1993-1-1:2005 - § 6.2.6

    """
    gamma_m0 = self._partial_factors.get('gamma_m0', 1.05)
    if render==False:
        shear_y = self.section_area_shear_y * (self.f_yk / sqrt(3)) / gamma_m0
        return shear_y
    elif render==True:
        try:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(A_vCy, f_yk):
                """
                """
                V_cCRdCy = (A_vCy * (f_yk / sqrt(3)) / gamma_m0).prefix(prefix)
            return render_instance(self.section_area_shear_y, self.f_yk)
        except:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(A_vCy, f_yk):
                """
                """
                V_cCRdCy = A_vCy * (f_yk / sqrt(3)) / gamma_m0
            return render_instance(self.section_area_shear_y, self.f_yk)            

def shear_z(self, render = False, prefix: str = '', precision: int = 3):
    """
    
    EC3 1993-1-1:2005 - § 6.2.6

    """
    gamma_m0 = self._partial_factors.get('gamma_m0', 1.05)
    if render==False:
        shear_z = self.section_area_shear_z * (self.f_yk / sqrt(3)) / gamma_m0
        return shear_z
    elif render==True:
        try:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(A_vCz, f_yk):
                """
                """
                V_cCRdCz = (A_vCz * (f_yk / sqrt(3)) / gamma_m0).prefix(prefix)
            return render_instance(self.section_area_shear_z, self.f_yk)
        except:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(A_vCz, f_yk):
                """
                """
                V_cCRdCz = A_vCz * (f_yk / sqrt(3)) / gamma_m0
            return render_instance(self.section_area_shear_z, self.f_yk)            

# INTERACTION BETWEEN STRESS CHARACTERISTICS

## Bending and axial force
def bending_moment_axial_y(self, render = False, prefix: str = '', precision: int = 3, n_ed: float = 0):
    """
    Bending moment around y axis (along z axis) with simultaneous axial force
    EC3 1993-1-1:2005 - § 6.2.9
    (ONLY CROSS-SECTIONS IN CLASS 1 OR 2)

    """
    gamma_m0 = self._partial_factors.get('gamma_m0', 1.05)
    n_pl_rd = self.section_area * self.f_yk / gamma_m0
    if render==False:
        if n_ed <= 0.25 * n_pl_rd and n_ed <= 0.5 * self.h_w * self.t_w * self.f_yk / gamma_m0:
            bending_moment_y = self.section_w_pl_y * self.f_yk / gamma_m0
        else:
            # For higher axial forces, the moment capacity is reduced
            # This is a simplified implementation; full interaction should be implemented
            n = n_ed / n_pl_rd
            a = (self.section_area - 2*self.b*self.t_f / self.section_area) 
            k =  (1 - n) / (1 - 0.5*a) 
            m_pl_rd_y = self.section_w_pl_y * self.f_yk / gamma_m0 
            bending_moment_y = m_pl_rd_y * k
            if bending_moment_y > m_pl_rd_y:
                bending_moment_y = m_pl_rd_y
        return bending_moment_y
    elif render==True:
        m_pl_rd_y = self.section_w_pl_y * self.f_yk / gamma_m0 
        try:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(N_Ed, N_plCRd, W_plCy, f_yk, A, b, t_f):
                """
                """
                n = N_Ed / N_plCRd
                a = (A - 2*b*t_f) / A 
                k =  (1 - n) / (1 - 0.5*a) 
                M_plCRdCy = (W_plCy * f_yk / gamma_m0).prefix(prefix) 
                M_NCy = (M_plCRdCy * k).prefix(prefix)
            return render_instance(n_ed, n_pl_rd, self.section_w_pl_y, self.f_yk, self.section_area, self.b, self.t_f)
        except:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(N_Ed, N_plCRd, W_plCy, f_yk, A, b, t_f):
                """
                """
                n = N_Ed / N_plCRd
                a = (A - 2*b*t_f) / A
                k =  (1 - n) / (1 - 0.5*a) 
                M_plCRdCy = W_plCy * f_yk / gamma_m0 
                M_NCy = M_plCRdCy * k
            return render_instance(n_ed, n_pl_rd, self.section_w_pl_y, self.f_yk, self.section_area, self.b, self.t_f)

def bending_moment_axial_z(self, render = False, prefix: str = '', precision: int = 3, n_ed: float = 0):
    """
    Bending moment around z axis (along y axis) with simultaneous axial force
    EC3 1993-1-1:2005 - § 6.2.9
    (ONLY CROSS-SECTIONS IN CLASS 1 OR 2)

    """
    gamma_m0 = self._partial_factors.get('gamma_m0', 1.05)
    n_pl_rd = self.section_area * self.f_yk / gamma_m0
    if render==False:
        if n_ed <= 0.5 * self.h_w * self.t_w * self.f_yk / gamma_m0:
            bending_moment_z = self.section_w_pl_z * self.f_yk / gamma_m0
        else:
            # For higher axial forces, the moment capacity is reduced
            # This is a simplified implementation; full interaction should be implemented
            n = n_ed / n_pl_rd
            a = (self.section_area - 2*self.b*self.t_f / self.section_area)
            k =  1 - ((n - a) / (1 - a))**2 
            m_pl_rd_z = self.section_w_pl_y * self.f_yk / gamma_m0 
            if n <= a: bending_moment_z = m_pl_rd_z
            elif n > a: bending_moment_z = m_pl_rd_z * k
        return bending_moment_z
    elif render==True:
        m_pl_rd_z = self.section_w_pl_y * self.f_yk / gamma_m0 
        try:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(N_Ed, N_plCRd, W_plCz, f_yk, A, b, t_f):
                """
                """
                n = N_Ed / N_plCRd
                a = (A - 2*b*t_f) / A
                k =  1 - ((n - a) / (1 - a))**2 
                M_plCRdCz = (W_plCz * f_yk / gamma_m0).prefix(prefix) 
                M_NCz = (M_plCRdCz * k).prefix(prefix)
            return render_instance(n_ed, n_pl_rd, self.section_w_pl_z, self.f_yk, self.section_area, self.b, self.t_f)
        except:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(N_Ed, N_plCRd, W_plCz, f_yk, A, b, t_f):
                """
                """
                n = N_Ed / N_plCRd
                a = (A - 2*b*t_f) / A
                k =  1 - ((n - a) / (1 - a))**2 
                M_plCRdCz = W_plCz * f_yk / gamma_m0 
                M_NCz = M_plCRdCz * k
            return render_instance(n_ed, n_pl_rd, self.section_w_pl_z, self.f_yk, self.section_area, self.b, self.t_f)

## Bending and shear

## Torsion

# ----- STABILITY

def eulerian_critic_load(self, render = False, prefix: str = '', precision: int = 3):
    """
    """
    if render==False:    
        n_cr_y = (pi**2 * self.elastic_modulus * self.section_inertia_y) / (self.length)**2
        n_cr_z = (pi**2 * self.elastic_modulus * self.section_inertia_z) / (self.length)**2
        n_cr = min(n_cr_y, n_cr_z)
        return n_cr
    elif render==True:
        try:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(E, I_y, I_z, L_0):
                """
                """
                N_crCy = ((pi**2 * E * I_y) / L_0**2).prefix(prefix)
                N_crCz = ((pi**2 * E * I_z) / L_0**2).prefix(prefix)
                N_cr = (min(N_crCy, N_crCz)).prefix(prefix)
            return render_instance(self.elastic_modulus, self.section_inertia_y, self.section_inertia_z, self.length)
        except:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(E, I_y, I_z, L_0):
                """
                """
                N_crCy = ((pi**2 * E * I_y) / L_0**2)
                N_crCz = ((pi**2 * E * I_z) / L_0**2)
                N_cr = min(N_crCy, N_crCz)
            return render_instance(self.elastic_modulus, self.section_inertia_y, self.section_inertia_z, self.length)            

def slenderness_relative(self):
    """"
    """
    lambda_relative = sqrt(self.section_area * self.f_yk / self.eulerian_critic_load())
    return lambda_relative

def normal_force_buckling(self, buckling_curve: str, render = False, prefix: str = '', precision: int = 3):
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
        N_bRd = chi * self.section_area * self.f_yk / gamma_m1
        return N_bRd
    if render==True:
        try:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(A, f_yk, alpha, lamb):
                """
                """
                Phi = 0.5*(1+alpha*(lamb-0.2)+lamb**2)
                chi = 1/ (Phi+sqrt(Phi**2 - lamb**2))
                N_bCRd = (chi * A * f_yk / gamma_m1).prefix(prefix)
            return render_instance(self.section_area, self.f_yk, alpha, lambd)
        except:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(A, f_yk, alpha, lamb):
                """
                """
                Phi = 0.5*(1+alpha*(lamb-0.2)+lamb**2)
                chi = 1/ (Phi+sqrt(Phi**2 - lamb**2))
                N_bcRd = chi * A * f_yk / gamma_m1
            return render_instance(self.section_area, self.f_yk, alpha, lambd)


def bending_moment_buckling_y(self, psi_1:float = 1.0 , k_c: float = 1.0, buckling_curve_lt: str = 'a', beta:float = 1.0, render = False, prefix: str = '', precision: int = 3):
    """
    
    Buckling resistance for uniform members in bending
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
    if render==False:
        m_cr = psi_1 * (pi/l_cr) * sqrt(self.elastic_modulus * self.section_inertia_z * self.shear_modulus * self_section_inertia_torsional) # Approximation without taking warping stiffness into account
        lambd_lt = sqrt(self.section_w_pl_y* self.f_yk/m_cr)
        phi_lt = 0.5*(1+alpha_lt*(lambd_lt-lamb_lt0)+beta*lambd_lt**2)
        f = 1-0.5*(1-k_c)*(1-2*(lamb_lt-0.8)**2)
        chi_lt = (1/f)* (1/ (phi_lt+sqrt(phi_lt**2 - beta*lambd_lt**2)))
        M_bRd = chi_lt * self.section_w_pl_y * self.f_yk / gamma_m1
        return M_bRd
    if render==True:
        try:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(A, f_yk, alpha, lamb):
                """
                """
                Phi = 0.5*(1+alpha*(lamb-0.2)+lamb**2)
                chi = 1/ (Phi+sqrt(Phi**2 - lamb**2))
                N_bCRd = (chi * A * f_yk / gamma_m1).prefix(prefix)
            return render_instance(self.section_area, self.f_yk, alpha, lambd)
        except:
            @handcalc(override= "", precision= precision, left= "", right= "", jupyter_display=True)
            def render_instance(A, f_yk, alpha, lamb):
                """
                """
                Phi = 0.5*(1+alpha*(lamb-0.2)+lamb**2)
                chi = 1/ (Phi+sqrt(Phi**2 - lamb**2))
                N_bcRd = chi * A * f_yk / gamma_m1
            return render_instance(self.section_area, self.f_yk, alpha, lambd)