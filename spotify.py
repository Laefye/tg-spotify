from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urlencode, parse_qs, urlparse
from aiohttp import ClientSession, ClientResponse
from logging import getLogger
from base64 import standard_b64encode
from json import loads
from typing import Union


@dataclass
class SpotifyAppInfo:
    client_id: str
    client_secret: str
    redirect_uri: str

    def to_json(self) -> dict:
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri
        }
    
    @staticmethod
    def from_json(data: dict) -> SpotifyAppInfo:
        return SpotifyAppInfo(
            client_id=data['client_id'],
            client_secret=data['client_secret'],
            redirect_uri=data['redirect_uri']
        )

SCOPE_USER_READ_PLAYBACK_STATE = 'user-read-playback-state'
DEFAULT_SCOPES = [SCOPE_USER_READ_PLAYBACK_STATE]

@dataclass
class Callback:
    code: str

@dataclass
class AccessToken:
    access_token: str
    refresh_token: str
    token_type: str
    scope: str
    expires_in: int

    def to_json(self) -> dict:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "scope": self.scope,
            "expires_in": self.expires_in
        }
    
    @staticmethod
    def from_json(data: dict) -> AccessToken:
        return AccessToken(
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
            token_type=data['token_type'],
            scope=data['scope'],
            expires_in=data['expires_in']
        )

@dataclass
class Item:
    name: str
    artists: list[dict]
    duration_ms: int

@dataclass
class PlaybackState:
    is_playing: bool
    progress_ms: int
    item: Item

class SpotifyError(Exception):
    error: str

    def __init__(self, error: str, error_description: str):
        super().__init__(error_description)
        self.error = error

class SpotifyAuthorizationError(SpotifyError):
    pass

class OAuth2:
    def __init__(self, spotify: Spotify):
        self.spotify = spotify

    def get_authorization_url(self, scopes: list[str]) -> str:
        query = {
            "client_id": self.spotify.app_info.client_id,
            "response_type": "code",
            "redirect_uri": self.spotify.app_info.redirect_uri,
            "scope": " ".join(scopes)
        }
        return f"https://accounts.spotify.com/authorize?{urlencode(query)}"
    
    def parse_callback_uri(self, uri: str) -> Callback:
        query = parse_qs(urlparse(uri).query)
        return Callback(code=query['code'][0])
    
    def _get_client_credentials(self) -> str:
        return standard_b64encode(f"{self.spotify.app_info.client_id}:{self.spotify.app_info.client_secret}".encode()).decode()

    async def _make_token_post(self, query: dict[str, str]) -> ClientResponse:
        async with ClientSession() as session:
            headers = {
                "Authorization": f"Basic {self._get_client_credentials()}"
            }
            response = await session.post("https://accounts.spotify.com/api/token", data=query, headers=headers)
            if response.status != 200:
                data = await response.json()
                if 'error' in data:
                    raise SpotifyAuthorizationError(data['error'], data['error_description'])
            return response

    async def get_access_token(self, code: str) -> AccessToken:
        query = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.spotify.app_info.redirect_uri,
        }
        response = await self._make_token_post(query)
        data = await response.json()
        return AccessToken.from_json(data)
        
    async def refresh_access_token(self, access_token: AccessToken) -> AccessToken:
        query = {
            "grant_type": "refresh_token",
            "refresh_token": access_token.refresh_token,
        }
        response = await self._make_token_post(query)
        data = await response.json()
        access_token.access_token = data['access_token']
        access_token.token_type = data['token_type']
        access_token.scope = data['scope']
        access_token.expires_in = data['expires_in']
        return access_token

class User:
    def __init__(self, spotify: Spotify, access_token: AccessToken):
        self.spotify = spotify
        self.access_token = access_token

    def _get_default_header(self) -> dict[str, str]:
        return {
            "Authorization": f"{self.access_token.token_type} {self.access_token.access_token}"
        }
    
    async def _raw_get_playback_state(self) -> Union[dict, None]:
        async with ClientSession() as session:
            headers = self._get_default_header()
            response = await session.get("https://api.spotify.com/v1/me/player", headers=headers)
            text = await response.text()
            if len(text) == 0:
                return None
            return loads(text)
        
    async def get_playback_state(self) -> Union[PlaybackState, None]:
        data = await self._raw_get_playback_state()
        if data is None:
            return None
        return PlaybackState(
            is_playing=data['is_playing'],
            progress_ms=data['progress_ms'],
            item=Item(
                name=data['item']['name'],
                artists=data['item']['artists'],
                duration_ms=data['item']['duration_ms']
            )
        )

    async def refresh_access_token(self):
        self.access_token = await self.spotify.oauth2.refresh_access_token(self.access_token)
    

class Spotify:
    def __init__(self, app_info: SpotifyAppInfo):
        self.app_info = app_info
        self.oauth2 = OAuth2(self)

    def get_user(self, access_token: AccessToken) -> User:
        return User(self, access_token)


