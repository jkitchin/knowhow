---
name: opentrons-heater-shaker
description: Opentrons Heater-Shaker Module - temperature control (37-95°C) with orbital mixing (200-3000 rpm) for cell culture, enzymatic reactions, and sample preparation requiring simultaneous heating and agitation
allowed-tools: ["*"]
---

# Opentrons Heater-Shaker Module

## Overview

The **Heater-Shaker Module** combines precise temperature control (37-95°C) with orbital shaking (200-3000 rpm) for automated protocols requiring simultaneous heating and mixing. Ideal for cell culture incubation, enzymatic reactions, bacterial transformations, and any workflow needing temperature-controlled agitation.

**Core value:** Automate temperature-sensitive mixing protocols with reproducible timing and conditions. Replace manual incubator transfers with on-deck temperature control.

## When to Use

Use the Heater-Shaker skill when:
- Performing enzymatic reactions requiring temperature control and mixing
- Incubating cell cultures or bacterial transformations
- Conducting ELISA washing steps with temperature control
- Running temperature-sensitive binding or hybridization reactions
- Protocols requiring precise timing of heating + mixing cycles
- Resuspending beads or particles with controlled agitation

**Don't use when:**
- Only temperature control needed (use Temperature Module instead)
- Only mixing needed (consider manual shaking or alternative approaches)
- Temperature outside 37-95°C range (or <1.5°C above ambient)

## Quick Reference

| Operation | Method | Key Parameters |
|-----------|--------|----------------|
| Load module | `protocol.load_module()` | `"heaterShakerModuleV1"`, location |
| Set temperature (blocking) | `set_and_wait_for_temperature()` | celsius (37-95) |
| Set temperature (non-blocking) | `set_target_temperature()` | celsius |
| Wait for temperature | `wait_for_temperature()` | - |
| Start shaking (blocking) | `set_and_wait_for_shake_speed()` | rpm (200-3000) |
| Stop shaking | `deactivate_shaker()` | - |
| Stop heating | `deactivate_heater()` | - |
| Open latch | `open_labware_latch()` | - |
| Close latch | `close_labware_latch()` | - |
| Check status | `.current_temperature`, `.current_speed` | - |

## Platform Compatibility

### Opentrons Flex
- **Allowed slots:** Column 1 or Column 3 (A1, B1, C1, D1, A3, B3, C3, D3)
- **No adjacent restrictions** - Full deck flexibility

### OT-2
- **Allowed slots:** 1, 3, 4, 6, 7, or 10
- **Adjacent slot restrictions:**
  - Keep adjacent slots clear or use only low-profile labware (<53mm height)
  - 8-channel pipettes cannot pipette in adjacent slots (tip racks OK if front/back)

## Loading the Module

### Basic Loading

```python
from opentrons import protocol_api

metadata = {'apiLevel': '2.19'}

def run(protocol: protocol_api.ProtocolContext):
    # Load Heater-Shaker in deck slot
    hs_mod = protocol.load_module("heaterShakerModuleV1", location="D1")  # Flex
    # hs_mod = protocol.load_module("heaterShakerModuleV1", location="1")  # OT-2
```

### Loading Labware with Adapters

**Two-step approach (recommended):**

```python
# Load adapter first, then labware
hs_adapter = hs_mod.load_adapter("opentrons_96_flat_bottom_adapter")
hs_plate = hs_adapter.load_labware("nest_96_wellplate_200ul_flat")
```

**Available adapters:**
- `opentrons_96_flat_bottom_adapter` - Universal flat-bottom plates
- `opentrons_96_pcr_adapter` - PCR plates and strips
- `opentrons_96_deep_well_adapter` - Deep-well plates
- `opentrons_universal_flat_adapter` - Custom flat-bottom labware

**Pre-configured combinations (legacy):**

```python
# Load labware directly (adapter implicit)
hs_plate = hs_mod.load_labware("nest_96_wellplate_200ul_flat")
```

## Latch Control

**The labware latch MUST be closed for shaking operations.**

```python
# Close latch before shaking
hs_mod.close_labware_latch()

# Open latch for pipetting or gripper access
hs_mod.open_labware_latch()
```

**Important:**
- Pipetting is possible with latch open or closed
- Shaking requires latch closed (method will error if open)
- Gripper access requires latch open
- **Always open latch before gripper operations**

## Temperature Control

### Blocking Temperature Control

Protocol waits until temperature is reached before continuing:

```python
# Set temperature and wait
hs_mod.set_and_wait_for_temperature(celsius=37)

# Perform operations at target temperature
protocol.delay(minutes=10)

# Turn off heater
hs_mod.deactivate_heater()
```

**Temperature range:**
- **Minimum:** The greater of 37°C or ambient temperature + 1.5°C (the Heater-Shaker cannot actively cool)
- **Maximum:** 95°C
- **Resolution:** 1°C

### Non-Blocking Temperature Control

Set target temperature and continue with other operations while heating:

```python
# Start heating (non-blocking)
hs_mod.set_target_temperature(celsius=75)

# Perform pipetting while heating
pipette.transfer(100, source, hs_plate.columns()[0])

# Wait for temperature before critical step
hs_mod.wait_for_temperature()

# Now at target temperature
protocol.delay(minutes=5)
```

**Use case:** Parallel pipetting during heating to save time.

### Checking Temperature Status

```python
# Get current temperature
current_temp = hs_mod.current_temperature

# Log temperature
protocol.comment(f"Heater-Shaker at {current_temp}°C")
```

## Shaking Control

### Basic Shaking

```python
# Close latch first (required)
hs_mod.close_labware_latch()

# Start shaking and wait to reach speed
hs_mod.set_and_wait_for_shake_speed(rpm=500)

# Shake for specific duration
protocol.delay(minutes=5)

# Stop shaking
hs_mod.deactivate_shaker()

# Open latch for pipetting access
hs_mod.open_labware_latch()
```

**Speed range:**
- **Minimum:** 200 rpm
- **Maximum:** 3000 rpm

### Checking Shake Speed

```python
# Get current speed
current_speed = hs_mod.current_speed

if current_speed > 0:
    protocol.comment(f"Shaking at {current_speed} rpm")
```

### Shake Speed Guidelines

**Recommended speeds by application:**
- **Gentle mixing:** 200-500 rpm
- **Cell culture:** 300-600 rpm
- **Enzymatic reactions:** 400-800 rpm
- **Vigorous mixing:** 800-1500 rpm
- **Aggressive agitation:** 1500-3000 rpm

**Note:** Higher speeds increase risk of splashing and cross-contamination.

## Combined Heating and Shaking

### Sequential Approach

```python
# Set temperature first
hs_mod.set_and_wait_for_temperature(celsius=37)

# Then start shaking
hs_mod.close_labware_latch()
hs_mod.set_and_wait_for_shake_speed(rpm=400)

# Incubate with heating and shaking
protocol.delay(minutes=30)

# Stop shaking, then heating
hs_mod.deactivate_shaker()
hs_mod.open_labware_latch()
hs_mod.deactivate_heater()
```

### Parallel Approach (Time-Optimized)

```python
# Start heating (non-blocking)
hs_mod.set_target_temperature(celsius=42)

# Prepare samples while heating
pipette.transfer(100, samples, hs_plate.wells())

# Wait for temperature
hs_mod.wait_for_temperature()

# Start shaking
hs_mod.close_labware_latch()
hs_mod.set_and_wait_for_shake_speed(rpm=600)

# Incubate
protocol.delay(minutes=20)

# Cleanup
hs_mod.deactivate_shaker()
hs_mod.open_labware_latch()
hs_mod.deactivate_heater()
```

## Common Patterns

### Bacterial Transformation

**Note:** The Heater-Shaker cannot cool below 37C. Use a Temperature Module for ice incubation and heat shock steps, then transfer to the Heater-Shaker for the 37C recovery with shaking.

```python
# Ice incubation and heat shock on Temperature Module
temp_mod.set_temperature(celsius=4)
protocol.delay(minutes=20)  # Ice incubation
temp_mod.set_temperature(celsius=42)
protocol.delay(seconds=45)  # Heat shock

# Transfer plate to Heater-Shaker for recovery
temp_mod.deactivate()
protocol.move_labware(plate, hs_mod, use_gripper=True)

# Recovery at 37C with shaking
hs_mod.set_and_wait_for_temperature(celsius=37)
hs_mod.close_labware_latch()
hs_mod.set_and_wait_for_shake_speed(rpm=300)
protocol.delay(minutes=60)

hs_mod.deactivate_shaker()
hs_mod.deactivate_heater()
hs_mod.open_labware_latch()
```

### Enzymatic Reaction

```python
# Pre-warm to reaction temperature
hs_mod.set_and_wait_for_temperature(celsius=37)

# Add enzyme while at temperature
hs_mod.open_labware_latch()
pipette.transfer(10, enzyme, hs_plate.wells(), mix_after=(3, 50))

# Incubate with gentle mixing
hs_mod.close_labware_latch()
hs_mod.set_and_wait_for_shake_speed(rpm=300)
protocol.delay(minutes=30)

# Stop reaction - transfer to Temperature Module for cooling
hs_mod.deactivate_shaker()
hs_mod.deactivate_heater()
hs_mod.open_labware_latch()

# Use Temperature Module for cooling below 37C
# protocol.move_labware(hs_plate, temp_mod, use_gripper=True)
# temp_mod.set_temperature(celsius=4)
```

### ELISA Wash with Incubation

```python
# Incubate with antibody
hs_mod.set_and_wait_for_temperature(celsius=37)
hs_mod.close_labware_latch()
hs_mod.set_and_wait_for_shake_speed(rpm=400)
protocol.delay(minutes=60)

# Stop for washing
hs_mod.deactivate_shaker()
hs_mod.open_labware_latch()

# Wash steps
for _ in range(3):
    # Remove liquid
    pipette.transfer(200, hs_plate.wells(), waste, new_tip="always")
    # Add wash buffer
    pipette.transfer(200, wash_buffer, hs_plate.wells())
    # Mix
    hs_mod.close_labware_latch()
    hs_mod.set_and_wait_for_shake_speed(rpm=500)
    protocol.delay(seconds=30)
    hs_mod.deactivate_shaker()
    hs_mod.open_labware_latch()

hs_mod.deactivate_heater()
```

### Bead Resuspension

```python
# Resuspend magnetic beads
hs_mod.close_labware_latch()
hs_mod.set_and_wait_for_shake_speed(rpm=1200)
protocol.delay(minutes=2)
hs_mod.deactivate_shaker()
hs_mod.open_labware_latch()

# Transfer to magnetic module for separation
protocol.move_labware(hs_plate, mag_block, use_gripper=True)
```

## Advanced Techniques

### Temperature Ramping

```python
# Gradual temperature increase
for temp in [25, 35, 45, 55, 65]:
    hs_mod.set_and_wait_for_temperature(temp)
    protocol.delay(minutes=5)

hs_mod.deactivate_heater()
```

### Precise Timing with Manual Tracking

For holds requiring exact elapsed time:

```python
import time

# Set conditions
hs_mod.set_and_wait_for_temperature(celsius=37)
hs_mod.close_labware_latch()
hs_mod.set_and_wait_for_shake_speed(rpm=500)

# Track elapsed time
start_time = time.monotonic()

# Perform operations
# ... your protocol steps ...

# Calculate remaining time
elapsed = time.monotonic() - start_time
remaining = max(0, (10 * 60) - elapsed)  # 10 minutes total

# Complete the hold
protocol.delay(seconds=remaining)

hs_mod.deactivate_shaker()
hs_mod.deactivate_heater()
hs_mod.open_labware_latch()
```

### Integration with Gripper (Flex)

```python
# Heat/shake on Heater-Shaker
hs_mod.set_and_wait_for_temperature(celsius=37)
hs_mod.close_labware_latch()
hs_mod.set_and_wait_for_shake_speed(rpm=400)
protocol.delay(minutes=30)
hs_mod.deactivate_shaker()
hs_mod.deactivate_heater()

# Open latch BEFORE gripper operation
hs_mod.open_labware_latch()

# Move plate to next module
protocol.move_labware(hs_plate, magnetic_block, use_gripper=True)
```

## OT-2 Specific Considerations

### Deck Layout Restrictions

**Height restrictions:**
- Adjacent slots must be empty OR contain labware <53mm tall
- Tall labware (>53mm) in adjacent slots interferes with module

**8-channel pipette restrictions:**
- Cannot pipette in slots adjacent to Heater-Shaker
- Exception: Tip racks allowed if oriented front-to-back (not left-to-right)

**Example valid OT-2 layout:**
```python
# Heater-Shaker in slot 4
hs_mod = protocol.load_module("heaterShakerModuleV1", "4")

# Adjacent slots 1, 5, 7 - keep empty or use tip racks
tips_1 = protocol.load_labware("opentrons_96_tiprack_300ul", "1")  # OK
tips_5 = protocol.load_labware("opentrons_96_tiprack_300ul", "5")  # OK

# Use non-adjacent slots for plates
plate_2 = protocol.load_labware("corning_96_wellplate_360ul_flat", "2")
plate_3 = protocol.load_labware("corning_96_wellplate_360ul_flat", "3")
```

## Best Practices

1. **Always open latch before gripper operations** - Prevents gripper errors
2. **Deactivate shaker before heater** - Safer shutdown sequence
3. **Use non-blocking temperature for parallel operations** - Saves protocol time
4. **Close latch before shaking** - Required for operation
5. **Allow temperature stabilization** - Add brief delay after reaching target
6. **Monitor shake speed selection** - Higher speeds risk splashing/contamination
7. **Consider ambient temperature** - Affects minimum achievable temperature
8. **Plan deck layout (OT-2)** - Account for adjacent slot restrictions
9. **Add protocol comments** - Document temperature/shake conditions for reproducibility
10. **Deactivate at protocol end** - Prevents equipment running indefinitely

## Common Mistakes

**❌ Shaking with open latch:**
```python
hs_mod.open_labware_latch()
hs_mod.set_and_wait_for_shake_speed(500)  # Error: latch must be closed
```

**✅ Correct:**
```python
hs_mod.close_labware_latch()
hs_mod.set_and_wait_for_shake_speed(500)
```

**❌ Gripper movement without opening latch:**
```python
protocol.move_labware(hs_plate, "C1", use_gripper=True)  # Error: latch closed
```

**✅ Correct:**
```python
hs_mod.open_labware_latch()
protocol.move_labware(hs_plate, "C1", use_gripper=True)
```

**❌ Not deactivating modules:**
```python
hs_mod.set_and_wait_for_temperature(37)
# Protocol ends - heater stays on!
```

**✅ Correct:**
```python
hs_mod.set_and_wait_for_temperature(37)
# ... operations ...
hs_mod.deactivate_heater()
```

**❌ Temperature out of range:**
```python
hs_mod.set_and_wait_for_temperature(celsius=25)  # May error if ambient is >23.5°C
```

**✅ Correct:**
```python
# Use Temperature Module for temperatures <37°C
temp_mod.set_temperature(celsius=25)
```

## Troubleshooting

**Module won't heat below 37°C:**
- Check ambient temperature - minimum is 1.5°C above ambient
- Consider using Temperature Module for lower temperatures

**Shaking command errors:**
- Verify latch is closed
- Check shake speed is within 200-3000 rpm range

**Pipette collisions (OT-2):**
- Check adjacent slots for tall labware
- Move tall labware to non-adjacent slots
- Use only tip racks in adjacent slots for 8-channel pipetting

**Temperature not stable:**
- Allow additional time for equilibration
- Verify module is not in high-airflow environment
- Check labware is properly seated on adapter

**Gripper cannot access:**
- Ensure latch is open
- Verify module is in allowed deck slot (columns 1 or 3 for Flex)

## Integration with Other Modules

### With Magnetic Block (Flex)

```python
# Incubate with beads on Heater-Shaker
hs_mod.set_and_wait_for_temperature(37)
hs_mod.close_labware_latch()
hs_mod.set_and_wait_for_shake_speed(400)
protocol.delay(minutes=10)
hs_mod.deactivate_shaker()
hs_mod.deactivate_heater()
hs_mod.open_labware_latch()

# Move to Magnetic Block for separation
protocol.move_labware(hs_plate, mag_block, use_gripper=True)
protocol.delay(minutes=3)  # Bead separation

# Pipette supernatant
pipette.transfer(150, hs_plate.wells(), waste.wells())

# Return to Heater-Shaker for resuspension
protocol.move_labware(hs_plate, hs_mod, use_gripper=True)
```

### With Temperature Module

```python
# Cool samples on Temperature Module
temp_mod.set_temperature(4)
protocol.move_labware(cold_plate, temp_mod, use_gripper=True)

# Heat and shake on Heater-Shaker
hs_mod.set_and_wait_for_temperature(65)
hs_mod.close_labware_latch()
hs_mod.set_and_wait_for_shake_speed(600)
protocol.delay(minutes=15)
```

## API Version Requirements

- **Minimum API version:** 2.13
- **Recommended:** 2.19 or later for full feature support
- **Flex compatibility:** API 2.15+ with `robotType: "Flex"`

## Additional Resources

- **Module Documentation:** https://docs.opentrons.com/v2/modules/heater_shaker.html
- **Opentrons Support:** https://support.opentrons.com/
- **Protocol Examples:** https://protocols.opentrons.com/

## Related Skills

- `opentrons` - Main Opentrons Python API skill
- `opentrons-temperature-module` - Temperature-only control (4-95°C)
- `opentrons-thermocycler` - PCR thermal cycling
- `opentrons-magnetic-block` - Magnetic bead separation (Flex)
- `opentrons-gripper` - Automated labware movement (Flex)
