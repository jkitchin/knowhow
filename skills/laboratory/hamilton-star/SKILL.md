---
name: hamilton-star
description: Program Hamilton STAR and STARlet liquid handling robots from Python with PyLabRobot 0.2.x (open source, talks to the robot's firmware over USB, no VENUS needed). Covers installing (pip, USB/libusbK drivers, switching back to VENUS), building a deck with carriers, tip racks and plates, simulating protocols, 8-channel and 96-head pipetting, moving plates with the iSWAP or CoRe grippers, liquid-level detection, Hamilton liquid classes and firmware errors. Use whenever the user mentions a Hamilton STAR, STARlet, Microlab STAR, ML STAR, PyLabRobot, pylabrobot, STARBackend, or wants to automate pipetting, plate moves or serial dilutions on a Hamilton robot from Python, even if they don't name the library.
allowed-tools: ["*"]
---

# Hamilton STAR / STARlet with PyLabRobot

## Overview

[PyLabRobot](https://github.com/PyLabRobot/pylabrobot) (PLR) is an MIT-licensed Python SDK that
drives Hamilton STAR and STARlet robots by sending firmware commands over USB. It replaces
Hamilton's VENUS software for the session: you describe the deck in Python, then call
`aspirate`, `dispense`, `move_plate`, etc. The same code runs against a simulator first.

**This skill targets pylabrobot 0.2.2**, the current stable release (July 2026), and every
example in `examples/` was run against it. See "Version note" at the end before using 1.0.

**Safety first.** This code moves a real robot. Always:
1. run the protocol with the simulator (`STARChatterboxBackend`) and trackers on before hardware;
2. check the deck in Python matches the physical deck (carrier type, rail, site, labware);
3. keep the front cover closed and someone near the robot for the first hardware run;
4. call `await lh.stop()` in a `finally` so the USB connection is released.

PyLabRobot is not made or supported by Hamilton. Whether using a firmware driver affects your
service contract is between you and Hamilton.

## When to use something else

- **The lab must keep VENUS methods and liquid classes running as-is**: use
  [pyhamilton](https://github.com/dgretton/pyhamilton) (Windows only, drives VENUS).
- **Opentrons robots**: see the `opentrons` skill. PLR also supports the OT-2, Tecan EVO and
  Hamilton Vantage with the same `LiquidHandler` API but a different backend.

## Install

```bash
python -m venv env && source env/bin/activate      # Windows: .\env\Scripts\activate
pip install "pylabrobot[usb]==0.2.2"
python scripts/check_env.py                        # version, libusb, robot on USB
```

- **Linux**: nothing more.
- **macOS**: `brew install libusb`. (Known issue: some macOS 15 machines don't find the robot.)
- **Windows**: replace the "ML Star" USB driver with libusbK using Zadig, with VENUS closed.
  VENUS and pyhamilton then stop working until you switch the driver back.

Full steps, switching back to VENUS, and fixes for USB errors: `references/install.md`.

## The workflow

Every protocol has the same shape: build the deck, create a `LiquidHandler`, `setup()`, run
steps, `stop()`. All robot calls are `async`, so run them with `asyncio.run(...)` in a script or
top-level `await` in Jupyter.

```python
import asyncio
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.liquid_handling.backends import STARBackend
from pylabrobot.liquid_handling.backends.hamilton.STAR_chatterbox import STARChatterboxBackend
from pylabrobot.resources import (
    STARLetDeck,
    TIP_CAR_480_A00,
    PLT_CAR_L5AC_A00,
    hamilton_96_tiprack_300uL_filter,
    cor_96_wellplate_360uL_Fb,
    set_tip_tracking,
    set_volume_tracking,
)


def build_deck():
    deck = STARLetDeck()  # STARDeck() for a full-size STAR
    tip_car = TIP_CAR_480_A00(name="tip_carrier")
    tip_car[0] = hamilton_96_tiprack_300uL_filter(name="tips_01")  # site 0 = front-most
    deck.assign_child_resource(tip_car, rails=1)
    plt_car = PLT_CAR_L5AC_A00(name="plate_carrier")
    plt_car[0] = cor_96_wellplate_360uL_Fb(name="source")
    plt_car[1] = cor_96_wellplate_360uL_Fb(name="dest")
    deck.assign_child_resource(plt_car, rails=8)
    return deck


async def main(simulate=True):
    set_tip_tracking(True)  # error on picking up a tip that isn't there
    set_volume_tracking(True)  # error on aspirating more than a well holds
    backend = STARChatterboxBackend() if simulate else STARBackend()
    lh = LiquidHandler(backend=backend, deck=build_deck())
    await lh.setup()  # on hardware: initializes the robot, can take a minute
    try:
        tips = lh.deck.get_resource("tips_01")
        src, dst = lh.deck.get_resource("source"), lh.deck.get_resource("dest")
        for w in src["A1:H1"]:
            w.tracker.set_volume(200)  # what is really in the wells (uL)

        await lh.pick_up_tips(tips["A1:H1"])  # one tip per channel, 8 channels
        await lh.aspirate(src["A1:H1"], vols=[100] * 8)
        await lh.dispense(dst["A1:H1"], vols=[100] * 8)
        await lh.return_tips()  # or discard_tips() to the trash
    finally:
        await lh.stop()


asyncio.run(main())
```

### Key concepts

- **Deck, carriers, sites.** The deck has rails (STARlet 32, STAR 56 in 0.2.x). Carriers sit on a
  rail; labware sits in a carrier site, `carrier[i]`, with site 0 at the front. Names must be
  unique: you look things up with `lh.deck.get_resource("name")`.
- **Wells and tips by name.** `plate["A1"]`, `plate["A1:H1"]` (a column, list of 8),
  `plate["A1:A12"]` (a row). `plate.get_well("A1")` returns a single well.
  `plate.get_all_items()` returns all 96.
- **Lists everywhere.** `aspirate`/`dispense` take a list of containers and a list of volumes,
  one per channel used. `use_channels=[0, 2]` picks specific channels (channel 0 is the back-most).
- **Units.** Volumes in uL, flow rates in uL/s, distances in mm, `offsets=[Coordinate(x, y, z)]`
  shift a channel from its default position in the well.
- **Trackers.** With tracking on, mistakes raise in simulation (`HasTipError`,
  `TooLittleLiquidError`, ...) before they happen on the robot. Set real starting volumes with
  `well.tracker.set_volume(uL)`.
- **Inspect the deck.** `print(lh.deck.summary())` shows every carrier, site and position. Save
  and reload a layout with `deck.save("deck.json")` and `Deck.load_from_json_file("deck.json")`.
- **Visualizer.** `from pylabrobot.visualizer.visualizer import Visualizer`, then
  `vis = Visualizer(resource=lh); await vis.setup()` opens a browser view that animates the run.

## Core operations

| Task | Call |
|---|---|
| Tips on / off | `pick_up_tips(tip_spots)`, `drop_tips(tip_spots_or_trash)`, `return_tips()`, `discard_tips()` |
| Pipette | `aspirate(wells, vols)`, `dispense(wells, vols)` |
| One source to many | `transfer(source_well, target_wells, source_vol=...)` |
| Mix while pipetting | `mix=[Mix(volume=30, repetitions=3, flow_rate=100)]` (from `pylabrobot.liquid_handling.standard`) |
| 96 head | `pick_up_tips96(rack)`, `aspirate96(plate, volume)`, `dispense96(plate, volume)`, `return_tips96()`, `discard_tips96()` |
| Move labware | `move_plate(plate, carrier[site])` (iSWAP), add `use_arm="core"` for CoRe grippers; `move_lid`, `move_resource` |

`examples/` has runnable versions: `01_basic_transfer.py`, `02_96head_stamp.py`,
`03_move_plate_iswap.py`. Each runs in simulation by default and on hardware with `--hardware`.
Full signatures and parameters: `references/api.md`.

## STAR-specific options

Extra keyword arguments to `aspirate`/`dispense` are passed straight to the STAR backend. Most
take one value per channel:

```python
from pylabrobot.liquid_handling.backends import STARBackend

await lh.aspirate([well], vols=[50], lld_mode=[STARBackend.LLDMode.GAMMA])  # capacitive LLD
await lh.dispense([well], vols=[50], jet=[True], blow_out=[True])  # jet dispense
```

- **Liquid-level detection**: `lld_mode` = `OFF`, `GAMMA` (capacitive), `PRESSURE`, `DUAL`,
  `Z_TOUCH_OFF`.
- **Liquid classes**: by default PLR picks a Hamilton liquid class from the tip, jet/blow-out and
  liquid, and corrects the volume. Override per channel with `hamilton_liquid_classes=[...]` or
  turn correction off with `disable_volume_correction=[True]`.
- **Hardware queries**: `lh.backend.request_firmware_version()`,
  `request_machine_configuration()`, `probe_liquid_heights(...)`, `move_channel_x/y/z(...)`.

Details and more options: `references/api.md`.

## Errors

Firmware errors come back as Python exceptions. Multi-channel operations raise
`ChannelizedError`, whose `.errors` maps channel index to the error (e.g. `NoTipError`,
`TipTooLittleVolumeError`). Lower-level failures raise `STARFirmwareError` with `.errors` per
module (e.g. `TipAlreadyFittedError`, `NoCarrierError`, `PositionNotReachableError`). Recovery
recipes: `references/troubleshooting.md`.

## Common mistakes

- Forgetting `await`: the robot does nothing and Python only prints "coroutine was never awaited".
  Same for forgetting `await lh.setup()`.
- Running hardware code that was never simulated.
- Deck in code doesn't match the real deck: wrong rail, site or labware definition. Check with
  `deck.summary()` and by eye before the first run.
- VENUS (or a VENUS service) still running and holding the USB device.
- Passing one number where a list is expected: `vols=[100]`, not `vols=100`, for `aspirate`.
- Using names from other versions: in 0.2.2, labware functions are lowercase
  (`cor_96_wellplate_360uL_Fb`, not `Cor_96_wellplate_360ul_Fb`) and starting volumes use
  `tracker.set_volume`, not `set_liquids`.

## Version note: PyLabRobot 1.0

`pylabrobot 1.0.0b1` (pre-release, Sept 2026) changes the API: robots become devices
(`from pylabrobot.hamilton.star import STARlet`; `star = STARlet(simulation=True)`), hardware is
reached through `star.pipettes`, `star.head96`, `star.iswap`, `star.core_grippers`, and
`rails=` becomes `track=`. The 0.2 imports in this skill still work in 1.0 under
`pylabrobot.legacy` with deprecation warnings. Pin `pylabrobot[usb]==0.2.2` until this skill is
updated. `scripts/check_env.py` warns if 1.0 is installed.

## References

- `references/install.md`: install, USB drivers per OS, switching back to VENUS
- `references/api.md`: LiquidHandler and STAR backend reference, labware names
- `references/troubleshooting.md`: errors and recovery
- Docs: https://docs.pylabrobot.org, forum: https://discuss.pylabrobot.org
