"""Check that this machine is ready to drive a Hamilton STAR with PyLabRobot 0.2.x.

Run:  python check_env.py
Checks the installed pylabrobot version, that pyusb can find a libusb backend,
and lists any Hamilton STAR/STARlet visible on USB. Read-only: sends nothing to the robot.
"""

import sys

SKILL_VERIFIED = "0.2.2"
HAMILTON_VENDOR_ID = 0x08AF
STAR_PRODUCT_ID = 0x8000

ok = True


def report(passed, msg):
    global ok
    ok = ok and passed
    print(("[ OK ] " if passed else "[FAIL] ") + msg)


def warn(msg):
    print("[WARN] " + msg)


print(f"Python {sys.version.split()[0]}")
if sys.version_info < (3, 9):
    report(False, "pylabrobot 0.2.x needs Python >= 3.9")

try:
    import pylabrobot

    v = pylabrobot.__version__
    if v.startswith("0.2."):
        report(True, f"pylabrobot {v} (skill verified against {SKILL_VERIFIED})")
    elif v.startswith("1."):
        warn(
            f"pylabrobot {v} is the 1.0 API. The examples in this skill target 0.2.x;"
            " old imports still work but raise deprecation warnings."
            " Pin with: pip install 'pylabrobot[usb]==0.2.2'"
        )
    else:
        warn(f"pylabrobot {v} is older than this skill expects; upgrade to 0.2.2")
except ImportError:
    report(False, "pylabrobot not installed: pip install 'pylabrobot[usb]==0.2.2'")

try:
    import usb.core

    try:
        devices = list(usb.core.find(find_all=True, idVendor=HAMILTON_VENDOR_ID))
        report(True, "pyusb found a libusb backend")
        stars = [d for d in devices if d.idProduct == STAR_PRODUCT_ID]
        if stars:
            for d in stars:
                report(True, f"Hamilton STAR/STARlet on USB (bus {d.bus}, address {d.address})")
        else:
            warn(
                "no Hamilton STAR on USB. Fine for simulation. On real hardware check the cable,"
                " that the robot is on, and (Windows) that the libusbK driver is installed"
                " with Zadig."
            )
    except usb.core.NoBackendError:
        report(
            False,
            "pyusb has no libusb backend (NoBackendError). macOS: brew install libusb;"
            " Windows: install the libusbK driver with Zadig; Linux: install libusb-1.0",
        )
except ImportError:
    report(False, "pyusb missing: pip install 'pylabrobot[usb]'")

sys.exit(0 if ok else 1)
