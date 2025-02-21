from spotify import PlaybackState
from typing import Union

def format(state: Union[PlaybackState, None]) -> str:
    if state is None or state.is_playing == False:
        return "Ку"
    return f"🎶{', '.join(artist['name'] for artist in state.item.artists)} - {state.item.name}🎶 ||| Сейчас слушаю в Spotify"