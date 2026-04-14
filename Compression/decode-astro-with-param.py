import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt
import sys


# Paramètres
CIBLE = "Kepler-90"
DEBUT = 130
DUREE = 20
NOMBRE = 5
RESOLUTION = 2**13 # Doit être une puissance de 2 (2048 = 2**11)
ARRONDI = 3

# ==========================================
# PARTIE 1 : PRÉPARATION DU FLUX (Entrée)
# ==========================================
def get_clean_input(kepler_id, t_start, t_duration, n_points=2048):
    """Télécharge et prépare le flux pour l'encodeur."""
    print(f"--- Préparation du flux pour {kepler_id} ---")

    # Téléchargement et assemblage
    search = lk.search_lightcurve(kepler_id, author="Kepler", cadence="long")
    print(search)
    if not search: return None
    lc = search.download_all().stitch()
    lc_flat = lc.flatten(window_length=401)
    print(1)
    # Sélection de la fenêtre
    mask = (lc_flat.time.value >= t_start) & (lc_flat.time.value <= t_start + (t_duration * NOMBRE))
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
time, flux_in = get_clean_input(CIBLE, t_start=DEBUT, t_duration=DUREE, n_points=RESOLUTION)

# ==========
# Codage décodage
# ==========

def split_equal_parts(arr, n):
    arr = np.array(arr)
    return np.split(arr, n)
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

def roundlst(L, r=ARRONDI):
    for i in range(len(L)):
        for j in range(len(L[i])):
            L[i][j] = round(L[i][j],r)
    return L

#sys.getsizeof(lst)

#print(compression(flux_in))
sec = DUREE/20
comp = split_equal_parts(flux_in, sec)

for i in range(len(comp)):
    comp[i] = roundlst(compression(comp[i]))
flux_out = [decompression(comp[i]) for i in range(len(comp))]
    
#flux_out = decompression(roundlst(compression(flux_in)))
F = roundlst(compression(flux_in))

# =====================
plt.figure(figsize=(14, 10))

# Flux d'entrée
plt.subplot(2, 1, 1)
plt.plot(time, flux_in, color='black', alpha=0.3, label="Flux brut interpolé")

plt.subplot(2,1,2)
plt.plot(time, flux_out, color='blue', alpha=0.3,label="Flux reconstruit après compression")

plt.title("Étape 1 & 3 : Entrée vs Reconstruction (Efficacité)")
plt.legend()
plt.show()
# Les coefficients (ce que l'IA verra)

import sys
import os
import csv

def save_and_measure_sobriety(data, filename="data_tipe.csv"):

    # 1. Mesure de la taille en MÉMOIRE (RAM)
    # Note : sys.getsizeof ne calcule pas récursivement la taille des sous-listes.
    # On utilise une petite astuce pour additionner la taille de chaque élément.
    if any(isinstance(i, list) for i in data):
        ram_size = sys.getsizeof(data) + sum(sys.getsizeof(sub) for sub in data)
    else:
        ram_size = sys.getsizeof(data)

    # 2. ENREGISTREMENT AU FORMAT CSV
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        # Si c'est une liste de listes, writerows fait tout le travail
        if any(isinstance(i, list) for i in data):
            writer.writerows(data)
        else:
            # Si c'est une liste simple, on l'écrit comme une seule ligne
            writer.writerow(data)

    # 3. Mesure de la taille sur le DISQUE
    disk_size = os.path.getsize(filename)

    print(f"--- Rapport de Sobriété pour '{filename}' ---")
    print(f"📦 Taille en RAM      : {ram_size} octets")
    print(f"💾 Taille sur Disque  : {disk_size} octets")

    return ram_size, disk_size

# --- EXEMPLE D'UTILISATION POUR VOTRE TIPE ---

#save_and_measure_sobriety(flux_in, "flux_in.csv")
#save_and_measure_sobriety(flux_out, "flux_out.csv")

