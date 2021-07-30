"""
This file will contain the set of rules and functions for determining the
outcome of combat between players and NPCs or NPCs and NPCs.

The end goal is to create a combat system that feels somewhat realistic, is
moderately interactive, and resolves relatively quickly compared to some
other MUDs.

Combat hit attempts will be measured against defense roll checks to see if the
attack was successful. Critical success rolls and critical failure rolls will
have consequences; both will create a chance to learn something from the combat
and both may affect the advantages and disadvatages of the combatants for later
actions.

By default, PCs and NPCs will have Mercy toggled on. This will mean that unless
they do a massive hit, they will stop attempting to hit the other wounded
combatant, stopping combat (unless the wounded combatant continues to be
aggressive, of course).
"""
# imports
import random
from world.dice_roller import return_a_roll as roll
from world.dice_roller import return_a_roll_sans_crits as rollsc
from evennia import TICKER_HANDLER as tickerhandler
from evennia import utils
from evennia.utils.logger import log_file

COMBAT_ACTIONS = ('unarmed_strike', 'melee_weapon_strike', 'bash', 'grapple', \
                  'ranged_weapon_strike', 'mental_attack', 'taunt', 'defend')
FLEE_ACTIONS = ('disengage', 'flee', 'yield', 'mercy')


def hit_attempt(attacker, defender, attack_command):
    """
    This should be called whenever one player/NPC is attempting an aggressive
    combat attack against another player/NPC. This function will do action
    checks for both the attacker and defender.

    The function will first check to ensure the attacker and defender are in
    the same room.

    If a flee type action is passed in by the attacker, combat will be ceased.
    """
    attacker.msg("\n")
    attacker.location_msg(f"{attacker} tries to hit {defender}.")
    if attack_command in FLEE_ACTIONS or attacker.db.info['In Combat'] == False or defender.db.info['In Combat'] == False:
        attacker.db.info['In Combat'] = False
        defender.db.info['In Combat'] = False
        log_file(f"Trying to kill ticker: {att_ticker_id}.", filename=attacker.ndb.combatlog_filename)
        tickerhandler.remove(interval=4, callback=attacker.at_attack_tick, idstring=att_ticker_id, persistent=False)
        def_ticker_id = str("attack_tick_%s" % (defender.name))
        log_file(f"Trying to kill ticker: {def_ticker_id}.", filename=attacker.ndb.combatlog_filename)
        tickerhandler.remove(interval=4, callback=defender.at_attack_tick, idstring=def_ticker_id, persistent=False)
    return
