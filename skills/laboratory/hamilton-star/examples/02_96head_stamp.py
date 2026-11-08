"""Stamp a whole 96-well plate with the CoRe 96 head, in simulation.

Verified against pylabrobot 0.2.2. Requires a STAR/STARlet fitted with a 96 head.
Run with:  python 02_96head_stamp.py   (add --hardware for a real robot)
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
    TIP_CAR_480_A00,
    STARLetDeck,
    cor_96_wellplate_360uL_Fb,
    hamilton_96_tiprack_300uL_filter,
    set_tip_tracking,
    set_volume_tracking,
)


def build_deck():
    deck = STARLetDeck()
    tip_car = TIP_CAR_480_A00(name="tip_carrier")
    tip_car[0] = hamilton_96_tiprack_300uL_filter(name="tips_01")
    deck.assign_child_resource(tip_car, rails=1)

    plt_car = PLT_CAR_L5AC_A00(name="plate_carrier")
    plt_car[0] = cor_96_wellplate_360uL_Fb(name="source")
    plt_car[1] = cor_96_wellplate_360uL_Fb(name="dest")
    deck.assign_child_resource(plt_car, rails=8)
    return deck


async def main(hardware: bool):
    set_tip_tracking(True)
    set_volume_tracking(True)

    backend = STARBackend() if hardware else STARChatterboxBackend()
    lh = LiquidHandler(backend=backend, deck=build_deck())
    await lh.setup()
    try:
        tips = lh.deck.get_resource("tips_01")
        source = lh.deck.get_resource("source")
        dest = lh.deck.get_resource("dest")
        for well in source.get_all_items():
            well.tracker.set_volume(150)

        await lh.pick_up_tips96(tips)
        await lh.aspirate96(source, volume=50)
        await lh.dispense96(dest, volume=50)
        await lh.return_tips96()

        print("dest H12 volume:", dest.get_well("H12").tracker.get_used_volume(), "uL")
    finally:
        await lh.stop()


if __name__ == "__main__":
    asyncio.run(main(hardware="--hardware" in sys.argv))
