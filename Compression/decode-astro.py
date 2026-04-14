import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt
import sys

# ==========================================
# PARTIE 1 : PRÉPARATION DU FLUX (Entrée)
# ==========================================
def get_clean_input(kepler_id, t_start, t_duration, n_points=2048):
    """Télécharge et prépare le flux pour l'encodeur."""
    print(f"--- Préparation du flux pour {kepler_id} ---")

    # Téléchargement et assemblage
    search = lk.search_lightcurve(kepler_id, author="Kepler", cadence="long")
    if not search: return None
    lc = search.download_all().stitch()
    lc_flat = lc.flatten(window_length=401)
    print(1)
    # Sélection de la fenêtre
    mask = (lc_flat.time.value >= t_start) & (lc_flat.time.value <= t_start + t_duration)
    lc_win = lc_flat[mask]
    print(2)
    # Interpolation linéaire (la 'droite' pour les NaNs et la régularité)
    t_reg = np.linspace(lc_win.time.value.min(), lc_win.time.value.max(), n_points)
    flux_input = np.interp(t_reg, lc_win.time.value, lc_win.flux.value)
    print(3)
    return t_reg, flux_input

# ==========================================
# PARTIE 2 :PIPELINE D'OPTIMISATION
# ==========================================

# 1. On récupère le flux réel (2048 points pour faciliter les divisions par 2)
time, flux_in = get_clean_input("Kepler-90", t_start=130, t_duration=20, n_points=2048)
for i in range(len(flux_in)) :
    flux_in[i] = 1000*flux_in[i]
# ==========
# Codage décodage
# ==========
def poms(nmb,elt):
    return nmb-(elt/2),nmb+(elt/2)

def moyenne(a,b):
    return (a+b)/2

def haar(a,b):
    return -a +b

def compression(L):
    if len(L)==1:
        return [L]
    res, moy = [], []
    for i in range(0, len(L)-1, 2):
        a = L[i]
        b = L[i+1]
        moy.append(moyenne(a,b))
        res.append(haar(a,b))
    return [res] + compression(moy)

def decompression(E):
    S = []
    C,F = E[:-1],E[-1]
    for i in range(len(C)):
        for j in range(len(C[len(C)-i-1])):
            a,b = poms(F[j],C[len(C)-i-1][j])
            S += [a,b]
        F = S
        S = []
    return F

def roundlst(L, r=0):
    for i in range(len(L)):
        for j in range(len(L[i])):
            ##L[i][j] = round(L[i][j],r)
            L[i][j] = int(L[i][j])
    return L


flux_out = decompression(roundlst(compression(flux_in)))
F = roundlst(compression(flux_in))
print(F)


# =====================
plt.figure(figsize=(14, 10))

# Flux d'entrée
plt.subplot(2, 1, 1)
plt.plot(time, flux_in, color='black', alpha=0.3, label="Flux brut interpolé")

plt.subplot(2,1,2)
plt.plot(time, flux_out, color='blue', label="Flux reconstruit après compression")

plt.title("Étape 1 & 3 : Entrée vs Reconstruction (Efficacité)")
plt.legend()
plt.show()
