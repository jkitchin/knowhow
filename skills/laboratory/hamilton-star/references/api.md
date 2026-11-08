# PyLabRobot 0.2.2 API reference for the Hamilton STAR

Signatures below were read from pylabrobot 0.2.2. For anything not listed, read the source:
`pylabrobot/liquid_handling/liquid_handler.py` (general API) and
`pylabrobot/liquid_handling/backends/hamilton/STAR_backend.py` (STAR firmware, ~290 methods).

## Imports

```python
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.liquid_handling.backends import STARBackend  # real robot
from pylabrobot.liquid_handling.backends.hamilton.STAR_chatterbox import STARChatterboxBackend
from pylabrobot.liquid_handling.standard import GripDirection, Mix
from pylabrobot.resources import (
    Coordinate,
    Deck,
    STARDeck,
    STARLetDeck,
    set_tip_tracking,
    set_volume_tracking,
)
from pylabrobot.visualizer.visualizer import Visualizer
```

`STAR` is a deprecated alias of `STARBackend`; use `STARBackend`.

## Backends

```python
STARBackend(
    device_address=None,
    serial_number=None,
    packet_read_timeout=3,
    read_timeout=30,
    write_timeout=30,
    left_side_panel_installed=False,
)

STARChatterboxBackend(num_channels=8, machine_configuration=..., extended_configuration=...)
```

The chatterbox simulates a STAR with 8 channels, a 96 head and an iSWAP. It sends nothing to a
robot; combine it with the trackers to catch tip and volume mistakes.

`await lh.setup(skip_instrument_initialization=False, skip_pip=False, skip_autoload=False,
skip_iswap=False, skip_core96_head=False)` passes these to the STAR backend.

## Deck

```python
deck = STARLetDeck()  # 32 rails     STARDeck()  # 56 rails
# both: with_trash=True, with_trash96=True, with_teaching_rack=True,
#       core_grippers="1000uL-5mL-on-waste"   (or "1000uL-at-waste", None)

carrier = PLT_CAR_L5AC_A00(name="plates")  # 5 sites, site 0 at the front
carrier[0] = cor_96_wellplate_360uL_Fb(name="p1")
deck.assign_child_resource(carrier, rails=8)

print(deck.summary())  # table of rails, carriers, sites
deck.save("deck.json")
deck = Deck.load_from_json_file("deck.json")
```

### Common Hamilton labware in 0.2.2

| Kind | Names |
|---|---|
| Tip carriers | `TIP_CAR_480_A00` (5 racks), `TIP_CAR_480BC_A00`, `TIP_CAR_288_A00`, `TIP_CAR_384_A00` |
| Plate carriers | `PLT_CAR_L5AC_A00`, `PLT_CAR_L5MD_A00`, `PLT_CAR_L5PCR_A00`, `PLT_CAR_L5FLEX_AC_A00`, `PLT_CAR_P3AC_A00` |
| Multiflex | `MFX_CAR_L5_base`, `MFX_CAR_L4_SHAKER`, `MFX_CAR_P3_SHAKER` |
| Trough carriers | `Trough_CAR_4R200_A00`, `Trough_CAR_5R60_A00` with `hamilton_1_trough_200mL_Vb`, `hamilton_1_trough_60mL_Vb` |
| Tip racks | `hamilton_96_tiprack_{10,50,300,1000}uL[_filter]`, `hamilton_96_tiprack_300uL_filter_slim`, `hamilton_24_tiprack_5000uL` |
| Plates | `cor_96_wellplate_360uL_Fb` (+ `_lid`), `cor_96_wellplate_2mL_Vb`, `azenta_96_wellplate_200uL_Vb_4titudeframestar`, `eppendorf_96_wellplate_*`, `thermo_AB_*` |

List everything available: `[n for n in dir(pylabrobot.resources) if "plate" in n.lower()]`.
Custom labware: copy a definition from `pylabrobot/resources/<vendor>/` and change the dimensions.

## Pipetting (8 channels)

```python
pick_up_tips(tip_spots, use_channels=None, offsets=None)
drop_tips(tip_spots_or_trash, use_channels=None, offsets=None, allow_nonzero_volume=False)
return_tips(use_channels=None)                  # back to where they were picked up
discard_tips(use_channels=None)                 # into the trash

aspirate(resources, vols, use_channels=None, flow_rates=None, offsets=None,
         liquid_height=None, blow_out_air_volume=None, spread="wide", mix=None, **star_kwargs)
dispense(resources, vols, ...same...)

transfer(source, targets, source_vol=None, ratios=None, target_vols=None,
         aspiration_flow_rate=None, dispense_flow_rates=None)
```

- Lists are per channel: `aspirate([w1, w2], vols=[50, 80])`.
- `use_channels=[0, 1]`: channel 0 is the back-most.
- `liquid_height`: mm above the well bottom to aspirate/dispense from.
- `spread="wide"`: when several channels share one big container (trough), they spread out.
- `mix=[Mix(volume=30, repetitions=3, flow_rate=100)]`: one per channel.

## 96 head

```python
pick_up_tips96(tip_rack, offset=Coordinate(0, 0, 0))
aspirate96(plate_or_container, volume, offset=..., flow_rate=None, liquid_height=None,
           blow_out_air_volume=None, mix=None)
dispense96(plate_or_container, volume, ...same...)
return_tips96()
discard_tips96()
```

## Moving labware

```python
move_plate(
    plate,
    to,
    pickup_distance_from_top=9.87,
    pickup_direction=GripDirection.FRONT,
    drop_direction=GripDirection.FRONT,
    use_arm="iswap",
)  # or use_arm="core"
move_lid(lid, to)
move_resource(resource, to)
pick_up_resource(resource) / drop_resource(destination)  # two-step version
```

`to` can be a carrier site (`carrier[2]`), another resource or a `Coordinate`. With
`use_arm="core"`, PLR picks up the CoRe gripper tools with two channels; on the backend these are
`pick_up_core_gripper_tools(front_channel)` and `return_core_gripper_tools()`.

## STAR backend options for aspirate/dispense

Passed as extra keyword arguments to `lh.aspirate`/`lh.dispense`. Lists are per channel.

| Option | Meaning |
|---|---|
| `lld_mode=[STARBackend.LLDMode.GAMMA]` | Liquid-level detection: `OFF`, `GAMMA` (capacitive), `PRESSURE`, `DUAL`, `Z_TOUCH_OFF` |
| `gamma_lld_sensitivity=[1..4]`, `dp_lld_sensitivity=[1..4]` | LLD sensitivity (1 = high, 4 = low) |
| `immersion_depth=[mm]` | How far below the detected surface to go |
| `surface_following_distance=[mm]` | Follow the liquid down while aspirating |
| `pre_wetting_volume=[uL]` | Pre-wet the tip |
| `settling_time=[s]`, `swap_speed=[mm/s]` | Wait after aspirating, speed leaving the liquid |
| `transport_air_volume=[uL]` | Air gap while moving |
| `jet=[True]`, `blow_out=[True]` | (dispense) jet mode, blow-out; also chooses the liquid class |
| `hamilton_liquid_classes=[lc]` | Override the liquid class |
| `disable_volume_correction=[True]` | Use the volume as given, no liquid-class correction |
| `probe_liquid_height=True` | Measure the height with LLD first, then aspirate relative to it |

### Liquid classes

PLR chooses a Hamilton liquid class from the tip (volume, filter), jet/blow-out and liquid
(default water), and uses it to correct volumes and set speeds. To pick one explicitly:

```python
from pylabrobot.liquid_handling.liquid_classes.hamilton.star import (
    HighVolumeFilter_Water_DispenseJet_Empty,
)

await lh.aspirate(
    [well], vols=[50], hamilton_liquid_classes=[HighVolumeFilter_Water_DispenseJet_Empty]
)
```

There are ~250 classes in that module (`HighVolume...`, `StandardVolume...`, `LowVolume...`,
for water, ethanol, DMSO, glycerol, serum, etc.).

## Useful backend calls

Use through `lh.backend` on a real robot:

| Call | Returns / does |
|---|---|
| `request_firmware_version()` | Firmware string |
| `request_machine_configuration()`, `request_extended_configuration()` | What is fitted |
| `request_tip_presence()` | `[True, False, ...]` per channel |
| `probe_liquid_heights(containers, use_channels=None, lld_mode=None)` | Liquid heights (mm), needs tips |
| `move_channel_x(channel, x)`, `move_channel_y(channel, y)`, `move_channel_z(channel, z)` | Manual moves (absolute mm) |
| `move_all_channels_in_z_safety()` | Raise all channels |
| `spread_pip_channels()` | Spread channels apart |
| `park_iswap()` | Park the iSWAP |
| `iswap_open_gripper(open_position=None)`, `iswap_close_gripper(grip_strength=5, plate_width=86.0)` | Gripper control |
