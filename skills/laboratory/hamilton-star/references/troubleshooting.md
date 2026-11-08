# Errors and recovery on the Hamilton STAR (PyLabRobot 0.2.2)

## How errors arrive

| Exception | Where from | What to read |
|---|---|---|
| `ChannelizedError` (`pylabrobot.liquid_handling.errors`) | `pick_up_tips`, `drop_tips`, `aspirate`, `dispense` | `.errors`: `{channel_index: exception}` |
| `STARFirmwareError` (`...backends.hamilton.STAR_backend`) | Any firmware command | `.errors`: `{module_name: STARModuleError}`, `.raw_response` |
| `HasTipError`, `NoTipError`, `TooLittleLiquidError`, `TooLittleVolumeError` | Trackers (simulation and hardware) | The message names the tip spot or well |
| `ValueError` | PLR's own checks before sending | Usually a resource or list length mistake |

```python
from pylabrobot.liquid_handling.errors import ChannelizedError
from pylabrobot.liquid_handling.backends.hamilton.STAR_backend import STARFirmwareError

try:
    await lh.aspirate(wells, vols=[50] * 8, lld_mode=[STARBackend.LLDMode.GAMMA] * 8)
except ChannelizedError as e:
    for channel, err in e.errors.items():
        print(channel, type(err).__name__, err)
except STARFirmwareError as e:
    print(e.errors, e.raw_response)
```

## Common STAR module errors

All are in `pylabrobot.liquid_handling.backends.hamilton.STAR_backend`.

| Error | Usual cause | What to do |
|---|---|---|
| `TipAlreadyFittedError` | Channel already has a tip | `await lh.discard_tips()` or check `lh.backend.request_tip_presence()` |
| `HamiltonNoTipError` / `NoTipError` | Tip not picked up, or no tip at that spot | Check the tip rack in the deck matches reality; tip tracker state |
| `NoCarrierError`, `WrongCarrierError` | Carrier not on the rail in code, or autoload barcode mismatch | Fix the rail number in `assign_child_resource` |
| `TipTooLittleVolumeError` | "Too little liquid": LLD found no surface, or not enough to aspirate | Check volumes, `lld_mode`, sensitivity, labware definition |
| `ClotDetectedError` | Pressure jump during aspiration | Inspect sample; adjust speed/liquid class |
| `PositionNotReachableError` | Coordinate outside the arm's range | Labware/rail definition wrong, or offset too large |
| `CommandNotCompletedError`, `HardwareError` | Motor or hardware fault | Check the robot; re-run `setup()` |
| `CoverCloseError` | Front cover open | Close it |

## Recovery recipes

**Script crashed with tips on.** Start a new session and drop them in the trash:

```python
await lh.setup()  # initializing the channels ejects tips at the tip waste
print(await lh.backend.request_tip_presence())
```

If tips remain, `await lh.discard_tips()`. Tip tracker state is in memory only, so after a
crash the tracker no longer matches the rack. Start with a fresh rack, or mark which tips are
left with `tip_rack.set_tip_state({"A1": False, ...})` (`True` = tip present).

**USB is busy / device not found after a crash.** The previous Python process may still hold the
device. Kill it, power-cycle if needed, and always put `await lh.stop()` in a `finally`.

**Plate dropped or gripper error.** Stop. Remove the plate by hand, then
`await lh.backend.park_iswap()` (or re-run setup). Check `pickup_distance_from_top` and the plate
definition's height.

**Positions are a little off.** The labware definition or carrier is wrong more often than the
robot. Check the definition's dimensions against the real labware; use `offsets=[Coordinate(x, y, z)]` only as a
temporary fix.

## Debugging

- `print(lh.deck.summary())` to check the layout.
- Turn on logs to see every firmware command and reply. They are logged at a custom level 5,
  below `DEBUG`:

  ```python
  import logging
  from pylabrobot.io.validation_utils import LOG_LEVEL_IO  # = 5

  logging.basicConfig(level=LOG_LEVEL_IO)
  ```

- Ask on the forum with the firmware command and response: https://discuss.pylabrobot.org
