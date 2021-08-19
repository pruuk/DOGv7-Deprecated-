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

Please see the combat_handler script file in the typeclasses folder for more
details.
"""
import random
from evennia.utils.logger import log_file
from evennia import utils as utils
from world.dice_roller import return_a_roll as roll

# actions
actions_dict = {
1 : 'unarmed_strike_normal', \
2 : 'unarmed_strike_natural_weapons', \
3 : 'melee_weapon_strike', \
4 : 'bash', \
5 : 'grapple_takedown', \
6 : 'grapple_improve_position', \
7 : 'grapple_unarmed_strike_normal', \
8 : 'grapple_unarmed_strike_natural_weapons', \
9 : 'grapple_melee_weapon_strike', \
10 : 'grapple_attempt_submission', \
11 : 'grapple_escape', \
12 : 'ranged_weapon_strike', \
13 : 'mental_attack_range_physical', \
14 : 'mental_attack_fire', \
15 : 'mental_attack_electrical', \
16 : 'mental_attack_domination', \
17 : 'taunt', \
18 : 'defend', \
19 : 'equip', \
20 : 'use', \
21 : 'drop', \
22 : 'yield', \
23 : 'flee', \
24 : 'disengage',
25 : 'decrease_range',
26 : 'increase_range',
27 : 'stand'}

def combat_action_picker(character, action):
    """
    This function takes in a character object from the typeclasses.combat_handler
    script and determines which action script to spawn. That action script will
    determine the outcome of a character's actions for one combat round and then
    self-terminate.

    The combat_action script will be spawned by the combat handler. All this
    function does is determine which action type is to be attempted.
    """
    log_file("start of combat_action_picker func", filename='combat_step.log')
    log_file(f"{character.name} action: {action}", filename='combat_step.log')
    # grappling is the most complicated case. Moved it to its own funcion
    if action == 'grapple':
        log_file("calling resolve grappling action func to determine specific grappling action", \
                 filename='combat_step.log')
        grappling_action = resolve_grappling_action(character, action)
        log_file(f"grappling action type: {grappling_action}", filename='combat_step.log')
        if grappling_action == 'takedown':
            return actions_dict[5]
        elif grappling_action == 'improve_position':
            return actions_dict[6]
        elif grappling_action == 'submission':
            return actions_dict[10]
        elif grappling_action == 'unarmed_strike_normal':
            return actions_dict[7]
        elif grappling_action == 'unarmed_strike_natural_weapons':
            return actions_dict[8]
        elif grappling_action == 'melee_weapon_strike':
            return actions_dict[9]
        else:
            log_file(f"Weird output for grappling_action: {grappling_action}. \
                     Check code in world.combat_rules.", filename='error.log')
    # check first for flee actions, elminate cases where we're in bad grappling
    # position and not grappling
    elif character.ndb.range == 'grapple':
        if character.db.info['Position'] in ['side controlled', 'mounted', \
                                             'prmounted','standingbt']:
            # we're grappled and in a really bad position and we con't want to
            # be there. try to escape (regardless of preferred action)
            if action == 'flee':
                return actions_dict[23]
            elif action == 'yield':
                return actions_dict[22]
            else:
                return actions_dict[11]
        elif character.db.info['Position'] == 'standing':
            # we're standing. most of the time, we'll want to move back to a
            # more advantageous range
            if action == 'unarmed_strike':
                # strike some of the time, but move away most of the time
                if character.mutations.sharp_claws > 0:
                    curated_action = random.choices([actions_dict[26], actions_dict[8]], weights = (50, 50), k=1)
                    return str(curated_action[0])
                else:
                    curated_action = random.choices([actions_dict[26], actions_dict[7]], weights = (50, 50), k=1)
                    return str(curated_action[0])
            elif action == 'melee_weapon_strike':
                # check if we're using a two handed weapon.
                if character.slots['main hand'] != None and  character.slots['off hand'] != None and \
                   character.slots['main hand'].db.handedness > 1:
                   return actions_dict[26]
                else:
                    # strike some of the time, but move away most of the time
                    curated_action = random.choices([actions_dict[26], actions_dict[9]], weights = (70, 30), k=1)
                    return str(curated_action[0])
            elif action == 'taunt':
                # taunt some of the time, but move away most of the time
                curated_action = random.choices([actions_dict[26], actions_dict[17]], weights = (50, 50), k=1)
                return str(curated_action[0])
            elif action == 'flee':
                return actions_dict[23]
            elif action == 'yield':
                return actions_dict[22]
            elif action == 'disengage':
                return actions_dict[24]
            else:
                log_file(f"unknown decision tree for {character.name} while in \
                         range: {character.ndb.range} and \
                         position: {character.db.info['Position']}. \
                         Desired action: {action}",
                         filename='error.log')
        elif character.db.info['Position'] in ['tbmount', 'mount', 'side control']:
            # in a dominate grapplling position, but not choosing to grapple
            if action == 'unarmed_strike':
                # strike some of the time, but move away most of the time
                if character.mutations.sharp_claws > 0:
                    curated_action = random.choices([actions_dict[11], actions_dict[8]], weights = (50, 50), k=1)
                    return str(curated_action[0])
                else:
                    curated_action = random.choices([actions_dict[11], actions_dict[7]], weights = (50, 50), k=1)
                    return str(curated_action[0])
            elif action == 'melee_weapon_strike':
                # strike some of the time, but move away most of the time
                curated_action = random.choices([actions_dict[11], actions_dict[9]], weights = (50, 50), k=1)
                return str(curated_action[0])
            elif action == 'taunt':
                # taunt some of the time, but move away most of the time
                curated_action = random.choices([actions_dict[11], actions_dict[17]], weights = (50, 50), k=1)
                return str(curated_action[0])
            elif action == 'flee':
                return actions_dict[23]
            elif action == 'yield':
                return actions_dict[22]
            elif action == 'disengage':
                return actions_dict[24]
            else:
                log_file(f"unknown decision tree for {character.name} while in \
                         range: {character.ndb.range} and \
                         position: {character.db.info['Position']}. \
                         Desired action: {action}", \
                         filename='error.log')
        else:
            # in clinched, top, in guard, etc
            if action == 'unarmed_strike':
                # strike some of the time, but move away most of the time
                if character.mutations.sharp_claws > 0:
                    curated_action = random.choices([actions_dict[11], actions_dict[8]], weights = (50, 50), k=1)
                    return str(curated_action[0])
                else:
                    curated_action = random.choices([actions_dict[11], actions_dict[7]], weights = (50, 50), k=1)
                    return str(curated_action[0])
            elif action == 'melee_weapon_strike':
                # strike some of the time, but move away most of the time
                curated_action = random.choices([actions_dict[11], actions_dict[9]], weights = (50, 50), k=1)
                return str(curated_action[0])
            elif action == 'taunt':
                # taunt some of the time, but move away most of the time
                curated_action = random.choices([actions_dict[11], actions_dict[17]], weights = (50, 50), k=1)
                return str(curated_action[0])
            elif action == 'flee':
                return actions_dict[23]
            elif action == 'yield':
                return actions_dict[22]
            elif action == 'disengage':
                return actions_dict[24]
            else:
                log_file(f"unknown decision tree for {character.name} while in \
                         range: {character.ndb.range} and \
                         position: {character.db.info['Position']}. \
                         Desired action: {action}", \
                         filename='error.log')
    elif character.ndb.range == 'melee':
        if character.db.info['Position'] in ['sitting', 'supine', 'prone', \
                                             'sleeping']:
            return actions_dict[27]
        elif action in ['ranged_weapon_strike', 'mental_attack']:
            return actions_dict[26]
        elif action == 'melee_weapon_strike':
            return actions_dict[3]
        elif action == 'unarmed_strike':
            if character.mutations.sharp_claws > 0:
                return actions_dict[2]
            else:
                return actions_dict[1]
        elif action == 'bash':
            return actions_dict[4]
        elif action == 'taunt':
            return actions_dict[17]
        elif action == 'defend':
            return actions_dict[18]
        elif action == 'flee':
            return actions_dict[23]
        elif action == 'yield':
            return actions_dict[22]
        elif action == 'disengage':
            return actions_dict[24]
        else:
            log_file(f"unknown decision tree for {character.name} while in \
                     range: {character.ndb.range} and \
                     position: {character.db.info['Position']}. \
                     Desired action: {action}",
                     filename='error.log')
    elif character.ndb.range == 'ranged':
        if action  == 'ranged_weapon_strike':
            return actions_dict[26]
        elif action == 'mental_attack':
            return actions_dict[13]
            # TODO: Implement checks for different kinds of mental attacks once
            # we have them impmented
        elif action == 'taunt':
            return actions_dict[17]
        elif action == 'defend':
            return actions_dict[18]
        elif action == 'flee':
            return actions_dict[23]
        elif action == 'yield':
            return actions_dict[22]
        elif action == 'disengage':
            return actions_dict[24]
        elif action in ['unarmed_strike', 'melee_weapon_strike', 'bash', 'grapple']:
            return actions_dict[25]
        else:
            log_file(f"unknown decision tree for {character.name} while in \
                     range: {character.ndb.range} and \
                     position: {character.db.info['Position']}. \
                     Desired action: {action}",
                     filename='error.log')
    elif character.ndb.range == 'out_of_range':
        if action == 'taunt':
            return actions_dict[17]
        elif action == 'flee':
            return actions_dict[23]
        elif action == 'yield':
            return actions_dict[22]
        elif action == 'disengage':
            return actions_dict[24]
        else:
            return actions_dict[25]
    else:
        log_file(f"unknown decision tree for {character.name} while in \
                 range: {character.ndb.range} and \
                 position: {character.db.info['Position']}. \
                 Desired action: {action}",
                 filename='error.log')
    log_file(f"Decision tree for curating action failed. Returning None for {character.name} - action: {action}.", \
             filename='error.log')
    return None


def resolve_grappling_action(character, action):
    """
    Determine the specific action taken when the character is choosing to grapple.
    Because mma is so fluid, the position the character and defender are currently
    in affects the liklihood of an character choosing certain actions.
    """
    log_file("start of resolve grappling action func.", filename='combat_step.log')
    possible_grappling_actions = ['takedown', 'improve_position', 'submission', \
                                  'unarmed_strike_normal', 'unarmed_strike_natural_weapons', \
                                  'melee_weapon_strike']
    # if character is standing, we want to improve position (move into a grappling position)
    if character.db.info['Position'] == 'standing':
        log_file(f"character in position standing. takedown is the action to do.", \
                 filename='combat_step.log')
        grappling_action = ['takedown']
    elif character.db.info['Position'] in ['side controlled', 'mounted', \
                                          'prmounted', 'standingbt']:
        log_file(f"character in position side controlled, mounted, or worse. generating choices", \
                 filename='combat_step.log')
        grappling_action = random.choices(possible_grappling_actions, \
                           weights=(0, 95, 5, 0, 0, 0), k=1)
    elif character.db.info['Position'] in ['top', 'in guard']:
        log_file(f"character in position top or guard. generating choices", \
                 filename='combat_step.log')
        if character.mutations.sharp_claws.actual > 0:
            grappling_action = random.choices(possible_grappling_actions, \
                           weights=(0, 30, 30, 0, 40, 0), k=1)
            # TODO: Add conditional for wielding a small melee weapon
        else:
            grappling_action = random.choices(possible_grappling_actions, \
                           weights=(0, 30, 30, 40, 0, 0), k=1)
    elif character.db.info['Position'] in ['clinching', 'clinched']:
        log_file(f"character in position clinching or clinched. generating choices", \
                 filename='combat_step.log')
        if character.mutations.sharp_claws.actual > 0:
            grappling_action = random.choices(possible_grappling_actions, \
                           weights=(0, 40, 30, 0, 30, 0), k=1)
        # TODO: Add conditional for wielding a small melee weapon
        else:
            grappling_action = random.choices(possible_grappling_actions, \
                           weights=(0, 40, 30, 30, 0, 0), k=1)
    elif character.db.info['Position'] in ['tbmount', 'tbstanding']:
        log_file(f"character in position tbmount or tbstanding. generating choices", \
                 filename='combat_step.log')
        if character.mutations.sharp_claws.actual > 0:
            grappling_action = random.choices(possible_grappling_actions, \
                           weights=(0, 0, 70, 0, 30, 0), k=1)
            # TODO: Add conditional for wielding a small melee weapon
        else:
            grappling_action = random.choices(possible_grappling_actions, \
                           weights=(0, 0, 70, 30, 0, 0), k=1)
    else:
        if character.mutations.sharp_claws.actual > 0:
            log_file(f"character in position unknown. generating choices", \
                     filename='combat_step.log')
            grappling_action = random.choices(possible_grappling_actions, \
                           weights=(0, 10, 25, 0, 65, 0), k=1)
            # TODO: Add conditional for wielding a small melee weapon
        else:
            grappling_action = random.choices(possible_grappling_actions, \
                           weights=(0, 10, 25, 65, 0, 0), k=1)
    grappling_action = str(grappling_action[0])
    log_file(f"{character.name} is doing grappling action: {grappling_action}", \
             filename='combat_step.log')
    return grappling_action


def apply_damage(attacker, defender, attack_type, critical_hit):
    """
    Master function for applying damage. Damage multipliers from equipment
    and armor multipliers will be applied to the damage. This function will
    also do checks to determine if the defender's health, stamina, and
    conviction pools are above zero. If they are not, the death/exhaustion/
    ennunu functions will be called.
    """
    log_file("start of apply damage func in combat rules", filename='combat_step.log')
    if attack_type == "submission":
        # submissions bypass armor for damage to stamina, but armor has an
        # effect onm the damage to health
        pass
    elif attack_type == "mental_attack_non_psychokinetic":
        # damage is applied to conviction pool. Psychokinetic are generated by
        # the mind, but have physical effects (like a hurled projectile or fire)
        pass
    else:
        # all damage types that do physical damage are affcted by armor if they
        # aren't critical hits
        damage = round(roll( (attacker.ability_scores.Str.actual * attacker.ndb.eq_damage / defender.ndb.eq_phy_arm), \
                 'very flat', attacker.ability_scores.Str))
        defender.traits.hp.current -= damage
        log_file(f"{attacker.name} hit {defender.name} for {damage} damage. \
                 They have {defender.traits.hp.actual} hps left.", \
                 filename='combat.log')
        if defender.traits.hp.actual < 1:
            # TODO: Implement death - for now we'll just flee
            defender.execute_cmd('flee')
        return damage


def check_shield_block_multiplier(defender):
    """
    Checks to see if a defender is currently equipping a shield and applies
    a blocking modifier based upon the armor value of the shield to the
    chance to block.
    """
    shield_block_multiplier = 1
    for slot in defender.db.slots:
        if slot != None:
            if utils.inherits_from(slot, 'typeclasses.armors.Shield'):
                shield_block_multiplier *= slot.db.physical_armor_value
    return shield_block_multiplier
