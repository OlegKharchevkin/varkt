import plotly.graph_objs as go
import numpy as np
import argparse
import math
import os.path
import json
import time

import kepler
import lunolet_4
import converter
import ship
import auto


def main():
    first = False
    second = False
    points_x = np.array([])
    points_y = np.array([])
    parser = argparse.ArgumentParser(description='VARKT math model')
    parser.add_argument('--input', '-i', default='settings.json',
                        type=str, help='input file (default: settings.json)')
    args = parser.parse_args()

    d_sys = {
        "ossetian_sys": False,
        "G": 6.67554e-11,
        "M_kerbin": 5.2915158e+22,
        "M_mun": 9.7599066e+20,
        "V_mun": 543,
        "R_mun": 12000000,
        "dt": 5,
    }
    d_ship = {
        "Vr_k": 0,
        "Vt_k": 2705,
        "Vr_m": 0,
        "Vt_m": 0,
        "L_kerbin": 150000000,
        "L_mun": 0,
        "fi": math.pi,
        "psi": 0
    }

    if not os.path.exists(args.input):
        file_data = {
            "ossetian_sys": d_sys["ossetian_sys"],
            "G": d_sys["G"],
            "M_kerbin": d_sys["M_kerbin"],
            "M_mun": d_sys["M_mun"],
            "V_mun": d_sys["V_mun"],
            "R_mun": d_sys["R_mun"],
            "dt": d_sys["dt"],
            "Vr_k": d_ship["Vr_k"],
            "Vt_k": d_ship["Vt_k"],
            "L_kerbin": d_ship["L_kerbin"]
        }
        with open(args.input, 'w') as outfile:
            json.dump(file_data, outfile)
    else:
        with open(args.input) as json_file:
            file_data = json.load(json_file)
            for key in file_data:
                if key in d_sys:
                    d_sys[key] = file_data[key]
                if key in d_ship:
                    d_ship[key] = file_data[key]

    k = kepler.Kepler(d_sys)
    l = lunolet_4.Lunolet_4(d_sys)
    c = converter.Converter(d_sys)
    s = ship.Ship(d_ship)
    s_new = ship.Ship(d_ship)

    dfi = 0
    a = 0
    psi_tmp = 0
    Vt_tmp = 0
    beta = 0
    auto_dv = d_ship["Vt_k"]
    start = time.time()
    data = [s.copy()]

    for i in range(1000000):
        k.step(s, s_new, d_sys["dt"])
        if s.Vr_k > 0 and s_new.Vr_k < 0:
            dfi = s_new.fi
            break
        data.append(s_new.copy())
        s_new.copyTo(s)
    auto_dfi = -(math.pi - dfi)
    for i in range(len(data)):
        data[i].fi -= dfi
        data[i].fi %= (2 * math.pi)
        if k.get_L_mun(data[i]) < 2e6:
            data = data[:i]
            break
        x, y = k.get_coords(data[i], i * d_sys["dt"] * d_sys["ossetian_sys"])
        points_x = np.append(points_x, x)
        points_y = np.append(points_y, y)

    t = len(data) * d_sys["dt"]
    s.L_mun = k.get_L_mun(data[-1])
    data[-1].L_mun = s.L_mun
    s.Vr_m, s.Vt_m, s.psi = c.from_k_to_l(data[-1])
    data = [s.copy()]

    count = 0
    for i in range(1000000):
        l.step(d_sys["dt"], s, s_new, a, beta)
        a = 0
        beta = 0
        if not first and s.Vr_m < 0 and s_new.Vr_m > 0:
            first = True
            psi_tmp = (- s.psi) % (2 * math.pi)
            Vt_tmp = ((d_sys["G"] * d_sys["M_mun"]) / (s.L_mun))**0.5

            a_x = (s.Vt_m - Vt_tmp) / d_sys["dt"]
            a_y = 0
            a = math.sqrt(a_x**2 + a_y**2)
            beta = -math.acos(a_y / a)
            continue
        if first and not second and s.psi < psi_tmp and s_new.psi > psi_tmp:
            if count < 1:
                count += 1
            else:
                second = True
                a = math.sqrt(a_x**2 + a_y**2) * Vt_tmp / \
                    ((d_sys["G"] * d_sys["M_mun"]) / (s.L_mun))**0.5
                beta = math.acos(a_y / a)
                continue
        if second and s_new.L_mun > 2e6:
            break
        data.append(s_new.copy())
        s_new.copyTo(s)

    for i in range(len(data)):
        x, y = l.get_coords(data[i], i * d_sys["dt"]
                            * d_sys["ossetian_sys"] + t * d_sys["ossetian_sys"])
        points_x = np.append(points_x, x)
        points_y = np.append(points_y, y)

    t += len(data) * d_sys["dt"]
    s.L_kerbin = l.get_L_kerbin(data[-1])
    data[-1].L_kerbin = s.L_kerbin
    s.Vr_k, s.Vt_k, s.fi = c.from_l_to_k(data[-1])
    dfi = (-dfi) % (2 * math.pi)
    dfi = math.pi - dfi
    data = [s.copy()]

    for i in range(1000000):
        k.step(s, s_new, d_sys["dt"])
        if s.fi < dfi and s_new.fi > dfi and s.L_kerbin < d_sys["R_mun"]:
            break
        data.append(s_new.copy())
        s_new.copyTo(s)

    for i in range(len(data)):
        x, y = k.get_coords(data[i], i * d_sys["dt"]
                            * d_sys["ossetian_sys"] + t * d_sys["ossetian_sys"])
        points_x = np.append(points_x, x)
        points_y = np.append(points_y, y)

    end = time.time()
    auto.auto(auto_dv, auto_dfi, d_sys["V_mun"],
              d_sys["R_mun"], d_sys["G"] * d_sys["M_mun"])
    print("The time of execution of above program is :",
          (end-start) * 10**3, "ms")
    fig = go.Figure()
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.add_trace(go.Scatter(x=points_x, y=points_y))
    fig.show()


if __name__ == "__main__":
    main()
