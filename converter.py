import math
import numpy as np


class Converter():
    def __init__(self, initial_state):
        self.V_mun = initial_state["V_mun"]
        self.R_mun = initial_state["R_mun"]
        self.W_mun = self.V_mun / self.R_mun

    def from_k_to_l(self, s):
        psi = math.acos((s.L_mun**2 + self.R_mun**2 - s.L_kerbin**2) / (2 * s.L_mun * self.R_mun))
        theta = math.pi - psi - s.fi
        Vt = s.Vt_k - s.L_kerbin * self.W_mun
        a = np.array([s.Vr_k, Vt])
        b = np.array([[math.cos(theta), math.sin(theta)],
                      [math.sin(theta), -math.cos(theta)]])
        c = b.dot(a)
        Vr_new = c[0]
        Vt_new = c[1]
        return Vr_new, Vt_new, psi

    def from_l_to_k(self, s):
        fi = - math.acos((s.L_kerbin**2 + self.R_mun**2 - s.L_mun **
                       2) / (2 * s.L_kerbin * self.R_mun))
        theta = math.pi - s.psi - fi
        a = np.array([s.Vr_m, s.Vt_m])
        b = np.array([[ math.cos(theta),  math.sin(theta)],
                      [ math.sin(theta), -math.cos(theta)]])
        c = b.dot(a)
        Vr_new = c[0]
        Vt_new = c[1] + s.L_kerbin * self.W_mun
        return Vr_new, Vt_new, fi
