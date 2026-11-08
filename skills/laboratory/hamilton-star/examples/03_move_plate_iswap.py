"""Move a plate between carrier sites with the iSWAP gripper, in simulation.

Verified against pylabrobot 0.2.2. Requires a STAR/STARlet fitted with an iSWAP.
Run with:  python 03_move_plate_iswap.py   (add --hardware for a real robot)
"""

import asyncio
import sys

from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.liquid_handling.backends import STARBackend
from pylabrobot.liquid_handling.backends.hamilton.STAR_chatterbox import (
    STARChatterboxBackend,
)
from pylabrobot.resources import (
    PLT_CAR_L5AC_A00,
    STARLetDeck,
    cor_96_wellplate_360uL_Fb,
)


def build_deck():
    deck = STARLetDeck()
    plt_car = PLT_CAR_L5AC_A00(name="plate_carrier")
    plt_car[0] = cor_96_wellplate_360uL_Fb(name="plate")
    deck.assign_child_resource(plt_car, rails=8)
    return deck


async def main(hardware: bool):
    backend = STARBackend() if hardware else STARChatterboxBackend()
    lh = LiquidHandler(backend=backend, deck=build_deck())
    await lh.setup()
    try:
        plate = lh.deck.get_resource("plate")
        carrier = lh.deck.get_resource("plate_carrier")

        # Move from site 0 to site 2. The iSWAP is the default gripper on a STAR;
        # pass use_arm="core" to use CoRe grippers held by two pipetting channels.
        await lh.move_plate(plate, carrier[2])
        print("plate is now on:", plate.parent.name)

        await lh.move_plate(plate, carrier[0])  # and back
        print("plate is now on:", plate.parent.name)
    finally:
        await lh.stop()


if __name__ == "__main__":
    asyncio.run(main(hardware="--hardware" in sys.argv))
