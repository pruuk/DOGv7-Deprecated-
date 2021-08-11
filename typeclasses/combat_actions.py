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
        log_file(f"Combat action Script {self.key} deleting self", \
                 filename='combat.log')
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
        log_file(f"{self.key} start of action execution.", filename='combat_step.log')
        character = self.obj
        # loop through attacks
        for i in range(character.ndb.num_of_actions):
            # TODO: MOve this to combat rules once we get it working
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
        log_file(f"{self.key} start of action execution.", filename='combat_step.log')
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
        log_file(f"{self.key} start of action execution.", filename='combat_step.log')
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
    else:
        log_file(f"Error in spawn_combat_action_object func. \
                 character: {character.name} action: {action_curated}. ", \
                 filename='error.log')
    return
