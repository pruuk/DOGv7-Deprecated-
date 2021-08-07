"""
This script will orchastrate combat for any number of participants that are
co-located in a single room. Most of the combat logic will be located elsewhere
in different files. The script will mostly just hold info about the combatants'
combat modifiers and call the functions for moving through combat.
"""
import random
from evennia import DefaultScript
from evennia.utils.logger import log_file
from world.combat_rules import combat_action_picker
from typeclasses.combat_actions import spawn_combat_action_object
from world.dice_roller import return_a_roll as roll

class CombatHandler(DefaultScript):
    """
    This implements the combat handler.
    """

    # standard script hooks

    def at_script_creation(self):
        "Called when script is first created"

        self.key = "combat_handler_%i" % random.randint(1, 1000000)
        self.desc = "handles combat"
        self.interval = 5  # five second timeout
        self.start_delay = False
        self.persistent = False

        # store all combatants
        self.db.characters = {}
        # store all actions for each turn
        self.db.turn_actions = {}
        # number of actions entered per combatant
        self.db.action_count = {}
        # store all temp vars for the characters
        # NOTE: to begin with, these will be stored on the character, but
        # later we will move these to the handler or to the mini-script
        # for carrying out each attack.
        self.db.char_temp_vars = {}

    def _init_character(self, character):
        """
        This initializes handler back-reference
        and combat cmdset on a character
        """
        character.ndb.combat_handler = self
        character.cmdset.add("commands.combat_commands.CombatCmdSet")
        log_file(f"Added backref for {self.name} to {character.name}.", \
                 filename='combat.log')
        # run initial combat mod calcs so everything will run in combat
        character.calculate_encumberance()
        character.calc_status_modifiers()
        character.calc_footwork_and_groundwork_mods()


    def _cleanup_character(self, character):
        """
        Remove character from handler and clean
        it of the back-reference and cmdset
        """
        dbref = character.id
        del self.db.characters[dbref]
        del self.db.turn_actions[dbref]
        del self.db.action_count[dbref]
        del self.db.char_temp_vars[dbref]
        del character.ndb.combat_handler
        character.cmdset.delete("commands.combat_commands.CombatCmdSet")
        character.db.info['In Combat'] = False

    def at_start(self):
        """
        This is called on first start but also when the script is restarted
        after a server reboot. We need to re-assign this combat handler to
        all characters as well as re-assign the cmdset.
        """
        for character in self.db.characters.values():
            self._init_character(character)

    def at_stop(self):
        "Called just before the script is stopped/destroyed."
        for character in list(self.db.characters.values()):
            # note: the list() call above disconnects list from database
            self._cleanup_character(character)

    def at_repeat(self):
        """
        This is called every self.interval seconds (turn timeout) or
        when force_repeat is called.

        At repeat, the plan is to use up an action from the queue of actions
        for each character. The action will then be converted into a smaller
        script for that action of a type related to the action type. For example,
        a character wanting to grapple will create a grapple action script,
        which will then carry out the action and self delete.

        """
        for character in self.db.characters.values():
            dbref = character.id
            # update the char variables
            log_file("*********************************************************************", \
                     filename='combat.log')
            log_file(f"START OF ROUND FOR {character.name}", \
                     filename='combat.log')
            self._refresh_combat_temp_vars(character)
            log_file(f"calling refresh_combat_validity func for {character.name}", \
                     filename='combat.log')
            combat_valid = self._combat_validity_check(character)
            log_file(f"combat validity check done. Result: {combat_valid}", \
                     filename='combat.log')
            if combat_valid == False:
                log_file(f"combat validity checks failed for {character.name}.", \
                         filename='combat.log')
                self._cleanup_character(self, character)
            else:
                log_file(f"combat validity checks passed for {character.name}.", \
                         filename='combat.log')
            log_file("calling combat action picker func", filename='combat.log')
            action_curated = combat_action_picker(character, self.db.turn_actions[dbref][0][0])
            log_file(f"{character.name} taking curated action: {action_curated}", \
                     filename='combat.log')
            spawn_combat_action_object(character, action_curated)
            log_file(f"END OF AT_REPEAT FOR {character.name}.", filename='combat.log')
        del self


    # combat handler methods
    def add_character(self, character):
        "Add combatant to handler"
        dbref = character.id
        self.db.characters[dbref] = character
        self.db.action_count[dbref] = 0
        self.db.turn_actions[dbref] = [(character.db.info['Default Attack'], \
                                        character, \
                                        character.db.info['Target'])]
        self.db.char_temp_vars[dbref] = [] # to be populated later at tick
        log_file(f"Added {character.name} to {self.name}", \
                 filename='combat.log')
        # set up back-reference
        self._init_character(character)
        # set character to be in combat
        character.db.info['In Combat'] = True

    def remove_character(self, character):
        "Remove combatant from handler"
        if character.id in self.db.characters:
            self._cleanup_character(character)
        if not self.db.characters:
            # if no more characters in battle, kill this handler
            self.stop()

    def msg_all(self, message):
        "Send message to all combatants"
        for character in self.db.characters.values():
            character.msg(message)

    def add_action(self, action, character, target):
        """
        Called by combat commands to register an action with the handler.

         action - string identifying the action, like "hit" or "parry"
         character - the character performing the action
         target - the target character or None

        actions are stored in a dictionary keyed to each character, each
        of which holds a list of max 2 actions. An action is stored as
        a tuple (character, action, target).
        """
        dbref = character.id
        count = self.db.action_count[dbref]
        if 0 <= count <= 1: # only allow 2 actions
            self.db.turn_actions[dbref][count] = (action, character, target)
        else:
            # report if we already used too many actions
            return False
        self.db.action_count[dbref] += 1
        return True

    def _test_func(self, character):
        log_file(f"test func for {character.name}.", filename='combat.log')

    def _refresh_combat_temp_vars(self, character):
        """
        Refreshes the temp variables related to combat and/or applies variables on
        a character for the first time.
        """
        log_file(f"Refreshing temp variables for: {character.name}", \
                 filename='combat.log')
        # check if the action needs to be changed to a flee action
        log_file("checking if attacker wants to flee or yield", filename='combat.log')
        character.check_wimpyield() # TODO: update wimpyyield to justs end the action to queue
        # refresh the attacker's prompt
        character.execute_cmd('rprom')
        # refresh attacker and defender temp combat calcs
        log_file("refreshing combat calcs", filename='combat.log')
        character.calculate_encumberance()
        character.calc_status_modifiers()
        character.calc_footwork_and_groundwork_mods()
        # set range if it hasn't been set
        log_file(f"checking if range is set for {character.name}", filename='combat.log')
        if character.ndb.range in ['out_of_range', 'ranged', 'melee', 'grapple']:
            log_file(f"Range was set for {character.name} to {character.ndb.range}", \
                     filename='combat.log')
        else:
            character.ndb.range = 'out_of_range'
        # get num of attacks
        character.populate_num_combat_actions()
        # character.db.info['Target'].calc_footwork_and_groundwork_mods()
        log_file(f"{character.name} \n\tEnc: {character.ndb.enc_mod} \
                 \n\thp_mod: {character.ndb.hp_mod} \tsp_mod: {character.ndb.sp_mod} \
                 \n\tcp_mod: {character.ndb.cp_mod} \tpos_mod: {character.ndb.pos_mod} \
                 \n\tfootwork: {character.ndb.footwork_mod} \tgroundwork: {character.ndb.groundwork_mod} \
                 \n\tNum_of_actions: {character.ndb.num_of_actions}", \
                 filename='combat.log')


    def _combat_validity_check(self, character):
        """
        Check to ensure the character should be in combat, that the combat vars
        and temp vars exist and make sense.

        return True if script can move on to spawning combat action script for
        this round.
        """
        if character.db.info['Target'] == None:
            log_file(f"Combat invalid. {character.name}'s target is None.", \
                     filename='combat.log')
            return False
        elif character.db.info['Target'] not in self.db.characters.values():
            log_file(f"Combat invalid. {character.name}'s target is not in handler character list.", \
                     filename='combat.log')
            return False
        elif character.db.info['In Combat'] == False:
            log_file(f"Combat invalid. {character.name} not In Combat.", \
                     filename='combat.log')
            return False
        elif character.db.info['Target'].db.info['In Combat'] == False:
            log_file(f"Combat invalid. {character.db.info['Target'].name} not In Combat.", \
                     filename='combat.log')
            return False
        elif character.location != character.db.info['Target'].location:
            log_file(f"Combat invalid. {character.name} is not in same location as {character.db.info['Target'].name}.", \
                     filename='combat.log')
            return False
        else:
            return True

    def create_combat_action_script(attacker):
        """
        Creates a new combat action script to carry out the combat actions for a
        single combat round. If an attacker is able to do multiple actions, such as
        multiple unarmed strikes, it will resolve all of them and output it as a
        single block.
        """
        pass
