# tg-spotify

## Description
tg-spotify is a project that updates your Telegram bio with your current Spotify playback state.

## Requirements
- Docker

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/Laefye/tg-spotify.git
    cd tg-spotify
    ```

2. Build and run the Docker container:
    ```sh
    docker build -t tg-spotify . 
    docker run -it --name tg-spotify tg-spotify
    ```
    Note: The `-it` flag is used to create the configuration file interactively. After the configuration is set up, you can run the container without `-it`:
    ```sh
    docker run -d --name tg-spotify tg-spotify
    ```

## Usage
To (re)generate the configuration file, you need to set up the config:
```sh
docker exec -it tg-spotify python3 main.py generate
```

## Note
Windows native (without Docker) is not supported.

## Customization
To change the bio template, modify the `formating.py` file. The `format` function is responsible for generating the bio text based on the current playback state.
