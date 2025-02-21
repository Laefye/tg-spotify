from spotify import PlaybackState
from typing import Union

def format(state: Union[PlaybackState, None]) -> str:
    if state is None or state.is_playing == False:
        return "Я ничего не слушаю"
    return f"Сейчас слушаю {state.item.name} от {', '.join(artist['name'] for artist in state.item.artists)}\nМяу"