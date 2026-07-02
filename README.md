# Projet Cinéma App - par Malik HOUNI pour Progress Factory 2026

Application web moderne en **Python** avec **Flask**. Elle intègre des appels d'**API** et du **web scraping** pour rechercher des informations sur les films, comparer des œuvres, découvrir le parcours des personnalités du cinéma et recenser les pires films de l'histoire en bonus.

---

## Fonctionnalités

L'application est composée de 5 modules principaux :

1. **Page d'Accueil (Home) :**
   * Une interface épurée avec un système de grille Bootstrap 5 offrant des raccourcis vers toutes les fonctionnalités. Ajouts d'émojie pour rendre plus attirant et pro.
2. **Page de Recherche de Films :**
   * Interrogation de l'**API OMDB** pour obtenir les détails du film (affiche, genre, réalisateur, casting, synopsis, note IMDb, box-office, etc.).
   * Extraction par **Web Scraping** en temps réel sur **Rotten Tomatoes** des derniers commentaires des spectateurs.
3. **Page de Recherche de Personnalités :**
   * Recherche d'acteurs, réalisateurs ou producteurs en effectuant du **Web Scraping** sur **Wikipédia**.
   * Extraction dynamique de la photo de profil (infobox), de l'âge, d'une courte biographie, de la profession et de la liste des œuvres notables.
4. **Page de Comparaison :**
   * Comparaison face-à-face de deux films.
   * Récupération automatique du budget de chaque film via scraping Wikipédia.
   * Tableau comparatif avec **mise en valeur automatique (en vert) des vainqueurs** pour chaque critère (film le plus récent, plus long, mieux noté, plus grand succès au box-office, plus gros budget).
5. **Page des Pires Films (Top 10) :**
   * Liste des pires catastrophes cinématographiques de l'histoire (récupérée par scraping depuis l'éditorial *Rotten Tomatoes*).
   * **Filtrage par année** intégré permettant d'obtenir le classement spécifique d'une année.
   * Affichage des scores du Tomatometer et du public, ainsi que le consensus critique et le synopsis.

---

## Architecture du Projet

Le projet est structuré de la manière suivante :

```text
stepFinal/
├── .env                # fichier d'environnement pour variable secrets
├── app.py              # Point d'entrée de l'application Flask et gestion/définition des routes
├── movie.py            # Logique liée aux films (OMDB API, scraping Rotten Tomatoes & pire film)
├── people.py           # Logique de scraping Wikipédia pour les personnalités du cinéma
├── compare.py          # Logique de comparaison et parsing des données financières/temporelles
├── requirements.txt    # Liste des dépendances Python du projet
├── Projet_Cinema.md    # Cahier des charges et instructions du projet
├── README.md           # Documentation générale de l'application (ce fichier)
└── templates/          # Dossier contenant les templates HTML (Bootstrap 5)
    ├── base.html       # Squelette de base avec la barre de navigation globale
    ├── index.html      # Page d'accueil de l'application
    ├── film.html       # Interface de recherche de film et avis spectateurs
    ├── personne.html   # Fiche de présentation d'une personnalité
    ├── comparer.html   # Tableau de comparaison face-à-face
    └── pires.html      # Classement des pires films avec filtre par année
```

---

## Installation et Lancement

### 1. Prérequis
Il est nécessaire d'avoir **Python 3** installé sur la machine. Et au mieux faire un virtual environnement.

### 2. Accéder au répertoire
Se positionner dans le dossier du projet :
```bash
cd ProjetCinemaByStep/stepFinal
```

### 3. Installer les dépendances
Installer les bibliothèques requises répertoriées dans `requirements.txt` :
```bash
pip install -r requirements.txt
```

### 4. Clé API OMDB (Optionnel)
Par défaut, l'application utilise une clé API déjà configurée dans le fichier `app.py`. Pour utiliser une autre clé, il est possible de définir la variable d'environnement :
```bash
export OMDB_API_KEY="votre_cle_api"
```

### 5. Lancer l'application
Démarrer le serveur local de développement Flask :
```bash
python app.py
```

### 6. Accéder au site web
Ouvrir un navigateur web et se rendre à l'adresse suivante :
[http://127.0.0.1:5000](http://127.0.0.1:5000)

### Conclusion: 
Merci d'avoir lu ce Readme.
