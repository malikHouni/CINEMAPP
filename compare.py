# compare.py
# Fichier pour les méthodes permettant la comparaison de films sur les critères demandés.
###############################################################

import re
import requests
from bs4 import BeautifulSoup
from movie import get_movie_info#-> on recupere la méthode déjà défini

#necessaire!
def clean_wikipedia_text(text):
    while "[" in text and "]" in text:
        start = text.find("[")
        end = text.find("]")
        if start < end:
            text = text[:start] + text[end+1:]
        else:
            break
    text = text.replace("\t", " ").replace("\n", " ").replace("\r", " ")
    while "  " in text:
        text = text.replace("  ", " ")
    return text.strip()

#Recherche un film sur Wikipédia et extrait son budget depuis l'infobox_v3.
def scrape_wikipedia_movie_budget(movie_title):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    # Premierement, la recherche sur Wikipédia en Français
    try:
        search_url = f"https://fr.wikipedia.org/w/api.php?action=opensearch&search={movie_title}&limit=5&format=json"
        res = requests.get(search_url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            if len(data) > 3 and len(data[3]) > 0:
                url = None
                # on va privilégier les liens contenant "(film)" ou "film"
                for link in data[3]:
                    if "(film)" in link.lower() or "film" in link.lower():
                        url = link
                        break
                if not url:
                    url = data[3][0]
                
                page_res = requests.get(url, headers=headers)
                if page_res.status_code == 200:
                    soup = BeautifulSoup(page_res.content, "html.parser")
                    infobox = soup.find(class_=lambda c: c and "infobox" in c)
                    if infobox:
                        for row in infobox.find_all("tr"):
                            th = row.find("th")
                            td = row.find("td")
                            if th and td and "budget" in th.text.lower():
                                budget = td.text.strip()
                                return clean_wikipedia_text(budget)
    except Exception:
        pass

    # Deuxièment, fallback sur Wikipédia en Anglais si y a pas en france
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={movie_title}&limit=5&format=json"
        res = requests.get(search_url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            if len(data) > 3 and len(data[3]) > 0:
                url = None
                for link in data[3]:
                    if "film" in link.lower():
                        url = link
                        break
                if not url:
                    url = data[3][0]
                
                page_res = requests.get(url, headers=headers)
                if page_res.status_code == 200:
                    soup = BeautifulSoup(page_res.content, "html.parser")
                    infobox = soup.find(class_=lambda c: c and "infobox" in c)
                    if infobox:
                        for row in infobox.find_all("tr"):
                            th = row.find("th")
                            td = row.find("td")
                            if th and td and "budget" in th.text.lower():
                                budget = td.text.strip()
                                return clean_wikipedia_text(budget)
    except Exception:
        pass
    # sinon, perdu , y a rien!    
    return "N/A"

# pour "parser" les montant
def parse_amount(amount_str):
    if not amount_str or amount_str == "N/A":
        return 0
    
    # si c'est du texte avec million/milliard
    if any(m in amount_str.lower() for m in ["million", "milliard", "billion"]):
        # on recupere le premier nombre (ex: 185 ou 12.5)
        match = re.search(r'\d+(?:[.,]\d+)?', amount_str)
        val = float(match.group(0).replace(',', '.')) if match else 0
        mult = 1_000_000_000 if any(b in amount_str.lower() for b in ["milliard", "billion"]) else 1_000_000
        return int(val * mult)
        
    # sinon on garde juste les chiffres
    digits = "".join(c for c in amount_str if c.isdigit())
    return int(digits) if digits else 0


def extract_year(year_str):
    cleaned = ""
    for char in year_str:
        if char.isdigit():
            cleaned += char
        else:
            cleaned += " "
    for word in cleaned.split():
        if len(word) == 4 and (word.startswith("19") or word.startswith("20")):
            return int(word)
    return 0

def extract_runtime(runtime_str):
    digits = ""
    for char in runtime_str:
        if char.isdigit():
            digits += char
        elif digits:
            break
    return int(digits) if digits else 0

def extract_rating(rating_str):
    try:
        return float(rating_str)
    except ValueError:
        return 0.0

# Compare les deux films choisis en interrogeant l'API OMDB et Wikipédia pour recuperer le budget estimé.
def compare_movies(title1, title2, api_key):
    movie1_data, err1 = get_movie_info(title1, api_key)
    if err1:
        return None, None, None, f"Film '{title1}' : {err1}"
        
    movie2_data, err2 = get_movie_info(title2, api_key)
    if err2:
        return None, None, None, f"Film '{title2}' : {err2}"
        
    budget1 = scrape_wikipedia_movie_budget(movie1_data.get("Title"))
    budget2 = scrape_wikipedia_movie_budget(movie2_data.get("Title"))
    
    movie1_data["Budget"] = budget1
    movie2_data["Budget"] = budget2
    
    winners = {
        "Year": 0,
        "Runtime": 0,
        "imdbRating": 0,
        "BoxOffice": 0,
        "Budget": 0,
        "Plus_Rentable":0
    }

    
    # Note IMDb
    rt1 = extract_rating(movie1_data.get("imdbRating", ""))
    rt2 = extract_rating(movie2_data.get("imdbRating", ""))
    if rt1 > rt2: winners["imdbRating"] = 1
    elif rt2 > rt1: winners["imdbRating"] = 2
    
    # Box Office
    b1 = parse_amount(movie1_data.get("BoxOffice", ""))
    b2 = parse_amount(movie2_data.get("BoxOffice", ""))
    if b1 > b2: winners["BoxOffice"] = 1
    elif b2 > b1: winners["BoxOffice"] = 2
    
    # Budget
    bg1 = parse_amount(budget1)
    bg2 = parse_amount(budget2)
    if bg1 > bg2: winners["Budget"] = 1
    elif bg2 > bg1: winners["Budget"] = 2


    # on pourrait aussi voir qui est rentable et attribuer une note dessus....

    return movie1_data, movie2_data, winners, None
