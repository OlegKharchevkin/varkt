import math
import ctypes
import sys
import os

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(".\\", relative)


class Lunolet_4:
    class step_struct(ctypes.Structure):
        _fields_ = [('Vr', ctypes.c_double),
                    ('Vt', ctypes.c_double),
                    ('L_mun', ctypes.c_double),
                    ('psi', ctypes.c_double)]

    class coords(ctypes.Structure):
        _fields_ = [('x', ctypes.c_double),
                    ('y', ctypes.c_double)]

    def __init__(self, initial_state):
        self.G = initial_state["G"]
        self.M_mun = initial_state["M_mun"]
        self.V_mun = initial_state["V_mun"]
        self.R_mun = initial_state["R_mun"]
        self.W_mun = self.V_mun / self.R_mun
        self.mu = self.G * self.M_mun
        clib = ctypes.CDLL(resource_path('lunolet_4.so'))
        self.c_step = clib.c_step
        self.c_step.restype = ctypes.POINTER(self.step_struct)
        self.c_step.argtypes = [
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double
        ]
        self.c_get_coords = clib.c_get_coords
        self.c_get_coords.restype = ctypes.POINTER(self.coords)
        self.c_get_coords.argtypes = [
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double
        ]

    def step(self, dt, s, s_new, a=0, beta=0):
        p = self.c_step(dt, self.mu, self.W_mun, s.Vr_m, s.Vt_m, s.L_mun, s.psi, beta, a)
        s_new.Vr_m = p.contents.Vr
        s_new.Vt_m = p.contents.Vt
        s_new.L_mun = p.contents.L_mun
        s_new.psi = p.contents.psi

    def get_coords(self, s, t=0):
        p = self.c_get_coords(self.W_mun, self.R_mun, s.L_mun, s.psi, t)
        return p.contents.x, p.contents.y

    def get_L_kerbin(self, s):
        x, y = self.get_coords(s)
        L_kerbin = math.sqrt(x**2 + y**2)
        return L_kerbin
