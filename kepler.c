#include <math.h>
#include <stdlib.h>
#define pi 3.14159265358979323846 

struct step_struct
{
    double Vr;
    double Vt;
    double L_kerbin;
    double fi;
};

struct step_struct *c_step(double dt, double mu,double W_mun, double Vr, double Vt, double L_kerbin, double fi)
{
    struct step_struct *kepler;
    double fi_new = fmod(fi - dt * W_mun - (dt * dt * Vr * Vt) / (L_kerbin * L_kerbin) + (dt * Vt) / (L_kerbin), 2 * pi);
    double a = sqrt(pow(L_kerbin * pow(Vt, 2) - mu, 2) + pow(L_kerbin * Vr * Vt, 2));
    double multiplier = -1;
    if (Vr * Vt > 0){multiplier = 1;}
    double b = acos((L_kerbin * Vt * Vt - mu) / a) * multiplier - (dt * dt * Vr * Vt)/(L_kerbin * L_kerbin) + (dt * Vt)/(L_kerbin);
    double Vr_new = (sin(b) * a) / (Vt * L_kerbin);
    double Vt_new = (cos(b) * a + mu) / (L_kerbin * Vt);
    double L_kerbin_new = (Vt * L_kerbin) / (Vt_new);
    kepler = malloc(sizeof(struct step_struct));
    kepler->Vr = Vr_new;
    kepler->Vt = Vt_new;
    kepler->L_kerbin = L_kerbin_new;
    kepler->fi = fi_new;
    return kepler;
}

struct coords
{
    double x;
    double y;
};

struct coords *c_get_coords(double W_mun, double L_kerbin, double fi, double t)
{
    struct coords *coords;
    double x = L_kerbin * cos(fi + W_mun * t);
    double y = L_kerbin * sin(fi + W_mun * t);
    coords = malloc(sizeof(struct coords));
    coords->x = x;
    coords->y = y;
    return coords;
}

