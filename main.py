import asyncio
import logging
from spotify import Spotify, SpotifyAppInfo, SCOPE_USER_READ_PLAYBACK_STATE, AccessToken, User
from config import Generator, Builder
from formating import format
from signal import signal, SIGINT

from telegram.client import Telegram
from os import getenv
from sys import argv

LIBRARY_PATH = getenv('TDLIB_LIBRARY_PATH', None)

async def main():
    config = await Builder().build()
    tg = Telegram(
        api_id=config.telegramConfig.api_id,
        api_hash=config.telegramConfig.api_hash,
        phone=config.telegramConfig.phone,
        database_encryption_key=config.telegramConfig.database_encryption_key,
        files_directory='/tmp/.tdlib_files/',
        library_path=LIBRARY_PATH
    )
    tg.login()
    spotify = Spotify(config.spotifyAppInfo)
    user = spotify.get_user(config.spotifyCredentials)
    previous_format = None
    active = True
    def handler(sig, frame):
        print('Please wait +-10 seconds')
        nonlocal active
        active = False
    signal(SIGINT, handler)
    while active:
        for i in range(10):
            state = await user.get_playback_state()
            if state != previous_format:
                result = tg.call_method('setBio', params={'bio': format(state)})
                result.wait()
            if not active:
                break
            await asyncio.sleep(10)
        await user.refresh_access_token()
    result = tg.call_method('setBio', params={'bio': format(None)})
    result.wait()
   

if __name__ == '__main__':
    if len(argv) > 1 and argv[1] == 'generate':
        asyncio.run(Generator().generate())
    else:
        asyncio.run(main())

