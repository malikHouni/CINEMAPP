# movie.py
# ficher avec les methodes pour chercher et récuperer les données sur un film dans l'api puis les review et enfin les pires films
#################################################################################################################################

import requests
from bs4 import BeautifulSoup

def get_movie_info(title, api_key):
    url = f"http://www.omdbapi.com/?apikey={api_key}&t={title}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                return data, None
            else:
                return None, data.get("Error", "Film non trouvé.")
        else:
            return None, f"Erreur de connexion à l'API OMDB (Status {response.status_code})."
    except Exception as e:
        return None, f"Erreur de connexion : {str(e)}"

#Formate le titre pour le format d'URL de Rotten Tomatoes
def format_rt_title(title):
    title_clean = title.lower().strip()
    title_clean = title_clean.replace("-", "_").replace(" ", "_")
    title_clean = "".join(c for c in title_clean if c.isalnum() or c == "_")
    while "__" in title_clean:
        title_clean = title_clean.replace("__", "_")
    return title_clean

def get_movie_reviews(movie_title):
    formatted_title = format_rt_title(movie_title)
    url = f"https://www.rottentomatoes.com/m/{formatted_title}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            cards = soup.find_all("review-card-audience")
            reviews = []
            for card in cards[:4]:  # get les commentaires
                drawer = card.find("drawer-more")
                if drawer:
                    text = drawer.text.strip()
                    if text.endswith("See more"):
                        text = text[:-8].strip()
                    elif text.endswith("Show more"):
                        text = text[:-9].strip()
                    reviews.append(text)
                else:
                    p = card.find("p")
                    if p:
                        reviews.append(p.text.strip())
                    else:
                        reviews.append(card.text)
            return reviews
    except Exception:
        pass
    return []

WORST_MOVIES_CACHE = None

# on recupere dans le guide des 100 pires films de tour les temps de Roten Tomatoes, et on mets en cache
def get_worst_movies():
    #Pour éviter d'interroger et de scraper le site Rotten Tomatoes à chaque chargement de page, dans le cache...
    global WORST_MOVIES_CACHE
    if WORST_MOVIES_CACHE is not None:
        return WORST_MOVIES_CACHE, None
        
    url = "https://editorial.rottentomatoes.com/guide/worst-movies-of-all-time/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            items = soup.find_all(class_=lambda c: c and "block-countdown" in c)
            movies = []
            for item in items:
                # Rang
                rank_elem = item.find(class_="indicator")
                rank = rank_elem.text.strip().replace("#", "") if rank_elem else ""
                
                # Titre/lien
                title_elem = item.find(class_="meta-title")
                title = title_elem.text.strip() if title_elem else ""
                link = title_elem["href"] if title_elem and title_elem.has_attr("href") else ""
                
                # Année
                year_elem = item.find(class_="meta-year")
                year_str = year_elem.text.strip() if year_elem else ""
                year = 0
                if year_str:
                    clean_year = "".join(c for c in year_str if c.isdigit())
                    if len(clean_year) == 4:
                        year = int(clean_year)
                
                # Tomatometer / l'audience
                scores_wrapper = item.find(class_="meta-scores-wrapper")
                tomatometer = ""
                audience = ""
                if scores_wrapper:
                    score_spans = scores_wrapper.find_all(class_="tMeterScore")
                    if len(score_spans) > 0:
                        tomatometer = score_spans[0].text.strip()
                    if len(score_spans) > 1:
                        audience = score_spans[1].text.strip()
                
                # Image poster
                img_elem = item.find("img", class_="article_poster")
                image_url = img_elem["src"] if img_elem and img_elem.has_attr("src") else ""
                
                # Consensus, Synopsis, Casting actors, Réalisateur,... le contenue en somme!
                consensus = ""
                synopsis = ""
                starring = []
                director = ""
                
                details = item.find_all(class_="meta-detail")
                for d in details:
                    text_content = d.text.strip()
                    text_content = text_content.replace("\t", " ").replace("\n", " ").replace("\r", " ")
                    while "  " in text_content:
                        text_content = text_content.replace("  ", " ")
                        
                    if "Critics Consensus:" in text_content:
                        consensus = text_content.replace("Critics Consensus:", "").strip()
                    elif "Synopsis:" in text_content:
                        synopsis = text_content.replace("Synopsis:", "").strip()
                        if synopsis.endswith("View Full Synopsis"):
                            synopsis = synopsis[:-18].strip()
                    elif "Starring:" in text_content:
                        starring_text = text_content.replace("Starring:", "").strip()
                        starring = [s.strip() for s in starring_text.split(",") if s.strip()]
                    elif "Directed By:" in text_content:
                        director = text_content.replace("Directed By:", "").strip()
                
                movies.append({
                    "rank": int(rank) if rank.isdigit() else 999,
                    "title": title,
                    "link": link,
                    "year": year,
                    "tomatometer": tomatometer,
                    "audience": audience,
                    "image_url": image_url,
                    "consensus": consensus,
                    "synopsis": synopsis,
                    "starring": starring,
                    "director": director
                })
            
            movies.sort(key=lambda x: x["rank"])
            WORST_MOVIES_CACHE = movies
            return movies, None
    except Exception as e:
        return [], f"Erreur de récupération : {str(e)}"
    return [], "Impossible de charger la page."
