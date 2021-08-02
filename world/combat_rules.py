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

# actions
COMBAT_ACTIONS = ('unarmed_strikes', 'melee_weapon_strike', 'bash', 'grapple', \
                  'ranged_weapon_strike', 'mental_attack', 'taunt', 'defend')
STRIKE_ACTIONS = ('unarmed_strikes', 'melee_weapon_strike', 'bash', 'ranged_weapon_strike')
FLEE_ACTIONS = ('disengage', 'flee', 'yield')
# Positions
GRAPPLING_POSITIONS_POSITIONS = ('tbmount', 'mount', 'side control', 'top', 'in guard', \
                    'side controlled', 'mounted', 'prmounted', 'tbstanding', \
                    'clinching', 'clinched', 'standingbt')
NON_GRAPPLING_POSITIONS = ('standing', 'sitting', 'supine', 'prone', 'sleeping', \
                           'floating', 'flying')
COMBAT_RANGES = ('out_of_range', 'ranged', 'melee', 'grappling')

def resolve_combat_actions(attacker, defender):
    """
    This is the master control function for a combat round from the point of
    view of the attacker. Combat rounds will consist of 9 steps (with some
    sub-steps):

    1. Determine the # of actions this round for the attacker
    2. Run character functions for updating combat modifiers/encumberance
    3. Combat validity checks - Should everyone be in combat? This includes
       checks for death (since we loop here from #9 sometimes)
    4. Roll for footwork/groundwork for the attacker and retrieve the last
       footwork roll from the defender. These will be used as a modifier for
       later actions. Store the attacker's roll in a temp attribute.
    5. Position checks - Is the attacker in a position to attack? If not, use
       an action to try to improve position. Roll a ground work check instead
       of a footwork check, use actions until we're in position or out of
       actions. If we have actions left after this, move on to step #3
    6. Combat range checks - Is the attacker close/far enough away to perform
       their attack? If not, use an action to move into range. If we have
       actions left, move on to #6.
    7. Check if we're just trying to defend - If we are, use up all actions.
       Each action will provide a bonus to a new roll for footwork to be stored
       in a temp attribute and used later when we are a defender. i.e. spending
       3 actions will result in a significant bonus
    8. Try to hit with our attack - If we hit, move on to #8 and check for
       damage. If we are dodged or blocked, send combat msg to the room's
       occupants. If we have actions left over, return to step #3.
    9. Roll for damage - send combat msgs out and apply damage. If we have
       actions left, return to step #2.
    """
    # attacker.execute_cmd("emote is attacking.")
    # defender.execute_cmd("emote is attacking.")
    attacker.location.msg_contents("\n")
    log_file("start of resolve combat function.", filename=attacker.ndb.combatlog_filename)
    # determine num of actions for the attacker and log it
    return_num_combat_actions(attacker)
    log_file(f"{attacker.name} gets {attacker.ndb.num_of_actions} actions this round.", \
             filename=attacker.ndb.combatlog_filename)
    # Run character functions for updating combat modifiers and log them
    attacker.calc_combat_modifiers()
    defender.calc_combat_modifiers()
    log_file(f"Attacker - {attacker.name} - Enc_Mod: {attacker.ndb.enc_mod} HP_Mod: \
            {attacker.ndb.hp_mod} SP_MOD: {attacker.ndb.sp_mod} CP_MOD: \
            {attacker.ndb.cp_mod}", filename=attacker.ndb.combatlog_filename)
    log_file(f"Defender - {defender.name} - Enc_Mod: {defender.ndb.enc_mod} HP_Mod: \
            {defender.ndb.hp_mod} SP_MOD: {defender.ndb.sp_mod} CP_MOD: \
            {defender.ndb.cp_mod}", filename=attacker.ndb.combatlog_filename)
    # loop through sequence until attacker is out of actions to use or combat
    # ends
    while attacker.ndb.num_of_actions > 0:
        log_file("start of combat action loop.", filename=attacker.ndb.combatlog_filename)
        log_file(f"{attacker.name} has {attacker.ndb.num_of_actions} actions \
                 remaining this round.", filename=attacker.ndb.combatlog_filename)
        # Run combat validity checks. log in that function
        run_combat_validty_checks(attacker, defender)
        # Run functions to calc position modifiers on combatants
        log_file("start of pos mod checks.", filename=attacker.ndb.combatlog_filename)
        attacker.calc_position_modifier()
        defender.calc_position_modifier()
        log_file(f"Attacker - {attacker.name} - POS_Mod: {attacker.ndb.position_mod}", \
                 filename=attacker.ndb.combatlog_filename)
        log_file(f"Defender - {defender.name} - POS_Mod: {defender.ndb.position_mod}", \
                 filename=attacker.ndb.combatlog_filename)
        # roll for footwork/groundwork for the round and/or retrieve the
        # defender's previous roll
        get_footwork_and_groundwork_modifiers(attacker, defender)
        # do position checks and related actions to get into position
        run_combat_position_checks(attacker, defender)
        # do range checks. sanity check the ranges based upon targeting
        run_combat_range_checks(attacker, defender)
        # apply bonuses for defending if attacker is choosing to do that
        apply_defense_bonuses(attacker)
        # try to hit with preferred attack
        hit_attempt(attacker, defender)
    return


def return_num_combat_actions(attacker):
    """
    Rolls to determine the number of actions the attacker can perform during
    this round of combat.
    """
    log_file("start of num of combat actions function.", filename=attacker.ndb.combatlog_filename)
    # listing out modifiers for readbility
    attacker.calculate_encumberance() # updates a temp variable named enc_mod
    stamina_modifier = 1 - ((attacker.traits.sp.current / attacker.traits.sp.max) ** .3)
    actions_roll = (((attacker.ability_scores.Dex.actual + \
                     attacker.ability_scores.Vit.actual) / 100) * \
                     attacker.ndb.enc_mod )
    attacker.ndb.num_of_actions = round(roll(actions_roll))
    return


def run_combat_validty_checks(attacker, defender):
    """
    Run all the checks necessary to ensure attacker and defender should continue
    to be in combat. If not, log the results of why combat ended and run cleanup
    functions to remove tickers and temp attributes.
    """
    log_file("start of combat validity checks.", filename=attacker.ndb.combatlog_filename)
    # check for death/exhaustion/loss of will
    if attacker.traits.hp.current < 1:
        log_file(f"{attacker.name} has no health left.", filename=attacker.ndb.combatlog_filename)
        end_combat(attacker, defender)
    elif defender.traits.hp.current < 1:
        log_file(f"{defender.name} has no health left.", filename=attacker.ndb.combatlog_filename)
        end_combat(attacker, defender)
    elif attacker.traits.sp.current < 1:
        log_file(f"{attacker.name} has no stamina left.", filename=attacker.ndb.combatlog_filename)
        end_combat(attacker, defender)
    elif defender.traits.sp.current < 1:
        log_file(f"{defender.name} has no stamina left.", filename=attacker.ndb.combatlog_filename)
        end_combat(attacker, defender)
    elif attacker.traits.cp.current < 1:
        log_file(f"{attacker.name} has no conviction left.", filename=attacker.ndb.combatlog_filename)
        end_combat(attacker, defender)
    elif defender.traits.cp.current < 1:
        log_file(f"{defender.name} has no conviction left.", filename=attacker.ndb.combatlog_filename)
        end_combat(attacker, defender)
    # have the attacker and defender run funcs to check if they want to
    # flee/yield
    attacker.check_wimpyield()
    defender.check_wimpyield()
    # check if the attacker wants to flee/disengage/yield/mercy
    if len(attacker.ndb.next_combat_action) > 0:
        if attacker.ndb.next_combat_action[0] in FLEE_ACTIONS:
            action = attacker.ndb.next_combat_action.pop(0)
            log_file(f"{attacker.name} is choosing to {action}.")
            if action == 'yield' and defender.db.info['Mercy']:
                log_file(f"{attacker.name} yields and {defender.name} grants mercy.", filename=attacker.ndb.combatlog_filename)
                attacker.execute_cmd(f"emote yields and {defender.name} grants mercy.")
                end_combat(attacker, defender)
            else:
                attacker.execute_cmd(action)
    if len(defender.ndb.next_combat_action) > 0:
        if 'yield' in defender.ndb.next_combat_action and attacker.db.info['Mercy']:
            attacker.execute_cmd(f"emote is merciful towards {defender.name} and allows them to yield.")
            log_file(f"{attacker.name} is merciful towards {defender.name}.", filename=attacker.ndb.combatlog_filename)
            end_combat(attacker, defender)
    # check if both combatants are in the room
    if attacker.location != defender.location:
        log_file(f"{attacker.name} and {defender.name} not located in same room. Ending combat.", filename=attacker.ndb.combatlog_filename)
        end_combat(attacker, defender)
    # check if everyone is marked as in combat
    if not attacker.db.info["In Combat"]:
        log_file(f"{attacker.name} is marked as not in combat.", filename=attacker.ndb.combatlog_filename)
        end_combat(attacker, defender)
    if not defender.db.info["In Combat"]:
        log_file(f"{defender.name} is marked as not in combat.", filename=attacker.ndb.combatlog_filename)
        end_combat(attacker, defender)
    return


def get_footwork_and_groundwork_modifiers(attacker, defender):
    """
    This function determines the groundwork and footwork multiplier for the
    attacker and defender. These are stored as temp variables on the attacker
    and defender objects to be used later for almost all combat actions.
    """
    log_file("start of footwork/groundwork mods func.", filename=attacker.ndb.combatlog_filename)
    # calc groundwork ratio
    att_groundwork_dice = attacker.talents.grappling.actual * \
                          attacker.ndb.position_mod * \
                          attacker.traits.mass.actual * \
                          attacker.ndb.hp_mod * \
                          attacker.ndb.sp_mod * attacker.ndb.cp_mod * \
                          attacker.ndb.enc_mod
    def_groundwork_dice = defender.talents.grappling.actual * \
                          defender.ndb.position_mod * \
                          defender.traits.mass.actual * defender.ndb.hp_mod * \
                          defender.ndb.defending_bonus_mod * \
                          defender.ndb.sp_mod * defender.ndb.cp_mod * \
                          defender.ndb.enc_mod
    attacker.ndb.groundwork = roll(att_groundwork_dice, 'flat', \
                              attacker.ability_scores.Dex.learn, \
                              attacker.talents.grappling.learn)
    defender.ndb.groundwork = roll(def_groundwork_dice, 'flat', \
                              defender.ability_scores.Dex.learn, \
                              defender.talents.grappling.learn)
    # calc footwork ratio
    att_footwork_dice = attacker.talents.footwork.actual * \
                        attacker.ndb.position_mod * attacker.ndb.hp_mod * \
                        attacker.ndb.sp_mod * attacker.ndb.cp_mod * \
                        attacker.ndb.enc_mod
    def_footwork_dice = defender.talents.footwork.actual * \
                        defender.ndb.position_mod * defender.ndb.hp_mod * \
                        defender.ndb.defending_bonus_mod * \
                        defender.ndb.sp_mod * defender.ndb.cp_mod * \
                        defender.ndb.enc_mod
    attacker.ndb.footwork = roll(att_footwork_dice, 'flat', \
                            attacker.ability_scores.Dex.learn, \
                            attacker.talents.footwork.learn)
    defender.ndb.footwork = roll(def_footwork_dice, 'flat', \
                            defender.ability_scores.Dex.learn, \
                            defender.talents.footwork.learn)
    return


def run_combat_position_checks(attacker, defender):
    """
    Runs a series of checks to ensure the attacker is in a position to make
    their preferred attack. If they are not, use an action to try to get into
    position until attacker is in position or is out of actions for the round.
    """
    log_file("start of position checks.", filename=attacker.ndb.combatlog_filename)
    if len(attacker.ndb.next_combat_action) > 0:
        preferred_action = attacker.ndb.next_combat_action[0]
    else:
        preferred_action = attacker.db.info['Default Attack']
    # elimiate the easiest case, attacker is standing
    if attacker.db.info['Position'] == 'standing':
        log_file(f"Position check complete for {attacker.name}. On to range check.", filename=attacker.ndb.combatlog_filename)
        return
    # attacker wants to grapple
    if preferred_action == 'grapple':
        log_file(f"Position check complete for {attacker.name}. On to range check.", filename=attacker.ndb.combatlog_filename)
        return
    # attacker in a grappling position on ground
    if attacker.db.info['Position'] in GRAPPLING_POSITIONS:
        # check if we're in bad position, try to improve position (ignoring preferred action)
        # use action to try to escape to feet. If in guard we'll assume the
        # attacker will still try to do unarmed strikes and other attacks
        # we may also call the ground_grapple_improve_position func later in
        # the combat steps if attacker is grappling by choice
        if attacker.db.info['Position'] in ['side controlled', 'mounted', \
                                            'prmounted', 'standingbt']:
            while attacker.db.info['Position'] != 'standing':
                if attacker.ndb.num_of_actions > 0:
                    grapple_improve_position(attacker, defender)
                else:
                    log_file(f"{attacker.name} is out of actions.", filename=attacker.ndb.combatlog_filename)
                    return


def grapple_improve_position(attacker, defender):
    """
    Attempt to improve position while grappling on ground.
    """
    log_file("start of improve grapple position func.", filename=attacker.ndb.combatlog_filename)
    if len(attacker.ndb.next_combat_action) > 0:
        a_preferred_action = attacker.ndb.next_combat_action[0]
    else:
        a_preferred_action = attacker.db.info['Default Attack']
    if len(defender.ndb.next_combat_action) > 0:
        d_preferred_action = defender.ndb.next_combat_action[0]
    else:
        d_preferred_action = defender.db.info['Default Attack']
    attacker.ndb.num_of_actions -= 1
    log_file(f"{attacker.name} attempting to improve their grappling position.", filename=attacker.ndb.combatlog_filename)
    # index the ground position
    position_index = {6 : 'tbmount', 5 : 'mount', 4 : 'tbstanding', \
                      3 : 'side control', 2 : 'top', 1 : 'clinching', \
                      0 : 'standing', -1 : 'clinched', -2 : 'in guard', \
                      -3 : 'side controlled', -4 : 'standingbt', \
                      -5 : 'mounted', -6 : 'prmounted'}
    for key, value in position_index.items():
        if value == attacker.db.info['Position']:
            att_pos_ind = key
        if value == defender.db.info['Position']:
            def_pos_ind = key

    if attacker.ndb.groundwork >= defender.ndb.groundwork * 1.5:
        # massive grappling success
        success = True
        pos_change = 3
    elif attacker.ndb.groundwork >= defender.ndb.groundwork * 1.25:
        # excellent grappling success
        success = True
        pos_change = 2
    elif attacker.ndb.groundwork >= defender.ndb.groundwork:
        # grappling success
        success = True
        pos_change = 1
    elif attacker.ndb.groundwork * 1.5 < defender.ndb.groundwork :
        # massive grappling failure
        success = false
        pos_change = -1
    else:
        # grappling failure
        success = false
        pos_change = 0

    # attacker doesn't want to grapple, trying to escape from bad position
    if a_preferred_action != 'grapple' and attacker.db.info['Position'] in \
                             ['side controlled', 'mounted', 'prmounted', \
                             'clinched', 'standingbt']:
        if success:
            log_file(f"{attacker.name} was able to escape.", filename=attacker.ndb.combatlog_filename)
            attacker.db.info['Position'] = 'standing'
            defender.db.info['Position'] = 'standing'
            attacker.ndb.range = 'melee'
            defender.ndb.range = 'melee'
            # TODO: Replace this with more elegant combat messaging later
            attacker.execute_cmd("emote escapes to their feet.")
            defender.execute_cmd("emote loses their grip on their opponent and stands.")
            return
        else:
            if pos_change == 0:
                log_file(f"{attacker.name} was unable to escape.", filename=attacker.ndb.combatlog_filename)
                # TODO: Replace this with more elegant combat messaging later
                # TODO: Account for critical failure
                attacker.execute_cmd("emote fails to escape to their feet.")
                defender.execute_cmd("emote maintains their control over their opponent.")
                return
            elif pos_change == -1:
                log_file(f"{attacker.name} failed to escape and worsened their position", filename=attacker.ndb.combatlog_filename)
                attacker.execute_cmd("emote fails badly to escape to their feet.")
                defender.execute_cmd("emote improves their control over their opponent.")
                if attacker.db.info['Position'] != 'prmounted':
                    att_pos_ind -= 1
                    def_pos_ind += 1
                    for key, value in position_index.items():
                        if att_pos_ind == key:
                            attacker.db.info['Position'] = value
                        if def_pos_ind == key:
                            defender.db.info['Position'] = value
                return
    # defender doesn't want to grapple, critical failure
    if d_preferred_action != 'grapple' and pos_change == -1:
        log_file(f"{defender.name} was able to escape.", filename=attacker.ndb.combatlog_filename)
        attacker.db.info['Position'] = 'standing'
        defender.db.info['Position'] = 'standing'
        attacker.ndb.range = 'melee'
        defender.ndb.range = 'melee'
        # TODO: Replace this with more elegant combat messaging later
        defender.execute_cmd("emote escapes to their feet.")
        attacker.execute_cmd("emote loses their grip on their opponent and stands.")
        return
    # attacker is here to improve position and wants to grapple
    if pos_change == 0:
        log_file(f"{attacker.name} attempts and fails to improve their position on the ground.", filename=attacker.ndb.combatlog_filename)
        # TODO: Move this to the combat messaging module when we get that written
        attacker.execute_cmd("emote attempts and fails to improve their position on the ground.")
    else:
        # determine the new positions for attacker and defender
        att_pos_ind += pos_change
        def_pos_ind -= pos_change
        if att_pos_ind > 6:
            att_pos_ind = 6
        elif att_pos_ind < -6:
            att_pos_ind = -6
        if def_pos_ind > 6:
            def_pos_ind = 6
        elif def_pos_ind < -6:
            def_pos_ind = -6
        for key, value in position_index.items():
            if att_pos_ind == key:
                attacker.db.info['Position'] = value
            if def_pos_ind == key:
                defender.db.info['Position'] = value
        # communicate the position change
        # TODO: Move this to the messaging function when we have that built
        if attacker.db.info['Position'] == 'tbmount':
            log_file(f"{attacker.name} takes the back of {defender.name} and flattens them out.", filename=attacker.ndb.combatlog_filename)
            attacker.execute_cmd(f"emote takes the back of {defender.name} and flattens them out.")
            return
        elif attacker.db.info['Position'] == 'mount':
            log_file(f"{attacker.name} mounts {defender.name}.", filename=attacker.ndb.combatlog_filename)
            attacker.execute_cmd(f"emote mounts {defender.name}.")
            return
        elif attacker.db.info['Position'] == 'side control':
            log_file(f"{attacker.name} obtains side control on {defender.name}.", filename=attacker.ndb.combatlog_filename)
            attacker.execute_cmd(f"emote obtains side control on {defender.name}.")
            return
        elif attacker.db.info['Position'] == 'top':
            log_file(f"{attacker.name} gets on top of {defender.name}. They pull guard", filename=attacker.ndb.combatlog_filename)
            attacker.execute_cmd(f"emote  gets on top of {defender.name}. They pull guard")
            return
        elif attacker.db.info['Position'] == 'standing':
            log_file(f"{attacker.name} and {defender.name} stand to their feet.", filename=attacker.ndb.combatlog_filename)
            attacker.execute_cmd(f"emote and {defender.name} stand to their feet.")
            attacker.ndb.range = 'melee'
            defender.ndb.range = 'melee'
            return
        elif attacker.db.info['Position'] == 'in guard':
            log_file(f"{attacker.name} pulls guard on {defender.name}, who is now on top.", filename=attacker.ndb.combatlog_filename)
            attacker.execute_cmd(f"emote pulls guard on {defender.name}, who is now on top.")
            return
        elif attacker.db.info['Position'] == 'side controlled':
            log_file(f"{attacker.name} scrambles around and ends up being side controlled by {defender.name}.", filename=attacker.ndb.combatlog_filename)
            attacker.execute_cmd(f"emote scrambles around and ends up being side controlled by {defender.name}.")
            return
        elif attacker.db.info['Position'] == 'mounted':
            log_file(f"{attacker.name} scrambles around and ends up being mounted by {defender.name}.", filename=attacker.ndb.combatlog_filename)
            attacker.execute_cmd(f"emote scrambles around and ends up being mounted by {defender.name}.")
            return
        elif attacker.db.info['Position'] == 'prmounted':
            log_file(f"{attacker.name} scrambles around, but ends up getting mounted from behind and flattenede out by {defender.name}.", filename=attacker.ndb.combatlog_filename)
            attacker.execute_cmd(f"emote scrambles scrambles around, but ends up getting mounted from behind and flattenede out by {defender.name}.")
            return
        elif attacker.db.info['Position'] == 'tbstanding':
            log_file(f"{attacker.name} takes the back of {defender.name} while standing.", filename=attacker.ndb.combatlog_filename)
            attacker.execute_cmd(f"emote takes the back of {defender.name} while standing.")
            return
        elif attacker.db.info['Position'] == 'clinching':
            log_file(f"{attacker.name} gains control of {defender.name} with a tight clinch.", filename=attacker.ndb.combatlog_filename)
            attacker.execute_cmd(f"emote gains control of {defender.name} with a tight clinch.")
            return
        elif attacker.db.info['Position'] == 'clinched':
            log_file(f"{attacker.name} is now controlled by the tight clinch of {defender.name}.", filename=attacker.ndb.combatlog_filename)
            attacker.execute_cmd(f"emote is now controlled by the tight clinch of {defender.name}.")
            return
        elif attacker.db.info['Position'] == 'standingbt':
            log_file(f"{attacker.name} has their back taken by {defender.name} while standing.", filename=attacker.ndb.combatlog_filename)
            attacker.execute_cmd(f"emote has their back taken by {defender.name} while standing.")
            return
        else:
            logger.log_trace("Unexpected outcome in ground_grapple_improve_position() func")
            return


def run_combat_range_checks(attacker, defender):
    """
    Runs checks to ensure the combat ranges make sense for the attacker and
    defender relative to each other. Uses an attacker action to move into to
    preferred range if it makes sense.
    """
    log_file("start of range checks.", filename=attacker.ndb.combatlog_filename)
    # set preferred attacks
    if len(attacker.ndb.next_combat_action) > 0:
        a_preferred_action = attacker.ndb.next_combat_action[0]
    else:
        a_preferred_action = attacker.db.info['Default Attack']
    if len(defender.ndb.next_combat_action) > 0:
        d_preferred_action = defender.ndb.next_combat_action[0]
    else:
        d_preferred_action = defender.db.info['Default Attack']
    # check for cases where defender is actually trying to fight someone else
    if defender.db.info['Target'] == None:
        defender.db.info['Target'] = attacker
        defender.ndb.range = attacker.ndb.range
    if defender.db.info['Target'] != attacker:
        # defender is distracted, move attacker into the range they want w/o
        # a check and w/o spending an action
        if a_preferred_action == 'grapple':
            attacker.ndb.range = 'grappling'
            # TODO: find a clean way later to express a penalty for someone
            # being overwhelmed by more than one opponent and/or being grappled
        elif a_preferred_action in ['unarmed_strikes', 'melee_weapon_strike', \
                                    'bash', 'defend']:
            attacker.ndb.range = 'melee'
        elif a_preferred_action in ['ranged_weapon_strike', 'mental_attack']:
            attacker.ndb.range = 'ranged'
        elif a_preferred_action in ['disengage', 'flee']:
            attacker.ndb.range = 'out_of_range'
        return
    else:
        # attacker and defender are facing off against each other
        # cases where ranges don't match up, fix this
        if defender.ndb.range != attacker.ndb.range:
            log_file(f"{attacker.name} and {defender.name} were set to different \
            ranges even though they are targeting each other. Fixing this", \
            filename=attacker.ndb.combatlog_filename)
            log_file(f"{attacker.name}: {attacker.ndb.range}", filename=attacker.ndb.combatlog_filename)
            log_file(f"{defender.name}: {defender.ndb.range}", filename=attacker.ndb.combatlog_filename)
            defender.ndb.range = attacker.ndb.range
        # ranges match, go through preferred actions and change range as needed
        if a_preferred_action == 'grappling':
            if attacker.ndb.range == 'grappling':
                return # already in preferred range, move on to next step
            if attacker.ndb.footwork < defender.ndb.footwork:
                # attacker lost footwork battle. use and action and return
                attacker.ndb.num_of_actions -= 1
                log_file(f"{attacker.name} tries to close the range with \
                         {defender.name}, but fails.", \
                         filename=attacker.ndb.combatlog_filename)
                attacker.execute_cmd(f"emote tries to close the range with \
                         {defender.name}, but fails.")
                return
            if attacker.ndb.range == 'melee':
                # attacker wants to grapple and won footwork battle, move
                # both to clinch from melee range
                attacker.ndb.num_of_actions -= 1
                attacker.db.info['Position'] = 'clinching'
                attacker.ndb.range = 'grappling'
                defender.db.info['Position'] = 'clinched'
                defender.ndb.range = 'grappling'
                log_file(f"{attacker.name} moves from melee range into \
                         grappling range with {defender.name} and clinches \
                them.", filename=attacker.ndb.combatlog_filename)
                attacker.execute_cmd(f"emote moves from melee range into \
                         grappling range with {defender.name} and clinches \
                         them.")
                return
            elif attacker.ndb.range == 'ranged':
                # attacker wants to grapple and won footwork battle, move
                # both to melee range, use an action
                attacker.ndb.num_of_actions -= 1
                attacker.ndb.range = 'melee'
                defender.ndb.range = 'melee'
                log_file(f"{attacker.name} closes range to {attacker.ndb.range}.")
                attacker.execute_cmd(f"emote closes range to {attacker.ndb.range}.")
                return
            else:
                # combatants were out of range. Move to ranged
                attacker.ndb.num_of_actions -= 1
                attacker.ndb.range = 'ranged'
                defender.ndb.range = 'ranged'
                log_file(f"{attacker.name} closes range to {attacker.ndb.range}.")
                attacker.execute_cmd(f"emote closes range to {attacker.ndb.range}.")
                return
        elif a_preferred_action in ['unarmed_strikes', 'melee_weapon_strike', \
                                    'bash']:
            if attacker.ndb.range == 'melee':
                return # already in preferred range, move on to next step
            if attacker.ndb.footwork < defender.ndb.footwork:
                # attacker lost footwork battle. use and action and return
                attacker.ndb.num_of_actions -= 1
                log_file(f"{attacker.name} tries to move to melee range with \
                         {defender.name}, but fails.", \
                         filename=attacker.ndb.combatlog_filename)
                attacker.execute_cmd(f"emote tries to move to melee range with \
                         {defender.name}, but fails.")
                return
            if attacker.ndb.range == 'grappling':
                # this case shouldn't occur, but we'll add it just for safety sake
                attacker.ndb.num_of_actions -= 1
                attacker.db.info['Position'] = 'standing'
                attacker.ndb.range = 'melee'
                defender.db.info['Position'] = 'standing'
                defender.ndb.range = 'melee'
                log_file(f"{attacker.name} moves from grappling range into \
                         melee range with {defender.name}.", \
                         filename=attacker.ndb.combatlog_filename)
                attacker.execute_cmd(f"emote moves from grappling range into \
                         melee range with {defender.name}.")
                return
            elif attacker.ndb.range == 'ranged':
                # attacker wants to grapple and won footwork battle, move
                # both to melee range, use an action
                attacker.ndb.num_of_actions -= 1
                attacker.ndb.range = 'melee'
                defender.ndb.range = 'melee'
                log_file(f"{attacker.name} closes range to {attacker.ndb.range}.")
                attacker.execute_cmd(f"emote closes range to {attacker.ndb.range}.")
                return
            else:
                # combatants were out of range. Move to ranged
                attacker.ndb.num_of_actions -= 1
                attacker.ndb.range = 'ranged'
                defender.ndb.range = 'ranged'
                log_file(f"{attacker.name} closes range to {attacker.ndb.range}.")
                attacker.execute_cmd(f"emote closes range to {attacker.ndb.range}.")
                return
        elif a_preferred_action == 'ranged_weapon_strike':
            if attacker.ndb.range == 'ranged':
                return # already in preferred range, move on to next step
            if attacker.ndb.footwork < defender.ndb.footwork:
                # attacker lost footwork battle. use and action and return
                attacker.ndb.num_of_actions -= 1
                log_file(f"{attacker.name} tries to move to ranged distance with \
                         {defender.name}, but fails.", \
                         filename=attacker.ndb.combatlog_filename)
                attacker.execute_cmd(f"emote tries to move to ranged distance with \
                         {defender.name}, but fails.")
                return
            if attacker.ndb.range == 'grappling':
                # this case shouldn't occur, but we'll add it just for safety sake
                attacker.ndb.num_of_actions -= 1
                attacker.db.info['Position'] = 'standing'
                attacker.ndb.range = 'melee'
                defender.db.info['Position'] = 'standing'
                defender.ndb.range = 'melee'
                log_file(f"{attacker.name} moves from grappling range into \
                         melee range with {defender.name}.", \
                         filename=attacker.ndb.combatlog_filename)
                attacker.execute_cmd(f"emote moves from grappling range into \
                         melee range with {defender.name}.")
                return
            elif attacker.ndb.range == 'melee':
                # attacker wants to grapple and won footwork battle, move
                # both to melee range, use an action
                attacker.ndb.num_of_actions -= 1
                attacker.ndb.range = 'ranged'
                defender.ndb.range = 'ranged'
                log_file(f"{attacker.name} moves away to {attacker.ndb.range}.", \
                         filename=attacker.ndb.combatlog_filename)
                attacker.execute_cmd(f"emote moves away to {attacker.ndb.range}.")
                return
            else:
                # combatants were out of range. Move to ranged
                attacker.ndb.num_of_actions -= 1
                attacker.ndb.range = 'ranged'
                defender.ndb.range = 'ranged'
                log_file(f"{attacker.name} closes range to {attacker.ndb.range}.", \
                         filename=attacker.ndb.combatlog_filename)
                attacker.execute_cmd(f"emote closes range to {attacker.ndb.range}.")
                return


def apply_defense_bonuses(attacker):
    """
    Use up attacker actions in order to defend. Apply bonuses to defense against
    attacks later by others.
    """
    log_file("start of defense bonuses func.", filename=attacker.ndb.combatlog_filename)
    if len(attacker.ndb.next_combat_action) > 0:
        a_preferred_action = attacker.ndb.next_combat_action[0]
    else:
        a_preferred_action = attacker.db.info['Default Attack']
    if a_preferred_action != 'defend':
        attacker.ndb.defending_bonus_mod = 1
        return
    else:
        # apply bonuses for defending. 10% per action used
        attacker.ndb.defending_bonus_mod = 1 + (attacker.ndb.num_of_actions * .1)
        log_file(f"{attacker.name} uses up {attacker.ndb.num_of_actions}, \
                 choosing to defend themself.", \
                 filename=attacker.ndb.combatlog_filename)
        attacker.execute_cmd(f"emote uses up {attacker.ndb.num_of_actions}, \
                 choosing to defend themself.")
        attacker.ndb.num_of_actions = 0
        return



def hit_attempt(attacker, defender):
    """
    This function checks if the attacker hits with their preferred attack type.
    """
    # TODO: Move this to its own mini func
    if len(attacker.ndb.next_combat_action) > 0:
        a_preferred_action = attacker.ndb.next_combat_action[0]
    else:
        a_preferred_action = attacker.db.info['Default Attack']
    log_file("start of hit attempt func.", filename=attacker.ndb.combatlog_filename)
    # attacker.msg("\n")
    # attacker.location.msg_contents(f"{attacker} tries to hit {defender}.")
    if a_preferred_action in FLEE_ACTIONS or attacker.db.info['In Combat'] == False or defender.db.info['In Combat'] == False:
        end_combat(attacker, defender)
        return
    if a_preferred_action in COMBAT_ACTIONS:
        attacker.ndb.num_of_actions -= 1
        # simplified round of combat to ensure everything is working. Replace
        # with real code after testing
        attack_hit = roll(attacker.ability_scores.Dex.actual, 'flat', attacker.ability_scores.Dex.learn)
        dodge_roll = roll((defender.ability_scores.Dex.actual * .9), 'flat', defender.ability_scores.Dex.learn)
        block_roll = roll((defender.ability_scores.Str.actual * .9), 'flat', defender.ability_scores.Str.learn)
        log_file(f"{attacker.name} attacks - hit: {attack_hit} dodge: {dodge_roll} block: {block_roll}", filename=attacker.ndb.combatlog_filename)
        if dodge_roll > attack_hit:
            attacker.location.msg_contents(f"{defender.name} dodges the attack of {attacker.name}.")
        elif block_roll > attack_hit:
            attacker.location.msg_contents(f"{defender.name} blocks the attack of {attacker.name}.")
        else:
            damage = rollsc(attacker.ability_scores.Str.actual)
            attacker.location.msg_contents(f"{attacker.name} hits {defender.name} for {damage} damage.")
            defender.traits.hp.current -= damage
            log_file(f"{attacker.name} hit {defender.name} for {damage} damage. \
                     They have {defender.traits.hp.actual} hps left.", \
                     filename=attacker.ndb.combatlog_filename)
            if defender.traits.hp.actual < 1:
                attacker.location.msg_contents(f"{defender.name} has died. Combat is over!")
                end_combat(attacker, defender)
            return

def end_combat(attacker, defender):
    "Ends combat, cleans up temp variables"
    log_file("start of end combat func.", filename=attacker.ndb.combatlog_filename)
    attacker.db.info['In Combat'] = False
    defender.db.info['In Combat'] = False
    att_ticker_id = str("attack_tick_%s" % (attacker.name))
    log_file(f"Trying to kill ticker: {att_ticker_id}.", filename=attacker.ndb.combatlog_filename)
    tickerhandler.remove(interval=4, callback=attacker.at_attack_tick, idstring=att_ticker_id, persistent=False)
    def_ticker_id = str("attack_tick_%s" % (defender.name))
    log_file(f"Trying to kill ticker: {def_ticker_id}.", filename=attacker.ndb.combatlog_filename)
    tickerhandler.remove(interval=4, callback=defender.at_attack_tick, idstring=def_ticker_id, persistent=False)
    del attacker.ndb.next_combat_action
    del defender.ndb.next_combat_action
    return
