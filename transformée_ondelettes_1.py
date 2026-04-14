import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# PARTIE 1 : PRÉPARATION DU FLUX (Entrée)
# ==========================================
def get_clean_input(kepler_id, t_start, t_duration, n_points=2048):
    """Télécharge et prépare le flux pour l'encodeur."""
    print(f"--- Préparation du flux pour {kepler_id} ---")
    
    # Téléchargement et assemblage
    lc = lk.search_lightcurve(kepler_id, author="Kepler").download_all().stitch()
    lc_flat = lc.flatten(window_length=401)
    
    # Sélection de la fenêtre
    mask = (lc_flat.time.value >= t_start) & (lc_flat.time.value <= t_start + t_duration)
    lc_win = lc_flat[mask]
    
    # Interpolation linéaire (la 'droite' pour les NaNs et la régularité)
    t_reg = np.linspace(lc_win.time.value.min(), lc_win.time.value.max(), n_points)
    flux_input = np.interp(t_reg, lc_win.time.value, lc_win.flux.value)
    
    return t_reg, flux_input

# ==========================================
# PARTIE 2 : ENCODEUR / DÉCODEUR HAAR (Votre algo)
# ==========================================
def haar_encode(signal):
    """Version MP* : Transformée de Haar discrète unitaire."""
    # Le signal doit être de taille paire
    s = (signal[0::2] + signal[1::2]) / np.sqrt(2) # Moyennes (Approximation)
    d = (signal[0::2] - signal[1::2]) / np.sqrt(2) # Différences (Détails/Gaps)
    return s, d

def haar_decode(s, d):
    """Reconstruction exacte du signal."""
    reconstructed = np.zeros(2 * len(s))
    reconstructed[0::2] = (s + d) / np.sqrt(2)
    reconstructed[1::2] = (s - d) / np.sqrt(2)
    return reconstructed

# ==========================================
# PARTIE 3 : PIPELINE D'OPTIMISATION
# ==========================================

# 1. On récupère le flux réel (2048 points pour faciliter les divisions par 2)
time, flux_in = get_clean_input("Kepler-90", t_start=130, t_duration=20, n_points=2048)

# 2. On encode
moyennes, details = haar_encode(flux_in)

# 3. On optimise (Sobriété) : on ne garde que les détails > seuil
SEUIL = 0.002
details_optimises = np.where(np.abs(details) < SEUIL, 0, details)

# 4. On décode pour vérifier la fidélité
flux_out = haar_decode(moyennes, details_optimises)

# ==========================================
# VISUALISATION POUR LE TIPE
# ==========================================
plt.figure(figsize=(14, 10))

# Flux d'entrée
plt.subplot(3, 1, 1)
plt.plot(time, flux_in, color='black', alpha=0.3, label="Flux brut interpolé")
plt.plot(time, flux_out, color='blue', label="Flux reconstruit après compression")
plt.title("Étape 1 & 3 : Entrée vs Reconstruction (Efficacité)")
plt.legend()

# Les coefficients (ce que l'IA verra)
plt.subplot(3, 1, 2)
plt.stem(details_optimises, markerfmt=' ', basefmt="r-", label="Coefficients de Haar (Détails)")
plt.title("Étape 2 : Coefficients transmis à l'IA (Sobriété)")
plt.ylabel("Intensité du gap")
plt.legend()

# Erreur de reconstruction
plt.subplot(3, 1, 3)
plt.plot(time, flux_in - flux_out, color='red')
plt.title("Erreur de compression (Résidu)")
plt.tight_layout()
plt.show()

# Calcul du gain de sobriété
points_utiles = np.count_nonzero(details_optimises) + len(moyennes)
print(f"Nombre de points initial : {len(flux_in)}")
print(f"Nombre de points après optimisation : {points_utiles}")
print(f"Gain de stockage/calcul : {100 * (1 - points_utiles/len(flux_in)):.1f}%")