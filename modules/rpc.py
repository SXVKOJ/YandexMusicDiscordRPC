import time
import traceback

from configparser import ConfigParser
from pypresence import Presence
from modules.yandexmusic import MYAPI

config = ConfigParser()

config.read('info/config.ini')

dRPC = Presence(client_id=config.get('main', 'ds'))
dRPC.connect()

switch = 0
lasttrack = 0


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
            details=str(song),
            state=str(artist),
            large_image=str(image_link),
            small_image="https://github.com/maj0roff/YandexMusicDiscordRPC/blob/main/logo.png?raw=true",
            large_text=f"{artist if not artist is None else ''} - {song}",
            buttons=btns
        )

    @staticmethod
    def force_update():
        global switch

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
        except Exception:
            traceback.print_exc()

            time.sleep(1)

    @staticmethod
    def call_presence():
        global switch
        global lasttrack

        while True:
            try:
                song = MYAPI.get_current_track()

                if not song:
                    dRPC.clear()

                    MRPC.force_update()

                    continue
                
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
            except Exception:
                traceback.print_exc()

                MRPC.idling()

            time.sleep(1)