import requests
import pandas as pd
from pyquery import PyQuery as pq
import os

# Lire le fichier Excel pour obtenir les URLs
df = pd.read_excel("liens.xlsx")

# Liste pour stocker les adresses extraites
addresses = []

# Liste pour stocker les informations supplémentaires extraites
additional_info_list = []

# Fonction pour extraire l'adresse d'une page
def extract_address(page_html):
    doc = pq(page_html)
    address = ""
    
    # Rechercher la balise <li> contenant "Adresse :"
    address_li = doc('li:contains("Adresse :")')
    if address_li:
        # Extraire le texte après "Adresse :"
        address_text = address_li.text()
        if "Adresse :" in address_text:
            address = address_text.split("Adresse :")[1].strip()
    
    return address or "Adresse non trouvée"

# Fonction pour extraire les informations de l'URL
def extract_additional_info(page_html):
    doc = pq(page_html)
    info = {
        "Téléphone": "",
        "Accès": "",
        "Twitter": "",
        "Facebook": "",
        "LinkedIn": ""
    }
    
    # Extraction des informations
    info["Téléphone"] = doc('li:contains("Téléphone :")').text().replace("Téléphone :", "").strip()
    info["Accès"] = doc('li:contains("Accès :")').text().replace("Accès :", "").strip()
    info["Twitter"] = doc('a[href*="twitter.com"]').attr('href')
    info["Facebook"] = doc('a[href*="facebook.com"]').attr('href')
    info["LinkedIn"] = doc('a[href*="linkedin.com"]').attr('href')
    
    return info

# Boucler sur les URLs et extraire les adresses et les informations supplémentaires
for index, row in df.iterrows():
    url = row['URL']
    try:
        response = requests.get(url)
        response.raise_for_status()  # Vérifier si la requête a réussi
        page_html = response.text
        address = extract_address(page_html)
        additional_info = extract_additional_info(page_html)
        addresses.append(address)
        additional_info_list.append(additional_info)  # Ajouter les informations supplémentaires
    except requests.RequestException as e:
        print(f"Erreur lors de la requête HTTP pour le lien {url}: {e}")
        addresses.append("Erreur de requête")
        additional_info_list.append({})  # Ajouter un dictionnaire vide en cas d'erreur
    except Exception as e:
        print(f"Erreur lors de l'extraction des données pour le lien {url}: {e}")
        addresses.append("Erreur d'extraction")
        additional_info_list.append({})  # Ajouter un dictionnaire vide en cas d'erreur

# Ajouter les adresses extraites au DataFrame original
df['Adresse'] = addresses

# Créer un DataFrame à partir des informations supplémentaires
additional_info_df = pd.DataFrame(additional_info_list)

# Concaténer le DataFrame des informations supplémentaires avec le DataFrame original
df_concatenated = pd.concat([df, additional_info_df], axis=1)

# Écrire les données mises à jour dans un nouveau fichier xlsx
df_concatenated.to_excel("liens_avec_adresses_et_informations.xlsx", index=False)

# Obtenez le chemin absolu du répertoire de travail actuel
cwd = os.getcwd()
# Ajoutez le nom du fichier Excel pour obtenir le chemin complet
excel_file_path = os.path.join(cwd, "liens_avec_adresses_et_informations.xlsx")
print("Emplacement du fichier Excel:", excel_file_path)
