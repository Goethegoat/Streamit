import streamlit as st
import requests
import pandas as pd
from pyquery import PyQuery as pq
import folium
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable

# Lire le fichier Excel pour obtenir les URLs
df = pd.read_excel("liens.xlsx")

# Liste pour stocker les adresses extraites
addresses = []

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

# Boucler sur les URLs et extraire les adresses
for index, row in df.iterrows():
    url = row['URL']
    try:
        response = requests.get(url)
        response.raise_for_status()  # Vérifier si la requête a réussi
        page_html = response.text
        address = extract_address(page_html)
        addresses.append(address)
    except requests.RequestException as e:
        print(f"Erreur lors de la requête HTTP pour le lien {url}: {e}")
        addresses.append("Erreur de requête")
    except Exception as e:
        print(f"Erreur lors de l'extraction des données pour le lien {url}: {e}")
        addresses.append("Erreur d'extraction")

# Ajouter les adresses extraites au DataFrame original
df['Adresse'] = addresses

# Géocodage des adresses
geolocator = Nominatim(user_agent="my_geocoder")
df['Coordonnees'] = df['Adresse'].apply(lambda x: geolocator.geocode(x, timeout=30) if x != "Adresse non trouvée" else None)

# Créer une carte Folium
m = folium.Map()

# Ajouter des marqueurs pour chaque adresse
for index, row in df.iterrows():
    if row['Coordonnees'] is not None:
        folium.Marker(location=[row['Coordonnees'].latitude, row['Coordonnees'].longitude]).add_to(m)

# Afficher la carte dans Streamlit
st.write(m)
