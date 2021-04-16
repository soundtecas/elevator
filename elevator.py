import yaml
import glob
import dropbox
import os
import sys
import time, threading
import RPi.GPIO as GPIO
import time
import pygame
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
            print(files.entries)
            fileToFetch = files.entries[-1]
            _, res = dbx.files_download(path='/' + fileToFetch.name)

            # Cache the fetched file
            _, extension = os.path.splitext(fileToFetch.name)
            cachedFilePath = path + '/' + 'music' + extension

            with open(cachedFilePath, 'wb') as f:
                f.write(res.content)
                print('Soundtrack cached', cachedFilePath)

def configureGPIPTrigger(gpio_pin, cb):
    GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(gpio_pin, GPIO.RISING, callback=cb, bouncetime=500)

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

# Configure GPIO
pin_up = config['pi_signal_gpio_up']
pin_down = config['pi_signal_gpio_down']
pin_check_interval = config['pi_signal_interval_ms']

# Configure pygame mixer
pygame.mixer.init()
pygame.mixer.music.set_volume(1.0)

fade_ms = 1000
max_music_play_seconds = int(config['soundtrack_play_seconds'])

def stop_music():
    print("Fading out music for", fade_ms, "ms")
    pygame.mixer.music.fadeout(fade_ms)
    pygame.mixer.music.unload()

def play_music(gpio_trigger):
    print("Play music for trigger", gpio_trigger)
    
    is_music_playing = pygame.mixer.music.get_busy()
    if is_music_playing:
        print("Music already playing")
        return

    pygame.mixer.music.load(soundtrackPath)
    pygame.mixer.music.rewind()

    print("Playing music for", max_music_play_seconds, "seconds")
    pygame.mixer.music.play(max_music_play_seconds, fade_ms=fade_ms)
    threading.Timer(max_music_play_seconds, stop_music).start()

GPIO.setmode(GPIO.BCM)
configureGPIPTrigger(pin_up, play_music)
configureGPIPTrigger(pin_down, play_music)
print('Listening to signal on GPIO pins', pin_up, pin_down)

running = True
while running:
    time.sleep(1)

print("quitting")
pygame.quit()
GPIO.cleanup()
sys.exit()