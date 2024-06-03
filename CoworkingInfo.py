import requests
import pandas as pd
from pyquery import PyQuery as pq
import re
import os

# Fonction pour extraire des informations spécifiques d'une page :
def extract_info(page, key, offset):
    if key in page:
        info = page[page.index(key) + offset:]
        return info.strip()
    return ""

url = "https://www.leportagesalarial.com/coworking/"

# Récupérer le contenu HTML de la page :
response = requests.get(url)
contenu_html = response.text

# Utiliser PyQuery pour parser le contenu HTML :
doc = pq(contenu_html)

# Sélectionner les liens contenant "Paris" :
links = doc('a:contains("Paris")')

data = []

# Boucler sur les liens sélectionnés et extraire les informations nécessaires :
for link in links:
    try:
        # Extraire l'URL du lien :
        link_url = link.attrib['href']
        # Extraire le texte du lien :
        link_name = link.text

        # Faire une requête HTTP GET pour obtenir le contenu de la page pointée par le lien :
        rep_image = requests.get(link_url)
        rep_image.raise_for_status()  # Vérifier si la requête a réussi
        # Lire le contenu de la réponse et le stocker dans 'page_image' :
        page_image = rep_image.text
        # Utiliser PyQuery pour parcourir le contenu HTML de la page :
        page = pq(page_image)

        # Ajouter les informations récupérées à la liste 'data' :
        data.append([link_name, link_url])
    except requests.RequestException as e:
        print(f"Erreur lors de la requête HTTP pour le lien {link_url}: {e}")
    except Exception as e:
        print(f"Erreur lors de l'extraction des données pour le lien {link_url}: {e}")

# Créer un DataFrame à partir des données récupérées :
df = pd.DataFrame(data, columns=["Nom du lien", "URL"])

# Écrire les données dans un fichier xlsx :
df.to_excel("liens.xlsx", index=False)

# Obtenez le chemin absolu du répertoire de travail actuel
cwd = os.getcwd()
# Ajoutez le nom du fichier Excel pour obtenir le chemin complet
excel_file_path = os.path.join(cwd, "liens.xlsx")
print("Emplacement du fichier Excel:", excel_file_path)
