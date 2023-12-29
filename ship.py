class Ship():
    def __init__(self, initial_state: dict):
        self.Vr_k = initial_state["Vr_k"]
        self.Vt_k = initial_state["Vt_k"]
        self.Vr_m = initial_state["Vr_m"]
        self.Vt_m = initial_state["Vt_m"]
        self.L_kerbin = initial_state["L_kerbin"]
        self.L_mun = initial_state["L_mun"]
        self.fi = initial_state["fi"]
        self.psi = initial_state["psi"]
    def copy(self):
        return Ship({
            "Vr_k": self.Vr_k,
            "Vt_k": self.Vt_k,
            "Vr_m": self.Vr_m,
            "Vt_m": self.Vt_m,
            "L_kerbin": self.L_kerbin,
            "L_mun": self.L_mun,
            "fi": self.fi,
            "psi": self.psi
        })
    def copyTo(self, other):
        other.Vr_k = self.Vr_k
        other.Vt_k = self.Vt_k
        other.Vr_m = self.Vr_m
        other.Vt_m = self.Vt_m
        other.L_kerbin = self.L_kerbin
        other.L_mun = self.L_mun
        other.fi = self.fi
        other.psi = self.psi