from configparser import ConfigParser
from yandex_music import Client
from modules.getToken import get_token
from PyQt6.QtWidgets import QMessageBox
import pygetwindow as pw

config = ConfigParser()

config.read('info/config.ini')

if len(config.get("main","ym")) <= 2:
    print("[Яндекс Музыка] Замечен первый запуск, для работы приложения войдите в аккаунт яндекса, в открывшемся окне.")
    config.set("main", "ym", get_token())
    print("[Яндекс Музыка] Успешный запуск")
    with open("info/config.ini", "w") as config_file:
        config.write(config_file)
    
    client = Client(config.get("main", "ym")).init()
else:
    print("[Яндекс Музыка] Успешный запуск")
    client = Client(config.get("main", "ym")).init()


class MYAPI:
    
    @staticmethod
    def force_update_token():
        config.set("main", "ym", get_token())
        print("[Яндекс Музыка] Успешный запуск")
        with open("info/config.ini", "w") as config_file:
            config.write(config_file)
            
        client = Client(config.get("main", "ym")).init()

    @staticmethod
    def get_current_track():
        window_title = get_window_title("Yandex.Music")

        if not window_title or window_title == "Yandex.Music":
            # не вижу смысла перекрывать другие активности 
            return None

        queue = client.queues_list()

        if not len(queue):
            raise 'not playing now'
        
        if not queue:
            return None
        
        queue = client.queue(queue[0].id)

        if not queue:
            return
        
        try:
            track = queue.get_current_track().fetch_track()

            return {
                "title" : track.title,
                "link" : f"https://music.yandex.ru/album/{track['albums'][0]['id']}/track/{track['id']}/",
                "image" : f"https://{track.cover_uri.replace('%%', '1000x1000')}",
                "id" : track.id,
                "artist" : ", ".join(track.artists_name())
            }
        except Exception as _:
            if queue.context.id == 'user:onyourwave':
                window_title = ' '.join(window_title.split('-')[:-1]).strip()

                response = JSONAPI.search_song(window_title)

                return {
                    "title": window_title,
                    "link": JSONAPI.get_song_link(response),
                    "image": JSONAPI.get_song_img(response),
                    "id": JSONAPI.get_song_id(response),
                    "artist": JSONAPI.get_song_artist(response)
                }


class JSONAPI:

    @staticmethod
    def get_song_title(response):
        return response['title']

    @staticmethod
    def get_song_artist(response):
        artists = response['artists']
        artist_names = [artist['name'] for artist in artists]
        return ', '.join(artist_names)
    
    @staticmethod
    def get_song_link(response):
        track_id = response['id']
        album_id = response['albums'][0]['id']
        return f"https://music.yandex.ru/album/{album_id}/track/{track_id}/"
        
    @staticmethod
    def get_song_id(response):
        return response['id']

    @staticmethod
    def get_song_img(response):
        cover_uri = response['cover_uri']
        return "https://" + cover_uri.replace("%%", "1000x1000")
    
    @staticmethod
    def search_song(track_name):
        search_result = client.search(track_name)

        if search_result.best:
            type_ = search_result.best.type
            best = search_result.best.result

            if type_ in ['track']:
                return best
            
        if len(search_result.tracks["results"]) > 1:
            return search_result.tracks["results"][1]
            
        return None


def get_window_title(process_name):
    windows = pw.getWindowsWithTitle(process_name)

    if windows:
        return windows[0].title

    return None