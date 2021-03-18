import yaml
import glob
import dropbox
import os
import sentry_sdk
from sentry_sdk import start_transaction

def loadConfig(file):
    with open(file, 'r') as stream:
        config_dict = yaml.safe_load(stream)
        return config_dict
        
def clearCache(path):
    files = glob.glob(path + '/*')
    for f in files:
        os.remove(f)

def fetchAndCacheSoundtrack(dropboxAccessToken, path):
    with start_transaction(op="task", name="fetchAndCacheSoundtrack"):
        with dropbox.Dropbox(dropboxAccessToken) as dbx:
            # List available fiels
            files = dbx.files_list_folder(path='', include_non_downloadable_files=False)
            if len(files.entries) <= 0:
                raise Exception('No files found')

            # Select the last file in the folder
            fileToFetch = files.entries[-1]
            _, res = dbx.files_download(path='/' + fileToFetch.name)

            # Cache the fetched file
            _, extension = os.path.splitext(fileToFetch.name)
            cachedFilePath = path + '/' + 'music' + extension

            with open(cachedFilePath, 'wb') as f:
                f.write(res.content)
                print('Soundtrack cached', cachedFilePath)

config = loadConfig('config.yaml')
print('Config loaded')

sentry_sdk.init(
    dsn=config['sentry'],
    environment=config['sentry_env'],

    ignore_errors=[KeyboardInterrupt],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

cachePath = config['cache_path']
clearCache(cachePath)
fetchAndCacheSoundtrack(config['dropbox_access_token'], cachePath)

cachedFiles = glob.glob(cachePath + '/*.mp3')
if len(cachedFiles) <= 0:
    raise Exception('Missing cached file. Exiting program.')

soundtrackPath = cachedFiles[0]
print('Ready using cached soundtrack', soundtrackPath)

try:
    import RPi.GPIO as GPIO
    import time
    import pygame

    # Configure GPIO
    # gpioPin = 16
    pin_up = config['pi_signal_gpio_up']
    pin_down = config['pi_signal_gpio_down']
    pin_check_interval = config['pi_signal_interval_ms']

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_up, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(pin_down, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print('Listening to signal on GPIO pins', pin_up, pin_down)

    # Configure pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(soundtrackPath)
    pygame.mixer.music.set_volume(1.0)
    max_music_play_seconds = int(config['soundtrack_play_seconds'])

    while pygame.mixer.music.get_busy() == True:
        pass

    print('Awaiting signal')
    while True:
        signal_up_received = GPIO.input(pin_up) == False
        signal_down_received = GPIO.input(pin_down) == False
        is_music_playing = pygame.mixer.music.get_busy()
        fade_ms = 1000

        if signal_up_received or signal_down_received: # Button pressed / signal received
            if is_music_playing == False:
                with start_transaction(op="task", name="music_play"):
                    print('Playing music')
                    pygame.mixer.music.rewind()
                    pygame.mixer.music.play(fade_ms=fade_ms)
            else:
                print('Music is already playing')

        if is_music_playing:
            music_play_time = (pygame.mixer.music.get_pos() / 1000) % 60
            if music_play_time >= max_music_play_seconds:
                with start_transaction(op="task", name="music_stop"):
                    print('Music play time threshold reached. Stopping.')
                    pygame.mixer.music.fadeout(fade_ms)
                    pygame.mixer.music.rewind()

        time.sleep(pin_check_interval)

except (ImportError, RuntimeError):
    print('Not running on raspberry')
    input('Press any key to trigger music:\n')

    from playsound import playsound
    playsound(soundtrackPath)
