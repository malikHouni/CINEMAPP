# people.py
# fichier avec les méthode pour "scrapper" les informations sur wikipedia(infobox et texte de bio)
##################################################################################################

import requests
from bs4 import BeautifulSoup

def remove_citations(text):
    while "[" in text and "]" in text:
        start = text.find("[")
        end = text.find("]")
        if start < end:
            text = text[:start] + text[end+1:]
        else:
            break
    return text

 #nettoyafge de l'infobox_v3
def clean_cell(data_cell):
    for br_tag in data_cell.find_all("br"):
        br_tag.replace_with("\n")
        
    list_items = data_cell.find_all("li")
    if list_items:
        raw_text = ", ".join(li.text for li in list_items)
    else:
        raw_text = data_cell.text.replace("\n", ", ")
        
    text_without_citations = remove_citations(raw_text)
    
    # Remplacer les tabulations, sauts de ligne et multiples espaces présents qui polluent...
    text_without_citations = text_without_citations.replace("\t", " ").replace("\n", " ").replace("\r", " ")
    while "  " in text_without_citations:
        text_without_citations = text_without_citations.replace("  ", " ")
        
    return text_without_citations.strip(" ,")

def get_person_info(name):
    try:
        api_url = f"https://fr.wikipedia.org/w/api.php?action=opensearch&search={name}&limit=1&format=json"
        # user agent plus precis pour pas se faire bloquer sur render
        headers = {"User-Agent": "ProjetCinemaApp/1.0 (contact@cinemaapp.com; Projet Etudiant)"}
        res = requests.get(api_url, headers=headers)
        if res.status_code != 200:
            return None, f"Wikipedia a renvoye une erreur (Status {res.status_code})"
        
        try:
            search_response = res.json()
        except ValueError:
            return None, "Erreur de lecture des donnees Wikipedia (bloque par Wikipedia?)"
            
        if not search_response or not search_response[3]: 
            return None, "Personne non trouvée"
        
        wikipedia_url = search_response[3][0]
        page_soup = BeautifulSoup(requests.get(wikipedia_url, headers=headers).content, "html.parser")
        
        person_data = {
            "name": search_response[1][0], 
            "photo_url": None, 
            "age": None, 
            "profession": None, 
            "notable_works": [], 
            "biography": None
        }
        
        # Le scraping des données de l'infobox (le petit pannel d'informations à droite de la page wiki)
        infobox = page_soup.find(class_=lambda class_name: class_name and "infobox" in class_name)
        if infobox:
            # Recuperer la photo
            photo_element = infobox.find("img")
            if photo_element: 
                image_src = photo_element["src"]
                person_data["photo_url"] = "https:" + image_src if image_src.startswith("//") else image_src
            
            # Recuperer les caractéristiques ligne par ligne
            for row in infobox.find_all("tr"):
                header_cell = row.find("th")
                data_cell = row.find("td")
                
                if header_cell and data_cell:
                    label = header_cell.text.lower().strip()
                    cleaned_value = clean_cell(data_cell)# nettoyage( br, note de page, ...)
                    
                    if "naissance" in label:
                        text_lower = data_cell.text.lower()
                        if "ans" in text_lower:
                            words = text_lower.replace("(", " ").replace(")", " ").split()
                            if "ans" in words:
                                idx = words.index("ans")
                                if idx > 0 and words[idx-1].isdigit():
                                    person_data["age"] = words[idx-1]
                    elif label.startswith(("profession", "activité", "métier")):
                        person_data["profession"] = cleaned_value
                    elif any(keyword in label for keyword in ["œuvres", "oeuvres", "films"]):
                        person_data["notable_works"] = [work.strip() for work in cleaned_value.split(",") if work.strip()]
                        
        # On prend le premier paragraphe de la bio
        content_container = page_soup.find(id="mw-content-text")
        if content_container:
            for paragraph in content_container.find_all("p"):
                paragraph_text = paragraph.text.strip()
                if len(paragraph_text) > 90 and not paragraph.find(id="coordinates"):
                    person_data["biography"] = remove_citations(paragraph_text)
                    break

                
        return person_data, None
        
    except Exception as error:
        return None, f"Erreur de récupération : {str(error)}"
