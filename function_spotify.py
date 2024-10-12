import requests
import json
import webbrowser
import config

user_id_arnaud = config.user_id_arnaud
CLIENT_ID = config.CLIENT_ID
CLIENT_SECRET = config.CLIENT_SECRET
redirect_uri = config.REDIRECT_URI
REDIRECT_URI='http://localhost:8889/callback'
BASE_URL = config.BASE_URL

# GET code for scope 
def get_code_with_scope(CLIENT_ID, *additional_scopes):
    # Impression des valeurs pour débogage
    print(f"CLIENT_ID: {CLIENT_ID}")
    print(f"REDIRECT_URI: {REDIRECT_URI}")
    # Liste des scopes de base
    base_scopes = [
        "playlist-modify-private",
        "playlist-read-private",
        "playlist-modify-public",
        "user-library-read"
    ]
    # Ajout des scopes supplémentaires, s'ils sont fournis
    if additional_scopes:
        base_scopes.extend(additional_scopes)
    # Concaténation des scopes en une chaîne unique
    scopes = " ".join(base_scopes)
    # Construire l'URL d'autorisation
    auth_url = f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={scopes}"
    # Ouvrir l'URL dans le navigateur
    webbrowser.open(auth_url)

#Creer le header a partir du code
def create_header(code): 
    
    # Préparer les données pour l'échange de code
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    # Faire la requête pour obtenir le token
    auth_response = requests.post('https://accounts.spotify.com/api/token', data=data)
    auth_response_data = auth_response.json()
    # Sauvegarder le token d'accès
    access_token = auth_response_data['access_token']
    
    # Maintenant vous pouvez utiliser ce token pour accéder aux endpoints nécessitant les scopes autorisés
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    return headers

# Recuperer la liste des Playlists d'un user
def get_playlist_for_user(headers, user = user_id_arnaud, limits = '50') :
    url = f"{BASE_URL}users/{user}/playlists?limit={limits}"
    response = requests.get(url, headers=headers)
    playlists = response.json()
    print(playlists)
## Recupère la list des playlists et affiche le playlist_id
    for playlist in playlists['items']:
       print(playlist['name'], ' --- ', playlist['href'])

# fonction qui retourne une liste d'uri des tracks
def get_track_for_playlist(playlist) :
    list_uris = []
    for song in playlist['tracks']['items']:
        list_uris.append(song['track']['uri'])
    return list_uris

#Créer une playliste
def create_playlist(playlist_name, user = user_id_arnaud) :
    new_playlist = json.dumps({
      "name": playlist_name,
      "description": "create by API",
      "public": False
      })
    #création d'une playlist
    requests.post(BASE_URL  + 'users/'+ user +'/playlists',  data=new_playlist, headers=headers)
    return response.json()

def intersection_listes(*listes):
    # Convertir les listes en ensembles pour utiliser l'intersection
    ensembles = map(set, listes)
    # Calculer l'intersection de tous les ensembles
    resultat = set.intersection(*ensembles)
    # Convertir le résultat en liste
    return list(resultat)


#def main():
#    get_code_with_scope()

#if __name__ == "__main__":
#    main()