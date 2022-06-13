Many Sony headphones aren't immediately recognized as a sound device by Bluez, and you need to
issue a second connect command, which is mildly inconvenient but more importantly not allowed by
many Bluetooth UIs. This script monitors the Connected status of all devices using DBus and
when any of them change to true it issues a second Connect command after a timeout of 1s.

## Parameters

`-v`: debug output

## Usage

Clone somewhere and add `main.sh` or `main.py` to your DE's login scripts. `main.py` runs the
program, `main.sh` looks for updates first. 

## ToDo

I'm not working on these

- [ ] Systemd service file
- [ ] Packages for various distros