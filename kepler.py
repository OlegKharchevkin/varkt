import math
import ctypes
import sys
import os


def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(".\\", relative)

class Kepler():
    class step_struct(ctypes.Structure):
        _fields_ = [('Vr', ctypes.c_double),
                    ('Vt', ctypes.c_double),
                    ('L_kerbin', ctypes.c_double),
                    ('fi', ctypes.c_double)]

    class coords(ctypes.Structure):
        _fields_ = [('x', ctypes.c_double),
                    ('y', ctypes.c_double)]

    def __init__(self, initial_state):
        self.G = initial_state["G"]
        self.M_kerbin = initial_state["M_kerbin"]
        self.V_mun = initial_state["V_mun"]
        self.R_mun = initial_state["R_mun"]
        self.W_mun = self.V_mun / self.R_mun
        self.mu = self.G * self.M_kerbin
        clib = ctypes.CDLL(resource_path('kepler.so'))
        self.c_step = clib.c_step
        self.c_step.restype = ctypes.POINTER(self.step_struct)
        self.c_step.argtypes = [
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
            ctypes.c_double
        ]

    def step(self, s, s_new, dt):
        p = self.c_step(dt, self.mu, self.W_mun, s.Vr_k, s.Vt_k, s.L_kerbin, s.fi)
        s_new.Vr_k = p.contents.Vr
        s_new.Vt_k = p.contents.Vt
        s_new.L_kerbin = p.contents.L_kerbin
        s_new.fi = p.contents.fi

    def get_coords(self, s, t=0):
        p = self.c_get_coords(self.W_mun, s.L_kerbin, s.fi, t)
        return p.contents.x, p.contents.y

    def get_L_mun(self, s):
        x, y = self.get_coords(s)
        L_mun = math.sqrt((x - self.R_mun)**2 + y**2)
        return L_mun
