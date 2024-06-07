Présentation de l’application Streamit
Carte des adresses de coworking à Paris

1.	Web Scapping du site : Annuaire des espaces de coworking | Le Journal du portage salarial (leportagesalarial.com)

Pour commencer ce travail, nous avons besoin de regrouper et récupérer les URL des espaces de coworking dont l’adresse est sur Paris. 
Le programme `Coworking.py` commence par envoyer des requêtes HTTP, traiter les données HTML, effectuer des opérations de traitement de texte et manipuler les fichiers.
Le programme procède ensuite à la récupération du contenu HTML de la page web "https://www.leportagesalarial.com/coworking/" en envoyant une requête HTTP à cette adresse et en récupérant le contenu textuel de la réponse.
Une fois le contenu HTML récupéré, PyQuery est utilisé pour convertir en un objet DOM manipulable. Cela permet au programme de rechercher et de sélectionner les liens qui contiennent le mot "Paris".
En parcourant ces liens sélectionnés, le programme extrait l'URL et le texte de chaque lien. Il effectue ensuite une requête HTTP pour obtenir le contenu de la page pointée par le lien. Ce contenu est analysé à l'aide de PyQuery, et les informations pertinentes sont extraites à l'aide de la fonction `extract_info`. 

# Fonction pour extraire des informations spécifiques d'une page :
def extract_info(page, key, offset):
    if key in page:
        info = page[page.index(key) + offset:]
        return info.strip()
    return ""

Cette fonction est définie pour extraire des informations spécifiques d'une page HTML en fonction d'une clé donnée. Cette fonction est utilisée pour extraire des informations pertinentes des pages web analysées.
Toutes les informations extraites sont ajoutées à une liste appelée `data`. Si une erreur survient lors de l'extraction des informations ou lors de la requête HTTP, le programme affiche un message d'erreur mais continue à traiter les autres liens.
Une fois toutes les données extraites, le programme crée un DataFrame pandas à partir de la liste `data`, avec des colonnes nommées "Nom du lien" et "URL". Enfin, il écrit les données extraites dans un fichier Excel nommé "liens.xlsx" et affiche l'emplacement de ce fichier.

En résumé, le programme extrait les URL des espaces de coworking situés à Paris à partir d'une page web, les stocke dans un fichier Excel, et affiche l'emplacement de ce fichier.
Maintenant, nous avons les liens et allons chercher les informations souhaités sur ces page web. 




2.	Récolte des informations sur chaque url

A partir du fichier liens.xlsx, le programme URLInfo.py va récolter pour chaque URL présent, l’adresse, le téléphone, l’accès, le twitter, le Facebook et le LinkedIn de l’espace coworking visé. Pour cela, le programme se base sur les balises HTML du site web : 
 # Extraction des informations
    info["Téléphone"] = doc('li:contains("Téléphone :")').text().replace("Téléphone :", "").strip()
    info["Accès"] = doc('li:contains("Accès :")').text().replace("Accès :", "").strip()
    info["Twitter"] = doc('a[href*="twitter.com"]').attr('href')
    info["Facebook"] = doc('a[href*="facebook.com"]').attr('href')
    info["LinkedIn"] = doc('a[href*="linkedin.com"]').attr('href')

Ensuite, le programme fait cela pour chaque URL et les ajoute dans un nouveau fichier xlsx : liens_avec_adresses_et_informations.xlsx. Puis comme précédemment, il affiche l’emplacement du fichier. 



3.	Création de la carte avec Folium et Streamlit
Nous avons maintenant tous les éléments pour réaliser la carte des espaces de coworking à Paris. 
Pour commencer, le programme Streamlit lit le fichier liens_avec_adresses_et_informations.xlsx pour obtenir les adresses physiques et non URL des espaces de coworking avec la fonction def extract_additional_info(page_html. 

Ensuite on va utiliser Nominatim pour géocoder les adresses en coordonnées géographiques (latitude et longitude).
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

A partir de ces Latitude et Longitue, le programme crée une carte Folium centrée sur Paris puis il ajoute des marqueurs pour chaque espace de coworking sur la carte, avec des popups contenant les adresses et les informations supplémentaires. Enfin, il affiche la carte Folium dans l'interface Streamlit avec des dimensions spécifiques. 
Pour lancer ce travail on utilise streamlit run Streamlit.py et on obtient : 
![image](https://github.com/Goethegoat/Streamit/assets/90333550/15c96c05-43c8-49af-8869-3a8a9a1caf63)


4.	 Rendre publique l’accès à la carte. 
Pour cela, nous avons besoin d’un repo github depuis lequel lancé notre programme Streamit.py. 
https://github.com/Goethegoat/Streamit
Et ainsi on obtient une adresse URL public : Streamlit · Streamlit (github.dev)



