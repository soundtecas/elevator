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
