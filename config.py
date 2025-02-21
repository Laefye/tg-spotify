from __future__ import annotations
from dataclasses import dataclass
from typing import Union
from spotify import SpotifyAppInfo, AccessToken, Spotify, DEFAULT_SCOPES, SpotifyAuthorizationError
from json import load, dump
import os

DEFAULT_CONFIG_LOCATION = 'config.json'

class Generator:
    def __init__(self):
        pass

    async def _generate_spotify(self) -> Union[tuple[SpotifyAppInfo, AccessToken], None]:
        print('Spotify App Info:')
        client_id = input('Client ID: ')
        client_secret = input('Client Secret: ')
        redirect_uri = input('Redirect URI: ')
        spotifyAppInfo = SpotifyAppInfo(client_id, client_secret, redirect_uri)
        spotify = Spotify(spotifyAppInfo)
        print('Spotify Auth URL:', spotify.oauth2.get_authorization_url(DEFAULT_SCOPES))
        callback = spotify.oauth2.parse_callback_uri(input('Callback URI: '))
        try:
            access_token = await spotify.oauth2.get_access_token(callback.code)
            print('Access Token:', access_token.access_token)
        except SpotifyAuthorizationError as e:
            print('Spotify Authorization Error:', e)
            return None
        return spotifyAppInfo, access_token
    
    def _generate_telegram(self) -> TelegramConfig:
        print('Telegram Config:')
        api_id = input('API ID: ')
        api_hash = input('API Hash: ')
        phone = input('Phone Number: ')
        database_encryption_key = input('Database Encryption Key: ')
        return TelegramConfig(api_id, api_hash, phone, database_encryption_key)

    async def generate(self) -> Union[Config, None]:
        spotifyAppInfo, access_token = await self._generate_spotify()
        if spotifyAppInfo is None or access_token is None:
            return None
        telegramConfig = self._generate_telegram()
        return Config(spotifyAppInfo, access_token, telegramConfig)
        

class Builder:
    def __init__(self, filename: str = DEFAULT_CONFIG_LOCATION):
        self.filename = filename

    def load(self) -> Config:
        with open(self.filename, 'r') as f:
            return Config.from_json(load(f))
        
    def save(self, config: Config):
        with open(self.filename, 'w') as f:
            dump(config.to_json(), f)

    async def create_new(self) -> Union[Config, None]:
        generator = Generator()
        config = await generator.generate()
        if config is not None:
            self.save(config)
        return config

    async def build(self) -> Union[Config, None]:
        if os.path.exists(self.filename):
            return self.load()
        else:
            return await self.create_new()

@dataclass
class TelegramConfig:
    api_id: str
    api_hash: str
    phone: str
    database_encryption_key: str

    def to_json(self) -> dict:
        return {
            'api_id': self.api_id,
            'api_hash': self.api_hash,
            'phone': self.phone,
            'database_encryption_key': self.database_encryption_key
        }
    
    @staticmethod
    def from_json(data: dict) -> TelegramConfig:
        return TelegramConfig(
            data['api_id'],
            data['api_hash'],
            data['phone'],
            data['database_encryption_key']
        )

@dataclass
class Config:
    spotifyAppInfo: SpotifyAppInfo
    spotifyCredentials: AccessToken
    telegramConfig: TelegramConfig

    def to_json(self) -> dict:
        return {
            'spotifyAppInfo': self.spotifyAppInfo.to_json(),
            'spotifyCredentials': self.spotifyCredentials.to_json(),
            'telegramConfig': self.telegramConfig.to_json(),
        }
    
    @staticmethod
    def from_json(data: dict) -> Config:
        return Config(
            SpotifyAppInfo.from_json(data['spotifyAppInfo']),
            AccessToken.from_json(data['spotifyCredentials']),
            TelegramConfig.from_json(data['telegramConfig']),
        )
