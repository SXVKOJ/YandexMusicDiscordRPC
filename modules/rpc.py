from configparser import ConfigParser
from pypresence import Presence
from modules.yandexmusic import MYAPI
import time

config = ConfigParser()

config.read('info/config.ini')

dRPC = Presence(client_id=config.get('main', 'ds'))
dRPC.connect()


class MRPC:
    @staticmethod
    def clear():
        dRPC.clear()

    @staticmethod
    def idling():
        dRPC.update(
            details="Ничего не слушает",
            large_image="https://github.com/maj0roff/YandexMusicDiscordRPC/raw/main/fallback-black_2.gif",
            small_image="https://github.com/maj0roff/YandexMusicDiscordRPC/blob/main/logo.png?raw=true",
            large_text=f"Ничего не прослушивается."
        )

    @staticmethod
    def updatePresence(artist = None, 
                    song = None, 
                    image_link = None,
                    song_link = None):
        btns = [
            {
                "label": "Слушать",
                "url": song_link
            },
        ] if not song_link is None else None

        dRPC.update(
            details=song,
            state=artist,
            large_image=image_link,
            small_image="https://github.com/maj0roff/YandexMusicDiscordRPC/blob/main/logo.png?raw=true",
            large_text=f"{artist if not artist is None else ''} - {song}",
            buttons=btns
        )

    @staticmethod
    def force_update():
        switch = 0

        try:
            song = MYAPI.get_current_track()

            if not song:
                return
            
            if song['id'] != lasttrack:
                lasttrack = song['id']
                switch = 1
            if switch:
                switch = 0
                #print(f"[Яндекс Музыка] Слушаем {artist} - {song}")
                MRPC.updatePresence(
                    song['artist'],
                    song['title'],
                    song['image'],
                    song['link']
                )
        except Exception as e:
            print(e)

    @staticmethod
    def call_presence():
        while True:
            switch = 0
            lasttrack = 0

            try:
                song = MYAPI.get_current_track()

                if not song:
                    return
                
                if song['id'] != lasttrack:
                    lasttrack = song['id']
                    switch = 1
                if switch:
                    switch = 0

                    MRPC.updatePresence(
                        song['artist'],
                        song['title'],
                        song['image'],
                        song['link']
                    )
            except Exception as e:
                print(e)
                MRPC.idling()

            time.sleep(1)