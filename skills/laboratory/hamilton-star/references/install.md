# Installing PyLabRobot for a Hamilton STAR

Verified against pylabrobot 0.2.2. Based on the official guide:
https://docs.pylabrobot.org/stable/user_guide/getting-started/installation.html

## 1. Python package

Python 3.9 or newer. Use a virtual environment:

```bash
python -m venv env
source env/bin/activate          # Windows: .\env\Scripts\activate
pip install "pylabrobot[usb]==0.2.2"
```

The `usb` extra installs `pyusb` and `libusb-package`, which the STAR backend needs. Other extras:
`serial`, `ftdi`, `hid`, `opentrons`, `all`. Pin the version: a plain
`pip install --pre pylabrobot` gives the 1.0 beta, whose API differs (see SKILL.md).

Don't install from the GitHub `main` branch: it is already the 1.0 API.

Then run `python scripts/check_env.py`.

## 2. USB access per operating system

The robot connects over USB (Hamilton vendor ID `0x08AF`, STAR product ID `0x8000`).

### Linux
The official guide lists no extra steps. If you get permission errors as a normal user, add a udev rule, e.g.
`/etc/udev/rules.d/99-hamilton.rules`:

```
SUBSYSTEM=="usb", ATTR{idVendor}=="08af", MODE="0666"
```

then `sudo udevadm control --reload-rules` and replug the cable.

### macOS
```bash
brew install libusb
```
Known issue: some macOS 15 machines don't find the robot. There is no known fix; use Linux or
Windows if you hit it.

### Windows (Zadig and libusbK)
Windows binds the robot to Hamilton's own driver, which pyusb can't use. Replace it:

1. Close VENUS and any Hamilton services. Connect the robot by USB and turn it on.
2. Download Zadig from https://zadig.akeo.ie and run it.
3. Options > List All Devices.
4. Select **ML Star** (the STAR or STARlet).
5. Use the arrows to choose **libusbK**, then click Replace Driver, then Close.

### Switching back to VENUS (Windows)
While libusbK is installed, VENUS and pyhamilton can't see the robot. To switch back:

1. Device Manager > libusbK USB Devices > ML Star > Properties > Driver > Update Driver.
2. Browse my computer > Let me pick from a list.
3. Choose **Microlab STAR**, Next, Close.

Repeat the Zadig steps to go back to PyLabRobot. Labs that use both should write the switch into
their SOP.

## 3. Check it works

```bash
python scripts/check_env.py                    # finds libusb and the robot
python examples/01_basic_transfer.py           # simulation, no robot needed
```

On hardware, start with a script that only calls `await lh.setup()` and `await lh.stop()`.
`setup()` initializes the channels, 96 head, iSWAP and autoload, so clear the deck path first.
Skip parts with `await lh.setup(skip_iswap=True, skip_core96_head=True, skip_autoload=True)`.

## Problems

| Symptom | Fix |
|---|---|
| `usb.core.NoBackendError: No backend available` | libusb isn't found. macOS: `brew install libusb`. Windows: install libusbK with Zadig. Linux: install `libusb-1.0-0`. |
| Robot not found / `ValueError` finding the device | Cable, power, VENUS still running, or the Windows driver is still Hamilton's. |
| Access denied (Linux) | Add the udev rule above. |
| Several robots on one computer | Pass `STARBackend(serial_number="...")` or `device_address=...`. |
