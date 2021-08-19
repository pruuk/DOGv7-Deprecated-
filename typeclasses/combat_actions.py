"""
This file will contain the classes for combat action objects. These objects
will perform the action(s) that have been determined as correct for a character
or NPC by the combat_handler. For example, a character may want to flee, which
would instantiate a flee combat action object that will be associated with the
character. The action will be attempted by the character and then the combat
action object (script) will delete itself.

Some combat action objects might perform multiple attacks of a certain type
(for example 3 hits with a sword), but regardless, all combat action Objects
will carry out the actions for the round and then self-terminate.
"""
import random
from evennia import DefaultScript
from evennia.utils.logger import log_file
from world.combat_rules import actions_dict
from world.dice_roller import return_a_roll as roll
from evennia import create_script
from evennia import utils
from world.combat_messaging import build_msgs_for_unarmed_strikes_normal as msg_unarmed_normal
from world.combat_messaging import build_msgs_for_successful_dodge as msg_dodge
from world.combat_messaging import build_msgs_for_successful_block as msg_block
from world.combat_messaging import build_msgs_for_takedown as msg_takedown
from world.combat_messaging import build_msgs_for_grappling_improve_position as msg_grap_improve_pos
from world.combat_messaging import build_msgs_for_grappling_unarmed_strikes_normal as msg_grappling_unarmed_normal
from world.combat_messaging import build_msgs_for_grappling_submission as msg_grappling_sub
from world.combat_messaging import build_msgs_for_grappling_escape as msg_grappling_escape
from world.combat_messaging import build_msgs_for_melee_weapon_strikes as msg_melee_weapons
from world.combat_rules import apply_damage as apply_dam
from world.combat_rules import check_shield_block_multiplier as check_sbm

# # actions
# actions_dict = {
# 1 : 'unarmed_strike_normal', \
# 2 : 'unarmed_strike_natural_weapons', \
# 3 : 'melee_weapon_strike', \
# 4 : 'bash', \
# 5 : 'grapple_takedown', \
# 6 : 'grapple_improve_position', \
# 7 : 'grapple_unarmed_strike_normal', \
# 8 : 'grapple_unarmed_strike_natural_weapons', \
# 9 : 'grapple_melee_weapon_strike', \
# 10 : 'grapple_attempt_submission', \
# 11 : 'grapple_escape', \
# 12 : 'ranged_weapon_strike', \
# 13 : 'mental_attack_range_physical', \
# 14 : 'mental_attack_fire', \
# 15 : 'mental_attack_electrical', \
# 16 : 'mental_attack_domination', \
# 17 : 'taunt', \
# 18 : 'defend', \
# 19 : 'equip', \
# 20 : 'use', \
# 21 : 'drop', \
# 22 : 'yield', \
# 23 : 'flee', \
# 24 : 'disengage',
# 25 : 'decrease_range',
# 26 : 'increase_range',
# 27 : 'stand'}

class CombatActionObject(DefaultScript):
    """
    Abstract superclass for the all combat action scripts. Please use a subclass
    instead of this class.
    """

    def at_script_creation(self):
        "Called when script is first created"
        self.key = "cao_%i" % random.randint(1, 10000)
        self.desc = "executes combat action attempts"
        self.interval = 60
        # sixty second timeout. If we haven't carried out the combat actions
        # by then, we'll auto-delete the script to prevent scripts piling up
        self.start_delay = False
        self.persistent = False


    def _cleanup_character(self, character):
        """
        Remove character from handler and clean
        it of the back-reference and cmdset
        """
        dbref = self.id
        del self.db.character[dbref]

    def at_start(self):
        """
        This is called on first start but also when the script is restarted
        after a server reboot.
        """
        self.execute_purpose()

    def at_stop(self):
        "Called just before the script is stopped/destroyed."
        self._cleanup_character(self.db.character)

    def at_repeat(self):
        """
        This is called every self.interval seconds (turn timeout) or
        when force_repeat is called.
        """
        # we should only get here if the script failed to do the combat action
        # within 15 seconds
        log_file(f"At repeat - Combat action Script {self.key} deleting self", \
                 filename='combat_step.log')
        self.stop()

    # combat handler methods
    def add_character(self):
        "Add combatant to handler"
        self.db.character = self.obj
        log_file(f"Adding {self.obj.name} to {self.db.character} for {self.key}.", \
                 filename='combat_step.log')
        # add backrefs on character
        # character.db.combat_actioners.append(self)
        # log_file(f"Added backref for {self.name} to {character.name}.", \
        #          filename='combat.log')

    def execute_purpose(self):
        "Executes the combat action"
        pass



class CAOUnarmedStrikesNormal(CombatActionObject):
    """
    Combat action script that carries out normal unarmed combat strikes.
    """
    def execute_purpose(self):
        "Executes the combat action"
        log_file(f"{self.key} start of unarmed strikes normal action execution.", filename='combat_step.log')
        character = self.obj
        # loop through attacks
        for i in range(character.ndb.num_of_actions):
            log_file(f"Executing unarmed strike normal number: {i+1} for {character.name}", \
                     filename='combat_step.log')
            attack_hit = round(roll((character.talents.unarmed_striking.actual * \
                              character.ndb.footwork_mod), 'flat', \
                              character.ability_scores.Dex, character.talents.unarmed_striking))
            log_file(f"{character.name} attack roll: {attack_hit}", filename='combat.log')
            # use up stamina to attack
            character.traits.sp.current -= (12 / character.ndb.enc_mod)
            # get defender rolls
            defender = character.db.info['Target']
            log_file(f"doing defensive rolls for {defender.name}.", \
                     filename='combat_step.log')
            dodge_roll = round(roll((defender.ability_scores.Dex.actual * \
                               defender.ndb.footwork_mod) * .95, 'flat', \
                               defender.ability_scores.Dex))

            block_roll = round(roll((defender.ability_scores.Str.actual * \
                               defender.ndb.footwork_mod) * .9, 'flat', \
                               defender.ability_scores.Str))
            log_file(f"{defender.name} Dodge: {dodge_roll}\tBlock: {block_roll}", \
                     filename='combat.log')
            # use up some stamina to defend
            defender.traits.sp.current -= (5 / defender.ndb.enc_mod)
            if dodge_roll > attack_hit:
                msg_dodge(character, defender)
            elif block_roll > attack_hit:
                msg_block(character, defender)
            else:
                # TODO: Move this to apply damage function!
                damage = roll(character.ability_scores.Str.actual / 2, 'very flat', character.ability_scores.Str)
                defender.traits.hp.current -= damage
                log_file(f"{character.name} hit {defender.name} for {damage} damage. \
                         They have {defender.traits.hp.actual} hps left.", \
                         filename='combat.log')
                log_file("calling combat msging for unarmed attacks", filename='combat_step.log')
                msg_unarmed_normal(character, defender, damage)
                if defender.traits.hp.actual < 1:
                    # TODO: Implement death - for now we'll just flee
                    defender.execute_cmd('flee')
        log_file(f"Unarmed Strikes normal complete for {character.name}.", \
                 filename='combat_step.log')
        log_file(f"end of attacks - Combat action Script {self.key} deleting self", \
                 filename='combat_step.log')
        self.stop()



class CAOYield(CombatActionObject):
    """
    Combat action script that carries out the action of yielding.
    """
    def execute_purpose(self):
        "Executes the combat action"
        log_file(f"{self.key} start of yield action execution.", filename='combat_step.log')
        character = self.obj
        # check if the defender is the merciful type
        defender = character.db.info['Target']
        if defender.db.info['Mercy'] == True:
            character.location.msg_contents(f"{character.name} yields to {defender.name}, who is merciful.")
            log_file(f"{character.name} is yielding. killing combat handler: {character.ndb.combat_handler}", \
                     filename='combat_step.log')
            character.ndb.combat_handler.stop()
        else:
            character.location.msg_contents(f"{character.name} tries to yield to {defender.name}, but they have no mercy.")
        log_file(f"end of attacks - Combat action Script {self.key} deleting self", \
                 filename='combat_step.log')
        self.stop()


class CAOFlee(CombatActionObject):
    """
    Combat action script that carries out the action of yielding.
    """
    def execute_purpose(self):
        "Executes the combat action"
        log_file(f"{self.key} start of flee action execution.", filename='combat_step.log')
        character = self.obj
        exits = []
        for exit in character.location.exits:
            exits.append(exit)
        character.cmdset.delete("commands.combat_commands.CombatCmdSet")
        utils.delay(1,character.execute_cmd(f"{random.choice(exits)}"))
        log_file(f"{character.name} is fleeing. killing combat handler: {character.ndb.combat_handler}", \
                     filename='combat_step.log')
        character.ndb.combat_handler.stop()
        log_file(f"end of attacks - Combat action Script {self.key} deleting self", \
                 filename='combat_step.log')
        self.stop()


class CAOGrapplingTakedown(CombatActionObject):
    """
    Combat action script that carries out the action of taking down an opponent.
    """
    def execute_purpose(self):
        "Executes the combat action"
        log_file(f"{self.key} - start of grappling takedown action execution.", filename='combat_step.log')
        character = self.obj
        target = character.db.info['Target']
        character.traits.sp.current -= (20 / character.ndb.enc_mod)
        target.traits.sp.current -= (12 / target.ndb.enc_mod)
        # re-using groundwork rolls for determining success
        if character.ndb.groundwork_mod > target.ndb.groundwork_mod:
            log_file(f"{target.name} taken down by {character.name}.", filename='combat.log')
            character.ndb.range = 'grapple'
            target.ndb.range = 'grapple'
            if character.ndb.groundwork_mod > target.ndb.groundwork_mod * 3:
                # massive success, takedown directly to mount
                character.db.info['Position'] = 'mount'
                target.db.info['Position'] = 'mounted'
                success_lvl = 'mount'
            elif character.ndb.groundwork_mod > target.ndb.groundwork_mod * 1.75:
                # huge success, takedown directly to side control
                character.db.info['Position'] = 'side control'
                target.db.info['Position'] = 'side controlled'
                success_lvl = 'side control'
            elif character.ndb.groundwork_mod > target.ndb.groundwork_mod * 1.25:
                # great success, takedown directly to top
                log_file(f"{character.name} changing position from {character.db.info['Position']} to top.", \
                         filename='combat.log')
                character.db.info['Position'] = 'top'
                target.db.info['Position'] = 'in guard'
                success_lvl = 'top'
            else:
                # able to grapple, but in a clinch, no takedown
                character.db.info['Position'] = 'clinching'
                target.db.info['Position'] = 'clinched'
                success_lvl ='clinching'
        elif character.ndb.groundwork_mod * 4 < target.ndb.groundwork_mod:
            # massive failure
            log_file(f"{target.name} clowns takedown by {character.name}.", filename='combat.log')
            character.ndb.range = 'grapple'
            target.ndb.range = 'grapple'
            character.db.info['Position'] = 'mounted'
            target.db.info['Position'] = 'mount'
            success_lvl = 'mounted'
        elif character.ndb.groundwork_mod * 2.5 < target.ndb.groundwork_mod:
            # huge failure
            log_file(f"{target.name} easily avoids takedown by {character.name}.", filename='combat.log')
            character.ndb.range = 'grapple'
            target.ndb.range = 'grapple'
            character.db.info['Position'] = 'side controlled'
            target.db.info['Position'] = 'side control'
            success_lvl = 'side controlled'
        else:
            # failure to even close the distance
            log_file(f"{target.name} avoids takedown by {character.name}.", filename='combat.log')
            success_lvl = 'normal_failure'
        msg_takedown(character, target, success_lvl)
        log_file(f"end of attacks - Combat action Script {self.key} deleting self", \
                 filename='combat_step.log')
        self.stop()


class CAOGrapplingImprovePosition(CombatActionObject):
    """
    Combat action for improving position in a grappling encounter.
    """
    def execute_purpose(self):
        "Executes the combat action"
        log_file(f"{self.key} start of grappling improve position action execution.", \
                 filename='combat_step.log')
        ground_grappling_position_index = {
        1 : 'tbmount',
        2 : 'mount',
        3 : 'side control',
        4 : 'top',
        5 : 'in guard',
        6 : 'side controlled',
        7 : 'mounted',
        8 : 'prmounted'
        }
        standing_grappling_position_index = {
        1 : 'tbstanding',
        2 : 'clinching',
        3 : 'clinched',
        4 : 'standingbt'
        }
        character = self.obj
        target = character.db.info['Target']
        character.traits.sp.current -= (18 / character.ndb.enc_mod)
        target.traits.sp.current -= (15 / target.ndb.enc_mod)
        grappling_attack_dice = character.talents.grappling.actual * character.ndb.groundwork_mod
        grappling_block_dice = target.talents.grappling.actual * target.ndb.groundwork_mod
        grappling_attack_roll = round(roll(grappling_attack_dice, 'flat', \
                                character.ability_scores.Str, character.ability_scores.Dex, \
                                character.talents.grappling))
        grappling_block_roll = round(roll(grappling_block_dice, 'flat', \
                                target.ability_scores.Str, target.ability_scores.Dex, \
                                target.talents.grappling))
        log_file(f"Improve grappling pos. Attack Roll: {grappling_attack_roll} Block Roll: {grappling_block_roll}", \
                 filename='combat.log')
        # determine which index to use
        if character.db.info['Position'] in ground_grappling_position_index.values():
            c_grappling_status_list = [ground_grappling_position_index, 0]
        elif character.db.info['Position'] in standing_grappling_position_index.values():
            c_grappling_status_list = [standing_grappling_position_index, 0]
        else:
            log_file(f"Error in grappling improve position combat action. Attacker is not in a grappling position. Pos: {character.db.info['Position']}", \
                     filename='error.log')
        if target.db.info['Position'] in ground_grappling_position_index.values():
            t_grappling_status_list = [ground_grappling_position_index, 0]
        elif target.db.info['Position'] in standing_grappling_position_index.values():
            t_grappling_status_list = [standing_grappling_position_index, 0]
        else:
            log_file(f"Error in grappling improve position combat action. Attacker is not in a grappling position. Pos: {character.db.info['Position']}", \
                     filename='error.log')
        # make sure attacker and defender are actually in the same position indexes
        if c_grappling_status_list[0] != t_grappling_status_list[0]:
            log_file("Killing grappling improve position script. attacker and defender in wildly different positions.", \
                     filename='error.log')
            self.stop()
        # determine which index we're currently at
        for key, position in c_grappling_status_list[0].items():
            log_file(f"debug loop - checking {key} {position} against {character.db.info['Position']} {target.db.info['Position']}. ", \
                     filename='combat_step.log')
            if position == character.db.info['Position']:
                c_grappling_status_list[1] = key
            if position == target.db.info['Position']:
                t_grappling_status_list[1] = key
        log_file(f"Attacker grappling status initial: {c_grappling_status_list} Defender grappling status: {t_grappling_status_list}", \
                 filename='combat_step.log')
        # go through successes and failures
        if grappling_attack_roll * 3 < grappling_block_roll:
            # massive failure
            c_grappling_status_list[1] += 2
            t_grappling_status_list[1] -= 2
        elif grappling_attack_roll * 1.5 < grappling_block_roll:
            # critical failure
            c_grappling_status_list[1] += 1
            t_grappling_status_list[1] -= 1
        elif grappling_attack_roll * 1.5 >= grappling_block_roll and \
            grappling_attack_roll <= grappling_block_roll:
                # fail
                pass
        elif grappling_attack_roll > grappling_block_roll * 4:
            # massive success
            # if we were in a standing grappling position, we drag defender to
            # the ground. Otherwise, greatly improve position
            if c_grappling_status_list[0] == standing_grappling_position_index:
                c_grappling_status_list[0] = ground_grappling_position_index
                t_grappling_status_list[0] = ground_grappling_position_index
            else:
                c_grappling_status_list[1] -= 3
                t_grappling_status_list[1] -= 3
        elif grappling_attack_roll > grappling_block_roll * 3:
            # crit success
            c_grappling_status_list[1] -= 2
            t_grappling_status_list[1] += 2
        elif grappling_attack_roll > grappling_block_roll:
            # success
            c_grappling_status_list[1] -= 1
            t_grappling_status_list[1] += 1
        else:
            log_file("Error in determining grappling status for improve position.", \
                     filename='error.log')
        log_file(f"Attacker grappling status initial: {c_grappling_status_list} Defender grappling status: {t_grappling_status_list}", \
                 filename='combat_step.log')
        # Make sure we don't go out of list range
        if c_grappling_status_list[1] > len(c_grappling_status_list[0].keys()):
            c_grappling_status_list[1] = len(c_grappling_status_list[0].keys())
            t_grappling_status_list[1] = 1 + (len(c_grappling_status_list[0].keys()) - \
                                          c_grappling_status_list[1])
        elif c_grappling_status_list[1] < 1:
            c_grappling_status_list[1] = 1
            t_grappling_status_list[1] = len(c_grappling_status_list[0].keys())
        else:
            pass
        # apply the position changes
        character.db.info['Position'] = c_grappling_status_list[0][c_grappling_status_list[1]]
        target.db.info['Position'] = t_grappling_status_list[0][t_grappling_status_list[1]]
        log_file("calling msg func for improve grappling position", \
                 filename='combat_step.log')
        msg_grap_improve_pos(character, target)
        log_file(f"end of attacks - Combat action Script {self.key} deleting self", \
                 filename='combat_step.log')
        self.stop()


class CAOGrapplingUnarmedStrikesNormal(CombatActionObject):
    """
    Carries out normal unarmed strikes while in a grappling position.
    """
    def execute_purpose(self):
        "Executes the combat action"
        log_file(f"{self.key} start of grappling unarmed strikes normal action execution.", filename='combat_step.log')
        character = self.obj
        # loop through attacks
        for i in range(character.ndb.num_of_actions):
            log_file(f"Executing grappling unarmed strike normal number: {i+1} for {character.name}", \
                     filename='combat_step.log')
            attack_hit = round(roll((character.talents.unarmed_striking.actual * \
                              character.ndb.groundwork_mod), 'flat', \
                              character.ability_scores.Dex, character.talents.unarmed_striking))
            log_file(f"{character.name} attack roll: {attack_hit}", filename='combat.log')
            # use up stamina to attack
            character.traits.sp.current -= (12 / character.ndb.enc_mod)
            # get defender rolls
            defender = character.db.info['Target']
            log_file(f"doing defensive rolls for {defender.name}.", \
                     filename='combat_step.log')
            dodge_roll = round(roll((defender.ability_scores.Dex.actual * \
                               defender.ndb.groundwork_mod) * .9, 'flat', \
                               defender.ability_scores.Dex))
            block_roll = round(roll((defender.ability_scores.Str.actual * \
                               defender.ndb.groundwork_mod) * .9, 'flat', \
                               defender.ability_scores.Str))
            log_file(f"{defender.name} Dodge: {dodge_roll}\tBlock: {block_roll}", \
                     filename='combat.log')
            # use up some stamina to defend
            defender.traits.sp.current -= (5 / defender.ndb.enc_mod)
            if dodge_roll > attack_hit:
                msg_dodge(character, defender)
            elif block_roll > attack_hit:
                msg_block(character, defender)
            else:
                # TODO: Move this to apply damage function!
                damage = roll(character.ability_scores.Str.actual / 2, 'very flat', character.ability_scores.Str)
                defender.traits.hp.current -= damage
                log_file(f"{character.name} hit {defender.name} for {damage} damage. \
                         They have {defender.traits.hp.actual} hps left.", \
                         filename='combat.log')
                log_file("calling combat msging for unarmed attacks", filename='combat_step.log')
                msg_grappling_unarmed_normal(character, defender, damage)
                if defender.traits.hp.actual < 1:
                    # TODO: Implement death - for now we'll just flee
                    defender.execute_cmd('flee')
        log_file(f"Grappling Unarmed Strikes normal complete for {character.name}.", \
                 filename='combat_step.log')
        log_file(f"end of attacks - Combat action Script {self.key} deleting self", \
                 filename='combat_step.log')
        self.stop()


class CAOGrapplingSubmission(CombatActionObject):
    """
    Carries out a submission attempt while grappling.
    """
    def execute_purpose(self):
        "Executes the combat action"
        log_file(f"{self.key} start of grappling submission action execution.", filename='combat_step.log')
        character = self.obj
        target = character.db.info['Target']
        character.traits.sp.current -= (15 / character.ndb.enc_mod)
        target.traits.sp.current -= (12 / target.ndb.enc_mod)
        grappling_attack_dice = character.talents.grappling.actual * character.ndb.groundwork_mod
        grappling_block_dice = target.talents.grappling.actual * target.ndb.groundwork_mod
        grappling_attack_roll = round(roll(grappling_attack_dice, 'flat', \
                                character.ability_scores.Str, character.ability_scores.Dex, \
                                character.talents.grappling))
        grappling_block_roll = round(roll(grappling_block_dice, 'flat', \
                                target.ability_scores.Str, target.ability_scores.Dex, \
                                target.talents.grappling))
        log_file(f"Grappling submission. Attack Roll: {grappling_attack_roll} Block Roll: {grappling_block_roll}", \
                 filename='combat.log')
        if grappling_attack_roll > grappling_block_roll:
            # TODO: Move this to apply damage function!
            damage = roll(character.ability_scores.Str.actual / 2, 'very flat', character.ability_scores.Str)
            # note that submission damage is primarily to stamina. Attacker
            # will 'submit' the defender if they deplete their stamina
            target.traits.sp.current -= damage * .75
            target.traits.hp.current -= damage * .25
            log_file(f"{character.name} did a submission on {target.name}. \
                     They have {target.traits.sp.actual} sps left. \
                     They have {target.traits.hp.actual} hps left.", \
                     filename='combat.log')
            success = True
        else:
            # failed submision attempt
            success = False
            damage = 0
        log_file("calling combat msging for grappling submission attacks", filename='combat_step.log')
        msg_grappling_sub(character, target, damage, success)
        log_file(f"Grappling submission attempt complete for {character.name}.", \
                 filename='combat_step.log')
        log_file(f"end of attacks - Combat action Script {self.key} deleting self", \
                 filename='combat_step.log')
        self.stop()


class CAOGrapplingEscape(CombatActionObject):
    """
    Carries out an escape attempt while grappling.
    """
    def execute_purpose(self):
        "Executes the combat action"
        log_file(f"{self.key} start of grappling escape action execution.", \
                 filename='combat_step.log')
        character = self.obj
        # figure out who we're escaping from
        targeted_by_list = []
        log_file(f"Checking combatant list: {character.ndb.combat_handler.db.characters}", \
                 filename='combat_step.log')
        for combatant in character.ndb.combat_handler.db.characters.values():
            if combatant != character and combatant.db.info['Target'] == character:
                targeted_by_list.append(combatant)
        if len(targeted_by_list) == 0:
            # no one is targeting character, easy escape to the feet
            success = 'default'
            defender = None
        elif len(targeted_by_list) == 1:
            # we're grappling with just the one person
            defender = targeted_by_list[0]
            log_file(f"defender: {defender.name} will try top prevent escape.", \
                     filename='combat_step.log')
            escape_roll = round(roll((character.talents.grappling.actual * character.ndb.groundwork_mod), \
                          'flat', character.talents.grappling, \
                          character.ability_scores.Str, character.ability_scores.Dex))
            escape_defense = round(roll((defender.ndb.groundwork_mod * 100), \
                             'flat', defender.talents.grappling, \
                             defender.ability_scores.Str, defender.ability_scores.Dex))
        else:
            # multiple opponents targeting us, harder to escape
            defender = targeted_by_list[0] # TODO: Make this smarter for multi-combat
            log_file(f"defender: {defender.name} will try top prevent escape.", \
                     filename='combat_step.log')
            escape_roll = round(roll((character.talents.grappling.actual * character.ndb.groundwork_mod), \
                          'flat', character.talents.grappling, \
                          character.ability_scores.Str, character.ability_scores.Dex))
            escape_def_bonus = 1 + (.2 * len(targeted_by_list))
            for combatant in targeted_by_list:
                escape_def_bonus *= combatant.ndb.groundwork_mod
            escape_defense = round(roll((escape_def_bonus * 100), \
                             'flat'))
        # determine outcome, apply position and range changes
        log_file(f"Grappling escape rolls - Escaper: {character.name} {escape_roll} Defending: {defender.name} {escape_defense}", \
                 filename='combat.log')
        if escape_roll > escape_defense:
            success = 'success'
            character.db.info['Position'] = 'standing'
            character.ndb.range = 'melee'
            for combatant in targeted_by_list:
                combatant.db.info['Position'] = 'standing'
                if combatant.ndb.range == 'grapple':
                    combatant.ndb.range = 'melee'
        else:
            success = 'fail'
        log_file("calling combat msging for grappling escape", filename='combat_step.log')
        msg_grappling_escape(character, defender, success)
        log_file(f"Grappling escape attempt complete for {character.name}.", \
                 filename='combat_step.log')
        log_file(f"end of attacks - Combat action Script {self.key} deleting self", \
                 filename='combat_step.log')
        self.stop()


class CAOGrapplingMeleeWeaponStrike(CombatActionObject):
    """
    Carries out a strike with a small melee weapon while grappling.
    """
    def execute_purpose(self):
        "Executes the combat action"
        log_file(f"{self.key} start of grappling melee weapon strike action execution.", \
                 filename='combat_step.log')
        character = self.obj
        defender = character.db.info['Target']
        shield_block_multiplier = check_sbm(defender)
        # loop through attacks
        for i in range(character.ndb.num_of_actions):
            log_file(f"Executing grappling melee weapon strike number: {i+1} for {character.name}", \
                     filename='combat_step.log')
            attack_hit = round(roll((character.talents.melee_weapons.actual * \
                              character.ndb.groundwork_mod), 'flat', \
                              character.ability_scores.Dex, character.talents.melee_weapons))
            log_file(f"{character.name} attack roll: {attack_hit}", filename='combat.log')
            # use up stamina to attack
            character.traits.sp.current -= (12 / character.ndb.enc_mod)
            # get defender rolls
            defender = character.db.info['Target']
            log_file(f"doing defensive rolls for {defender.name}.", \
                     filename='combat_step.log')
            dodge_roll = round(roll((defender.ability_scores.Dex.actual * \
                               defender.ndb.groundwork_mod) * .9, 'flat', \
                               defender.ability_scores.Dex))
            block_roll = round(roll((defender.ability_scores.Str.actual * \
                               defender.ndb.groundwork_mod) * .9 * \
                               shield_block_multiplier, 'flat', \
                               defender.ability_scores.Str))
            log_file(f"{defender.name} Dodge: {dodge_roll}\tBlock: {block_roll}", \
                     filename='combat.log')
            # use up some stamina to defend
            defender.traits.sp.current -= (5 / defender.ndb.enc_mod)
            if dodge_roll > attack_hit:
                msg_dodge(character, defender)
            elif block_roll > attack_hit:
                msg_block(character, defender)
            else:
                if attack_hit > dodge_roll + block_roll:
                    critical_hit = True
                else:
                    critical_hit = False
                # call damage func here
                damage = apply_dam(character, defender, attack_type, critical_hit)
                log_file("calling combat msging for melee weapon attacks", filename='combat_step.log')
                msg_melee_weapons(character, defender, damage)
        log_file(f"Grappling melee weapon strikes complete for {character.name}.", \
                 filename='combat_step.log')
        log_file(f"end of attacks - Combat action Script {self.key} deleting self", \
                 filename='combat_step.log')
        self.stop()


class CAOMeleeWeaponStrike(CombatActionObject):
    """
    Carries out a strike with a melee weapon while in proper range.
    """
    def execute_purpose(self):
        "Executes the combat action"
        log_file(f"{self.key} start of melee weapon strike action execution.", \
                 filename='combat_step.log')
        character = self.obj
        defender = character.db.info['Target']
        shield_block_multiplier = check_sbm(defender)
        # loop through attacks
        for i in range(character.ndb.num_of_actions):
            log_file(f"Executing melee weapon strike number: {i+1} for {character.name}", \
                     filename='combat_step.log')
            attack_hit = round(roll((character.talents.melee_weapons.actual * \
                              character.ndb.footwork_mod), 'flat', \
                              character.ability_scores.Dex, character.talents.melee_weapons))
            log_file(f"{character.name} attack roll: {attack_hit}", filename='combat.log')
            # use up stamina to attack
            character.traits.sp.current -= (12 / character.ndb.enc_mod)
            # get defender rolls
            defender = character.db.info['Target']
            log_file(f"doing defensive rolls for {defender.name}.", \
                     filename='combat_step.log')
            dodge_roll = round(roll((defender.ability_scores.Dex.actual * \
                               defender.ndb.footwork_mod) * .9, 'flat', \
                               defender.ability_scores.Dex))
            block_roll = round(roll((defender.ability_scores.Str.actual * \
                               defender.ndb.footwork_mod) * .9 * \
                               shield_block_multiplier, 'flat', \
                               defender.ability_scores.Str))
            log_file(f"{defender.name} Dodge: {dodge_roll}\tBlock: {block_roll}", \
                     filename='combat.log')
            # use up some stamina to defend
            defender.traits.sp.current -= (5 / defender.ndb.enc_mod)
            if dodge_roll > attack_hit:
                msg_dodge(character, defender)
            elif block_roll > attack_hit:
                msg_block(character, defender)
            else:
                if attack_hit > dodge_roll + block_roll:
                    critical_hit = True
                else:
                    critical_hit = False
                # call damage func here
                attack_type = 'melee_weapons'
                log_file("calling apply damage for melee weapon strike", filename='combat_step.log')
                damage = apply_dam(character, defender, attack_type, critical_hit)
                log_file("calling combat msging for melee weapon attacks", filename='combat_step.log')
                msg_melee_weapons(character, defender, damage)
        log_file(f"Grappling melee weapon strikes complete for {character.name}.", \
                 filename='combat_step.log')
        log_file(f"end of attacks - Combat action Script {self.key} deleting self", \
                 filename='combat_step.log')
        self.stop()


# spawner func to instantiate the correct action type
def spawn_combat_action_object(character, action_curated):
    """
    This function chooses which combat action object type to spawn based upon
    the input from the handler. Note that we share the actions_dict with the
    combat_rules file in order to prevent the index getting out of sync.
    """
    log_file(f"Start of spawn_combat_action_object func for {character.name}", \
             filename='combat_step.log')
    if action_curated == 'unarmed_strike_normal':
        cao = create_script("typeclasses.combat_actions.CAOUnarmedStrikesNormal", obj=character)
    elif action_curated == 'yield':
        cao = create_script("typeclasses.combat_actions.CAOYield", obj=character)
    elif action_curated == 'flee':
        cao = create_script("typeclasses.combat_actions.CAOFlee", obj=character)
    elif action_curated == 'grapple_takedown':
        cao = create_script("typeclasses.combat_actions.CAOGrapplingTakedown", obj=character)
    elif action_curated == 'grapple_improve_position':
        cao = create_script("typeclasses.combat_actions.CAOGrapplingImprovePosition", obj=character)
    elif action_curated == 'grapple_unarmed_strike_normal':
        cao = create_script("typeclasses.combat_actions.CAOGrapplingUnarmedStrikesNormal", obj=character)
    elif action_curated == 'grapple_attempt_submission':
        cao = create_script("typeclasses.combat_actions.CAOGrapplingSubmission", obj=character)
    elif action_curated == 'grapple_escape':
        cao = create_script("typeclasses.combat_actions.CAOGrapplingEscape", obj=character)
    elif action_curated == 'grapple_melee_weapon_strike':
        cao = create_script("typeclasses.combat_actions.CAOGrapplingMeleeWeaponStrike", obj=character)
    elif action_curated == 'melee_weapon_strike':
        cao = create_script("typeclasses.combat_actions.CAOMeleeWeaponStrike", obj=character)
    else:
        log_file(f"Error in spawn_combat_action_object func. \
                 character: {character.name} action: {action_curated}. ", \
                 filename='error.log')
    return
