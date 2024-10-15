import requests
import json
import webbrowser
import config
from collections import Counter

user_id_arnaud = '11122778696'
client_secret = config.CLIENT_SECRET
redirect_uri = config.REDIRECT_URI
REDIRECT_URI='http://localhost:8889/callback'
BASE_URL = 'https://api.spotify.com/v1/'
client_id = config.CLIENT_ID

# GET code for scope 
def get_code_with_scope(CLIENT_ID = client_id, *additional_scopes):
    # Impression des valeurs pour débogage
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
def create_header(code, CLIENT_ID = client_id, CLIENT_SECRET = client_secret): 
    
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
    #print(playlists)
## Recupère la list des playlists et affiche le playlist_id
    for playlist in playlists['items']:
       print(playlist['name'], ' --- ', playlist['href'])


# fonction qui print la liste des tracks
def print_track_for_playlist(headers, PLAYLIST) :
    url = f"{BASE_URL}playlists/{PLAYLIST}"
    response = requests.get(url, headers=headers)
    song_playlist = response.json()
    for song in song_playlist['tracks']['items']:
        print(song['track']['name'], ' --- ', song['track']['artists'][0]['name'], '---', song['track']['uri'])
        uris_dict["uris"].append(song['track']['uri'])

# fonction qui retourne une liste d'uri des tracks
def get_track_for_playlist(headers, PLAYLIST) :
    uris_dict = {"uris": []}
    url = f"{BASE_URL}playlists/{PLAYLIST}"
    response = requests.get(url, headers=headers)
    song_playlist = response.json()
    for song in song_playlist['tracks']['items']:
        uris_dict["uris"].append(song['track']['uri'])
    return uris_dict

#Créer une playliste
def create_playlist(headers, playlist_name, user = user_id_arnaud) :
    new_playlist = json.dumps({
      "name": playlist_name,
      "description": "create by API",
      "public": False
      })
    #création d'une playlist
    response = requests.post(BASE_URL  + 'users/'+ user +'/playlists',  data=new_playlist, headers=headers)
    return response.json()

def merge_playlist(headers, output_playlist_id, input_playlist_id, user = user_id_arnaud):
    uris_dict_to_merge = get_track_for_playlist(headers, input_playlist_id)
    response = requests.post(BASE_URL + 'playlists/' + output_playlist_id +'/tracks', json=uris_dict_to_merge, headers=headers)
    print(response.status_code)
    return response.json()

# Recuperer la liste des tracks en plusieurs exemplaire
def find_duplicate_track(headers, playlist_id):
    uris_dict_songs = get_track_for_playlist(headers, playlist_id)
    uri_counts = Counter(uris_dict_songs['uris'])
    # Extraire les URI qui apparaissent plus d'une fois
    duplicates_list = [uri for uri, count in uri_counts.items() if count > 1]
    # Construire la liste de dictionnaires pour les pistes
    tracks_list = [{"uri": uri} for uri in duplicates_list]
    print(tracks_list)
    return tracks_list

def delete_duplicate_track(headers, playlist_id):
    uris_duplicate_songs = find_duplicate_track(headers, playlist_id)
    # Recupere le snapshot_id
    snapshot_id= requests.get(BASE_URL + 'playlists/' + playlist_id, headers=headers).json()['snapshot_id']
    # Construire le dictionnaire final 
    data = {
        "tracks": uris_duplicate_songs,
        "snapshot_id": snapshot_id
    }
    print(data)
    #response = requests.delete(BASE_URL + 'playlists/' + playlist_id, data=data, headers=headers)
    #print(response.status_code)
    #return response.json()

#def intersection_listes(*listes):
#    # Convertir les listes en ensembles pour utiliser l'intersection
#    ensembles = map(set, listes)
#    # Calculer l'intersection de tous les ensembles
#    resultat = set.intersection(*ensembles)
#    # Convertir le résultat en liste
#    return list(resultat)


def json_in_file(PATH, JSON):
    with open(PATH, 'w') as file:
      # Ecrire le JSON dans le fichier
      json.dump(JSON, file, indent=1)

#def main():
#    get_code_with_scope()

#if __name__ == "__main__":
#    main()