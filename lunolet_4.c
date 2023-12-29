#include <math.h>
#include <stdlib.h>
#define pi 3.14159265358979323846

struct step_struct
{
    double Vr;
    double Vt;
    double L_mun;
    double psi;
};

struct step_struct *c_step(double dt, double mu, double W_mun, double Vr, double Vt, double L_mun, double psi, double beta, double a)
{
    struct step_struct *lunolet_4;
    double Vt_new = (-(Vr * Vt) / L_mun - 2 * Vr * W_mun + 3 * sin(psi) * cos(psi) * L_mun * W_mun * W_mun + sin(beta) * a) * dt + Vt;
    double psi_new = fmod(((Vt + Vt_new) * dt) / (2 * L_mun) + psi, 2 * pi);
    double Vr_new = ((Vt_new * Vt_new) / L_mun - 2 * W_mun * Vt_new + 3 * cos(psi) * cos(psi) * L_mun * W_mun * W_mun - mu / (L_mun * L_mun) + cos(beta) * a) * dt + Vr;
    double L_mun_new = ((Vr + Vr_new) * dt) / 2 + L_mun;
    lunolet_4 = malloc(sizeof(struct step_struct));
    lunolet_4->Vr = Vr_new;
    lunolet_4->Vt = Vt_new;
    lunolet_4->L_mun = L_mun_new;
    lunolet_4->psi = psi_new;
    return lunolet_4;
};

struct coords
{
    double x;
    double y;
};

struct coords *c_get_coords(double W_mun, double R_mun, double L_mun, double psi, double t)
{
    struct coords *coords;
    double x = -L_mun * cos(psi - W_mun * t) + R_mun * cos(W_mun * t);
    double y = L_mun * sin(psi - W_mun * t) + R_mun * sin(W_mun * t);
    coords = malloc(sizeof(struct coords));
    coords->x = x;
    coords->y = y;
    return coords;
}