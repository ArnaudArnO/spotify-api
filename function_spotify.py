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
def get_playlist_for_user(headers, user=user_id_arnaud, limit=50):
    url = f"{BASE_URL}users/{user}/playlists"
    params = {"limit": limit, "offset": 0}
    all_playlists = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        playlists = response.json()
        # Vérifier que la réponse contient des playlists
        if 'items' not in playlists:
            break
        # Ajouter les playlists à la liste complète
        all_playlists.extend(playlists['items'])
        
        # Vérifier s'il reste des playlists à récupérer
        if playlists['next'] is not None:
            params['offset'] += limit
        else:
            break

    # Préparer les données à enregistrer avec seulement le nom et l'URI
    playlists_data = [{"name": playlist['name'], "uri": playlist['uri']} for playlist in all_playlists]
    # Nom du fichier basé sur l'ID de l'utilisateur
    output_file = f"/tmp/playlist_for_{user}.json"
    # Enregistrer les données dans un fichier
    json_in_file(output_file, playlists_data)
    # Afficher les playlists
    for playlist in playlists_data:
        print(playlist['name'], ' --- ', playlist['uri'])
    print(f"Les détails des playlists ont été enregistrés dans {output_file}.")
    return all_playlists



# fonction qui print la liste des tracks
def print_track_for_playlist(headers, PLAYLIST, output_file=None):
    url = f"{BASE_URL}playlists/{PLAYLIST}/tracks"
    params = {"limit": 100, "offset": 0}
    all_tracks = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        song_playlist = response.json()
        # Vérifier que la réponse contient des chansons
        if 'items' not in song_playlist:
            break
        # Accumuler les détails des morceaux
        for song in song_playlist['items']:
            if song['track'] and song['track']['name'] and song['track']['artists']:
                track_name = song['track']['name']
                track_uri = song['track']['uri']
                # Ajouter les détails du morceau à la liste
                all_tracks.append({"name": track_name, "uri": track_uri})
        # Vérifier s'il reste des chansons à récupérer
        if song_playlist['next'] is not None:
            params['offset'] += 100
        else:
            break
    # Nom du fichier basé sur l'ID de la playlist
    output_file = f"/tmp/tracks_for_{PLAYLIST}.json"
    # Enregistrer les données dans un fichier
    json_in_file(output_file, all_tracks)
    # Afficher les morceaux
    for track in all_tracks:
        print(f"{track['name']} --- {track['uri']}")
    print(f"Les détails des morceaux ont été enregistrés dans {output_file}.")


## Recuperer toute les musiques d'une playlist
def get_track_for_playlist(headers, PLAYLIST):
    uris_dict = {"uris": []}
    url = f"{BASE_URL}playlists/{PLAYLIST}/tracks"
    params = {"limit": 100, "offset": 0}
    while True:
        response = requests.get(url, headers=headers, params=params)
        song_playlist = response.json()
        # Vérifier que la réponse contient des chansons
        if 'items' not in song_playlist:
            break
        # Ajouter les chansons à la liste des URIs
        for song in song_playlist['items']:
            if song['track'] and song['track']['uri']:
                uris_dict["uris"].append(song['track']['uri'])
        # Vérifier s'il reste des chansons à récupérer
        if song_playlist['next'] is not None:
            params['offset'] += 100
        else:
            break 
    return uris_dict

#Créer une playlist
def create_playlist(headers, playlist_name, user = user_id_arnaud) :
    # Demander à l'utilisateur si la playlist doit être publique
    public_input = input("La playlist doit-elle être publique ? ((oui/y/yes)/non) : ").strip().lower()
    is_public = public_input in ['oui', 'y', 'yes']
    
    # Demander la description de la playlist
    description = input("Entrez la description de la playlist (laisser vide pour 'create by API') : ").strip()
    if not description:
        description = "create by API"
    
    # Construire les données de la nouvelle playlist
    new_playlist = json.dumps({
        "name": playlist_name,
        "description": description,
        "public": is_public
    })
    
    #création d'une playlist
    response = requests.post(BASE_URL  + 'users/'+ user +'/playlists',  data=new_playlist, headers=headers)
    return response.json()

def merge_playlist(headers, output_playlist_id, input_playlist_id, user=user_id_arnaud):
    # Récupérer les URIs des pistes de la playlist source
    uris_dict_to_merge = get_track_for_playlist(headers, input_playlist_id)["uris"]
    
    # Diviser les URIs en lots de 100
    batch_size = 100
    for i in range(0, len(uris_dict_to_merge), batch_size):
        # Créer un sous-ensemble de 100 URIs maximum
        batch_uris = uris_dict_to_merge[i:i + batch_size]
        payload = {"uris": batch_uris}
        
        # Envoyer le batch à la playlist de destination
        response = requests.post(
            f"{BASE_URL}playlists/{output_playlist_id}/tracks",
            json=payload,
            headers=headers
        )
        
        # Vérifier la réponse
        if response.status_code != 201:  # 201 Created est le code attendu
            print(f"Erreur lors de l'ajout des pistes : {response.status_code}")
            print(response.json())
            return response.json()

    print("Les pistes ont été fusionnées avec succès dans la playlist de destination.")
    return {"status": "success"}


## Fonction pour savoir si toute les musiques d'une playlist sont dans une autre
def can_i_delete_playlist(headers, playlist_master, playlist_2):
    # Récupérer les URIs des chansons de la playlist master
    name_master = requests.get(BASE_URL + 'playlists/' + playlist_master, headers=headers).json()['name']
    name_2 = requests.get(BASE_URL + 'playlists/' + playlist_2, headers=headers).json()['name']
    uris_master = set(get_track_for_playlist(headers, playlist_master)['uris'])
    # Récupérer les URIs des chansons de la playlist 2
    uris_playlist_2 = get_track_for_playlist(headers, playlist_2)['uris']
    # Trouver les chansons qui ne sont pas dans la playlist master
    missing_tracks = []
    
    for uri in uris_playlist_2:
        if uri not in uris_master:
            # Récupérer les détails du morceau manquant
            track_info = requests.get(f"{BASE_URL}tracks/{uri.split(':')[-1]}", headers=headers).json()
            missing_tracks.append({'uri': uri, 'name': track_info['name']})
    
    # Vérifier s'il y a des chansons manquantes
    if missing_tracks:
        print(f'Certaines chansons de la playlist {name_2} ne sont pas dans la playlist {name_master}.')
        print('Vous risquez de perdre les morceaux suivants si vous supprimez la playlist :')
        for track in missing_tracks:
            print(f"- {track['name']} (URI: {track['uri']})")
        return [track['uri'] for track in missing_tracks]
    else:
        print(f'Toutes les chansons de la playlist {name_2} sont déjà dans la playlist {name_master}. Vous pouvez supprimer la playlist sans perdre de musique.')
        return []

def are_tracks_in_playlist(headers, playlist_id, track_uris):
    # Récupérer les URIs des chansons de la playlist cible
    uris_in_playlist = set(get_track_for_playlist(headers, playlist_id)['uris'])
    
    # Vérifier si chaque morceau est présent dans la playlist
    missing_tracks = [uri for uri in track_uris if uri not in uris_in_playlist]
    
    # Retourner les résultats
    if missing_tracks:
        print("Certains morceaux ne sont pas dans la playlist :")
        for uri in missing_tracks:
            print(f"- URI manquant : {uri}")
        return False, missing_tracks
    else:
        print("Tous les morceaux sont présents dans la playlist.")
        return True, []

# Recuperer la liste des tracks en plusieurs exemplaire
def find_duplicate_track(headers, playlist_id):
    # Récupérer les URIs des chansons de la playlist
    uris_dict_songs = get_track_for_playlist(headers, playlist_id)
    uri_counts = Counter(uris_dict_songs['uris'])
    # Extraire les URI qui apparaissent plus d'une fois
    duplicates_list = [uri for uri, count in uri_counts.items() if count > 1]
    
    # Afficher les noms des titres en double
    if duplicates_list:
        print("Les pistes suivantes sont en double dans la playlist :")
        for uri in duplicates_list:
            # Récupérer le nom de la chanson
            track_info = requests.get(f"{BASE_URL}tracks/{uri.split(':')[-1]}", headers=headers).json()
            print(f"- {track_info['name']} (URI: {uri})")
    else:
        print("Aucun doublon trouvé dans la playlist.")
    
    # Retourner la liste des URIs en double
    return duplicates_list

def delete_duplicate_track(headers, playlist_id):
    # Récupère les URI des morceaux en double
    uris_duplicate_songs = find_duplicate_track(headers, playlist_id)
    if not uris_duplicate_songs:
        print("Aucun doublon trouvé.")
        return {"status": "no_duplicates"}
    # Récupérer le snapshot_id de la playlist
    response_playlist = requests.get(BASE_URL + f'playlists/{playlist_id}', headers=headers)
    snapshot_id = response_playlist.json().get('snapshot_id')
    # Vérifier si le snapshot_id a bien été récupéré
    if not snapshot_id:
        print("Impossible de récupérer le snapshot_id.")
        return {"status": "snapshot_id_error"}
    # Préparer la suppression des pistes par lots de 100
    batch_size = 100
    for i in range(0, len(uris_duplicate_songs), batch_size):
        batch_uris = uris_duplicate_songs[i:i + batch_size]
        tracks_list = [{"uri": uri} for uri in batch_uris]
        delete_tracks = {
            "tracks": tracks_list,
            "snapshot_id": snapshot_id
        }
        # Envoyer la requête de suppression
        response_delete = requests.delete(
            BASE_URL + f'playlists/{playlist_id}/tracks',
            json=delete_tracks,
            headers=headers
        )
        if response_delete.status_code != 200:
            print(f"Erreur lors de la suppression des doublons : {response_delete.status_code}")
            print(response_delete.json())
            return response_delete.json()
    print("Doublons supprimés avec succès.")

    # Ré-ajouter les morceaux uniques supprimés, par lots de 100
    for i in range(0, len(uris_duplicate_songs), batch_size):
        batch_uris = uris_duplicate_songs[i:i + batch_size]
        add_tracks = {"uris": batch_uris}

        response_add = requests.post(
            BASE_URL + f'playlists/{playlist_id}/tracks',
            json=add_tracks,
            headers=headers
        )
        if response_add.status_code != 201:  # 201 Created est le code attendu
            print(f"Erreur lors de la réinsertion des morceaux : {response_add.status_code}")
            print(response_add.json())
            return response_add.json()
    
    print("Morceaux uniques réintégrés avec succès dans la playlist.")
    return {"status": "success"}





def json_in_file(PATH, JSON_FILE):
    with open(PATH, 'w') as file:
      # Ecrire le JSON dans le fichier
      json.dump(JSON_FILE, file, indent=1)

#def main():
#    get_code_with_scope()

#if __name__ == "__main__":
#    main()