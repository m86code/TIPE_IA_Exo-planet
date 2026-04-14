import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt

def get_star_window(kepler_id, start_day, duration_days, target_points=4000):
    """
    Télécharge les données, sélectionne une fenêtre temporelle précise
    et comble les vides par interpolation linéaire.
    """
    print(f"--- Recherche de {kepler_id} ---")
    
    # 1. Téléchargement et assemblage (on prend plusieurs quarters pour avoir du choix)
    search = lk.search_lightcurve(kepler_id, author="Kepler")
    lc = search[:4].download_all().stitch() 
    
    # 2. Prétraitement classique (Aplatissement)
    lc_flat = lc.flatten(window_length=401)
    
    # 3. SÉLECTION DE LA ZONE (Windowing)
    # On filtre les données entre t_start et t_start + durée
    mask = (lc_flat.time.value >= start_day) & (lc_flat.time.value <= start_day + duration_days)
    lc_window = lc_flat[mask]
    
    if len(lc_window) == 0:
        print("Erreur : Aucune donnée dans cette fenêtre temporelle.")
        return None

    # 4. INTERPOLATION (La "droite" pour boucher les trous)
    # On crée un axe de temps parfaitement régulier pour l'IA
    t_min, t_max = lc_window.time.value.min(), lc_window.time.value.max()
    time_regular = np.linspace(t_min, t_max, target_points)
    
    # np.interp relie les points existants par des segments de droite
    # Cela remplace les NaNs et les zones sans mesures
    flux_interp = np.interp(time_regular, lc_window.time.value, lc_window.flux.value)
    
    return time_regular, flux_interp, lc_window

# --- PARAMÈTRES À MODIFIER ---
KEPLER_ID = "Kepler-90"
DEBUT = 130      # Jour de début (regardez les axes de vos précédents graphes)
DUREE = 30       # Durée de la fenêtre en jours
POINTS = 3000    # Résolution du vecteur final

# --- EXÉCUTION ---
time_final, flux_final, lc_raw_window = get_star_window(KEPLER_ID, DEBUT, DUREE, POINTS)

if flux_final is not None:
    plt.figure(figsize=(15, 6))
    
    # On affiche les points interpolés (le vecteur "propre")
    plt.plot(time_final, flux_final, label="Flux Interpolé (Vecteur IA)", color='#1f77b4', alpha=0.8)
    
    # On affiche les points réels par dessus pour voir la différence
    plt.scatter(lc_raw_window.time.value, lc_raw_window.flux.value, 
                s=5, color='red', label="Données Réelles (Kepler)", alpha=0.5)

    plt.axhline(1.0, color='black', linestyle='--', alpha=0.3)
    plt.title(f"Fenêtre de {DUREE} jours sur {KEPLER_ID} (Début : jour {DEBUT})")
    plt.xlabel("Temps (Barycentric Julian Day - 2454833)")
    plt.ylabel("Flux Normalisé")
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.show()

    print(f"Vecteur de {len(flux_final)} points généré avec succès.")
    print(flux_final)