# Soundtec Elevator

On a specific GPIO input signal, it plays a cached sound file for a set amount of seconds.

The cached sound file is downloaded from a shared Dropbox folder.
Configure access to your Dropbox account in `config.yaml`.

The program currently only supports `.mp3` sound files.

This program is intended for [Raspberry Pi](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/)
and [Beocreate 4](https://www.hifiberry.com/shop/boards/beocreate-4-channel-amplifier/).

---

## Configuration
* Create a `config.yaml` file (use `config.sample.yaml` as a template).
* Set your desired values in `config.yaml`.
* Run `pip install -r requirements.txt`
* Create cache directory: `mkdir cache`

## Development
**Requirements:**
* `python3`
* `pip3`
* `virtualenv`
* [Dropbox API app](https://www.dropbox.com/developers/apps) and API key.

**Create viritual enviornment:**
```sh
$ virtualenv <env_name> -p python3
```

**Active viritial enviornment:**
```sh
$ source <env_name>/bin/activate
```

To deactivate:
```sh
$ deactivate
```

## Running
With `python3` installed, run `python3 elevator.py` in your shell.

## Raspberry setup
* Ensure directory exists `/home/pi/bin`.
* Clone repo into the `bin` folder.
* `cd` into `/home/pi/bin/elevator`
* Follow **Configuration** steps above.

* The GPIO button should connect to `GPIO pin 16` and `GND`

To set volume on Raspberry PI: `alsamixer`
To store the set volume: `sudo alsactl store`

### Beocreate4
* [Follow guide](https://www.hifiberry.com/beocreate/beocreate-doc/beocreate-installing-the-sigmatcpserver/)

```
import os
os.system('mpg321 ~/elevator/cache/music.mp3')
``

https://stackoverflow.com/questions/62585077/how-do-i-get-amixer-pcm-numid-3-to-work-on-raspberry-pi-4

dsptoolkit install-profile https://raw.githubusercontent.com/hifiberry/hifiberry-dsp/master/sample_files/xml/4way-default.xml

Edit volume (Se issue: https://github.com/hifiberry/hifiberry-dsp/issues/22)
```
crontab -e

systemctl enable cron.service
systemctl restart cron.service
```


For Raspberry PI
```
sudo apt-get update && sudo apt-get install -y git vim python-pip python3-pip python3-rpi.gpio libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0
python3 -m pip install -U pygame --user
```



[Unit]
Description=Elevator
After=multi-user.target

[Service]
User=pi
Type=idle
ExecStart=/usr/bin/python3 /home/pi/elevator/elevator.py > /home/pi/elevator/logs.log 2>&1

[Install]
WantedBy=multi-user.target