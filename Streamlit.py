import streamlit as st
import requests
import pandas as pd
from pyquery import PyQuery as pq
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from streamlit_folium import st_folium

# Lire le fichier Excel pour obtenir les URLs
df = pd.read_excel("liens.xlsx")

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
        "Adresse": "",
        "Téléphone": "",
        "Accès": "",
        "Twitter": "",
        "Facebook": "",
        "LinkedIn": ""
    }
    
    # Extraction des informations
    info["Adresse"] = doc('li:contains("Adresse :")').text().replace("Adresse :", "").strip()
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
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Vérifier si la requête a réussi
        page_html = response.text
        address = extract_address(page_html)
        additional_info = extract_additional_info(page_html)
        df.at[index, 'Adresse'] = address  # Mettre à jour l'adresse dans le DataFrame
        for key, value in additional_info.items():
            df.at[index, key] = value  # Mettre à jour les informations supplémentaires dans le DataFrame
    except requests.RequestException as e:
        st.write(f"Erreur lors de la requête HTTP pour le lien {url}: {e}")
    except Exception as e:
        st.write(f"Erreur lors de l'extraction des données pour le lien {url}: {e}")

# Géocodage des adresses
geolocator = Nominatim(user_agent="my_geocoder")
latitudes = []
longitudes = []
for address in df['Adresse']:
    if address not in ["Adresse non trouvée", "Erreur de requête", "Erreur d'extraction"]:
        try:
            location = geolocator.geocode(address, timeout=30)
            if location:
                latitudes.append(location.latitude)
                longitudes.append(location.longitude)
            else:
                latitudes.append(None)
                longitudes.append(None)
        except (GeocoderUnavailable, requests.RequestException) as e:
            st.write(f"Le géocodage de l'adresse {address} a échoué en raison d'une erreur de connexion : {e}")
            latitudes.append(None)
            longitudes.append(None)
    else:
        latitudes.append(None)
        longitudes.append(None)

df['Latitude'] = latitudes
df['Longitude'] = longitudes

# Créer une carte Folium avec un titre et des dimensions spécifiques
m = folium.Map(location=[48.8566, 2.3522], zoom_start=12, width=800, height=600)  # Centrer la carte sur Paris

# Ajouter des marqueurs pour chaque adresse avec le texte de l'adresse et les informations supplémentaires dans le popup
for index, row in df.iterrows():
    if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
        popup_text = f"<div style='font-size: 14px'><strong>Adresse :</strong> {row['Adresse']}<br>"
        popup_text += f"<strong>Téléphone :</strong> {row['Téléphone']}<br>"
        popup_text += f"<strong>Accès :</strong> {row['Accès']}<br>"
        popup_text += f"<strong>Twitter :</strong> <a href='{row['Twitter']}' target='_blank'>{row['Twitter']}</a><br>"
        popup_text += f"<strong>Facebook :</strong> <a href='{row['Facebook']}' target='_blank'>{row['Facebook']}</a><br>"
        popup_text += f"<strong>LinkedIn :</strong> <a href='{row['LinkedIn']}' target='_blank'>{row['LinkedIn']}</a><br></div>"
        folium.Marker(location=[row['Latitude'], row['Longitude']], popup=popup_text).add_to(m)

# Afficher la carte dans Streamlit avec un titre
st.title("Carte des adresses de coworking à Paris")
st.markdown("Coworking à Paris en 2024")

# Afficher la carte Folium dans Streamlit avec des dimensions spécifiques
st_folium(m, width=800, height=600)
