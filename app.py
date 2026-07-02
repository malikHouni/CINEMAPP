# app.py
# fichier principale qui sert de "tour de controle" de l'application
####################################################################

import os
from dotenv import load_dotenv #<- pour charger le fichier .env
from flask import Flask, render_template, request, redirect, url_for
from movie import get_movie_info, get_movie_reviews, get_worst_movies
from people import get_person_info#<- ajout de recupération de la méthode pour les personne
from compare import compare_movies#<- ajout de recupération de la méthode pour la comparaison

load_dotenv()

app = Flask(__name__)

# ma clé api pour les film(qu'on charge depuis le .env uniquement!)
OMDB_API_KEY = os.environ.get("OMDB_API_KEY")

# route home
@app.route('/')
def index():
    return render_template('index.html')

#route pour la recherche de personne
@app.route('/personne', methods=['GET', 'POST'])
def personne():
    name = None
    person_data = None
    error = None

    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            person_data, error = get_person_info(name)
        else:
            error = "Entrez un nom"

    return render_template('personne.html', name=name, person=person_data, error=error)

#route pour la recherche de personne
@app.route('/film', methods=['GET', 'POST'])
@app.route('/movie', methods=['GET', 'POST'])  # Alias 
def film():
    # Si la route accédée est /movie, on redirige vers la route /film 
    title = None
    movie_data = None
    reviews = []
    error = None

    if request.method == 'POST':
        title = request.form.get('title')
        if title:
            # Appel des fonctions dans le fichier movie.py
            movie_data, error = get_movie_info(title, OMDB_API_KEY)
            if movie_data:
                reviews = get_movie_reviews(title)
        else:
            error = "Veuillez entrer un titre de film."

    return render_template('film.html', title=title, movie=movie_data, reviews=reviews, error=error)

#route pour la comparaison entre 2 films choisis
@app.route('/comparer', methods=['GET', 'POST'])
@app.route('/compare', methods=['GET', 'POST'])  # Alias
def comparer():
    title1 = None
    title2 = None
    movie1 = None
    movie2 = None
    winners = None
    error = None

    if request.method == 'POST':
        title1 = request.form.get('title1')
        title2 = request.form.get('title2')
        if title1 and title2:
            movie1, movie2, winners, error = compare_movies(title1, title2, OMDB_API_KEY)
        else:
            error = "Veuillez entrer les titres des deux films."

    return render_template('comparer.html', title1=title1, title2=title2, movie1=movie1, movie2=movie2, winners=winners, error=error)

# route pour les pires films de tous les temps et par année
@app.route('/pires')
def pires():
    year = request.args.get('year', '')
    movies, error = get_worst_movies()
    
    # Extraire les années uniques des pires films( de 2025 a 1982)
    years = []
    if movies:
        years = sorted(list(set(m['year'] for m in movies if m['year'] > 0)), reverse=True)
        
    selected_year = None
    if year.isdigit():
        selected_year = int(year)
        filtered_movies = [m for m in movies if m['year'] == selected_year]
        title_suffix = f" de l'année {selected_year}"
    else:
        filtered_movies = movies
        title_suffix = " de tous les temps"
        
    top_movies = filtered_movies[:10]
    
    return render_template('pires.html', movies=top_movies, years=years, selected_year=selected_year, title_suffix=title_suffix, error=error)

# main pour lancer le server
if __name__ == '__main__':
    # on ecoute sur 0.0.0.0 et sur le port de render pour que ca marche en ligne
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
