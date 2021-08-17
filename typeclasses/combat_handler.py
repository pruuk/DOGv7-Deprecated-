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
        # store all temp vars for the characters
        # NOTE: to begin with, these will be stored on the character, but
        # later we will move these to the handler or to the mini-script
        # for carrying out each attack.
        self.db.char_temp_vars = {}
        # keep track of round # so it is easier to debug
        self.db.round_count = 1


    def _init_character(self, character):
        """
        This initializes handler back-reference
        and combat cmdset on a character
        """
        character.ndb.combat_handler = self
        character.cmdset.add("commands.combat_commands.CombatCmdSet")
        log_file(f"Added backref for {self.name} to {character.name}.", \
                 filename='combat_step.log')
        # run initial combat mod calcs so everything will run in combat
        character.calculate_encumberance()
        character.calc_status_modifiers()
        character.calc_footwork_and_groundwork_mods()


    def _cleanup_character(self, character):
        """
        Remove character from handler and clean
        it of the back-reference and cmdset
        """
        log_file(f"Starting cleanup for {character.name}.", \
                 filename='combat_step.log')
        dbref = character.id
        del character.ndb.combat_handler
        del character.ndb.hp_mod
        del character.ndb.sp_mod
        del character.ndb.cp_mod
        del character.ndb.enc_mod
        del character.ndb.groundwork_mod
        del character.ndb.footwork_mod
        del character.ndb.range
        del character.ndb.position_mod
        del character.ndb.num_of_actions
        character.cmdset.delete("commands.combat_commands.CombatCmdSet")
        character.db.info['In Combat'] = False
        character.db.info['Position'] = 'standing'
        character.execute_cmd("rprom")
        log_file(f"Cleanup for {character.name} is complete.", \
                 filename='combat_step.log')


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
        log_file("start of char cleanup func", filename='combat_step.log')
        for character in list(self.db.characters.values()):
            # note: the list() call above disconnects list from database
            self._cleanup_character(character)
        del self.db.characters[dbref]
        del self.db.turn_actions[dbref]
        del self.db.char_temp_vars[dbref]


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
            log_file(f"START OF ROUND: {self.db.round_count} FOR {character.name}", \
                     filename='combat_step.log')
            self.reconcile_range_and_position(character)
            self._refresh_combat_temp_vars(character)
            log_file(f"calling combat_validity func for {character.name}", \
                     filename='combat_step.log')
            combat_valid = self._combat_validity_check(character)
            log_file(f"combat validity check done. Result: {combat_valid}", \
                     filename='combat_step.log')
            if combat_valid == False:
                log_file(f"combat validity checks failed for {character.name}.", \
                         filename='combat_step.log')
                self._cleanup_character(self, character)
            else:
                log_file(f"combat validity checks passed for {character.name}.", \
                         filename='combat_step.log')
            log_file("calling combat action picker func", filename='combat_step.log')
            round_action = self.remove_action(character)
            action_curated = combat_action_picker(character, round_action)
            log_file(f"{character.name} taking curated action: {action_curated}", \
                     filename='combat_step.log')
            spawn_combat_action_object(character, action_curated)
            log_file(f"END OF AT_REPEAT FOR {character.name}.", filename='combat_step.log')
        self.db.round_count += 1


    # combat handler methods
    def add_character(self, character):
        "Add combatant to handler"
        dbref = character.id
        self.db.characters[dbref] = character
        self.db.turn_actions[dbref] = [(character.db.info['Default Attack'])]
        self.db.char_temp_vars[dbref] = [] # to be populated later at tick
        log_file(f"Added {character.name} to {self.name}", \
                 filename='combat_step.log')
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
        elif len(self.db.characters) < 2:
            # less than 2 chars in combat, ending combat
            log_file("less than 2 characters in combat. killing handler", \
                      filename='combat_step.log')
            self.stop()


    def msg_all(self, message):
        "Send message to all combatants"
        for character in self.db.characters.values():
            character.msg(message)


    def add_action(self, action, character):
        """
        Called by combat commands to register an action with the handler.

         action - string identifying the action, like "hit" or "parry"
         character - the character performing the action
         target - the target character or None

        actions are stored in a dictionary keyed to each character, each
        of which holds a list of max 2 actions. An action is stored as
        a tuple (character, action, target).
        """
        log_file(f"{self.key} - Start of add_action method for {character.name}.",
                 filename='combat_step.log')
        dbref = character.id
        self.db.turn_actions[dbref].insert(0, action)
        log_file(f"Added action: {action} for {character.name}", \
                 filename='combat_step.log')
        return


    def remove_action(self, character):
        """
        Pops off the action in the zero position if appropriate.
        Returns the desired action for the round.
        """
        log_file("start of remove action func", filename='combat_step.log')
        dbref = character.id
        if len(self.db.turn_actions[dbref]) > 0:
            log_file(f"Action at top of queue: {self.db.turn_actions[dbref][0]}", \
                 filename='combat_step.log')
        else:
            log_file(f"No Actions in queue: {self.db.turn_actions[dbref]}", \
                 filename='combat_step.log')
            return character.db.info['Default Attack']
        if self.db.turn_actions[dbref][0] == character.db.info['Default Attack']:
            return character.db.info['Default Attack']
        elif self.db.turn_actions[dbref][0] in ['flee', 'yield', 'disengage']:
            # for flee type actions, we won't pop it off. keep trying until we succeed
            return self.db.turn_actions[dbref][0]
        else:
            popped_action = self.db.turn_actions[dbref].pop(0)
            log_file(f"Returning action: {popped_action}", filename='combat_step.log')
            return popped_action


    def _refresh_combat_temp_vars(self, character):
        """
        Refreshes the temp variables related to combat and/or applies variables on
        a character for the first time.
        """
        log_file(f"Round: {self.db.round_count} Refreshing temp variables for: {character.name}", \
                 filename='combat_step.log')
        # check if the action needs to be changed to a flee action
        log_file(f"Round: {self.db.round_count} checking if attacker wants to flee or yield", filename='combat_step.log')
        character.check_wimpyield() # TODO: update wimpyyield to justs end the action to queue
        # refresh the attacker's prompt
        character.execute_cmd('rprom')
        # refresh attacker and defender temp combat calcs
        log_file(f"Round: {self.db.round_count} refreshing combat calcs", filename='combat_step.log')
        character.calculate_encumberance()
        character.calc_status_modifiers()
        character.calc_footwork_and_groundwork_mods()
        # set range if it hasn't been set
        log_file(f"Round: {self.db.round_count} checking if range is set for {character.name}", filename='combat_step.log')
        if character.ndb.range in ['out_of_range', 'ranged', 'melee', 'grapple']:
            log_file(f"Range was set for {character.name} to {character.ndb.range}", \
                     filename='combat_step.log')
        else:
            character.ndb.range = 'out_of_range'
        # get num of attacks
        character.populate_num_combat_actions()
        # character.db.info['Target'].calc_footwork_and_groundwork_mods()
        log_file(f"Round: {self.db.round_count} {character.name} \n\tEnc: {character.ndb.enc_mod} \
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
        log_file(f"Round: {self.db.round_count} Start of combat_validity func for {character.name}", \
                 filename='combat_step.log')
        if character.db.info['Target'] == None:
            log_file(f"Combat invalid. {character.name}'s target is None.", \
                     filename='combat_step.log')
            return False
        elif character.db.info['Target'] not in self.db.characters.values():
            log_file(f"Combat invalid. {character.name}'s target is not in handler character list.", \
                     filename='combat_step.log')
            return False
        elif character.db.info['In Combat'] == False:
            log_file(f"Combat invalid. {character.name} not In Combat.", \
                     filename='combat_step.log')
            return False
        elif character.db.info['Target'].db.info['In Combat'] == False:
            log_file(f"Combat invalid. {character.db.info['Target'].name} not In Combat.", \
                     filename='combat_step.log')
            return False
        elif character.location != character.db.info['Target'].location:
            log_file(f"Combat invalid. {character.name} is not in same location as their target.", \
                     filename='combat_step.log')
            return False
        else:
            return True


    def reconcile_range_and_position(self, character):
        """
        Check to see if the range and positions of the character make sense.
        If we put ourselves in a position and range that don't make sense
        together, end combat and send an error log.
        """
        range_and_position_dict = {
            'standing': {
                'grapple': True,
                'melee': True,
                'ranged': True,
                'out_of_range': True,
            },
            'tbmount' : {
                'grapple': True,
                'melee': False,
                'ranged': False,
                'out_of_range': False,
            },
            'mount' : {
                'grapple': True,
                'melee': False,
                'ranged': False,
                'out_of_range': False,
            },
            'side control' : {
                'grapple': True,
                'melee': False,
                'ranged': False,
                'out_of_range': False,
            },
            'top' : {
                'grapple': True,
                'melee': False,
                'ranged': False,
                'out_of_range': False,
            },
            'in guard' : {
                'grapple': True,
                'melee': False,
                'ranged': False,
                'out_of_range': False,
            },
            'side controlled' : {
                'grapple': True,
                'melee': False,
                'ranged': False,
                'out_of_range': False,
            },
            'mounted' : {
                'grapple': True,
                'melee': False,
                'ranged': False,
                'out_of_range': False,
            },
            'prmounted' : {
                'grapple': True,
                'melee': False,
                'ranged': False,
                'out_of_range': False,
            },
            'tbstanding': {
                'grapple': True,
                'melee': False,
                'ranged': False,
                'out_of_range': False,
            },
            'clinching' : {
                'grapple': True,
                'melee': False,
                'ranged': False,
                'out_of_range': False,
            },
            'clinched': {
                'grapple': True,
                'melee': False,
                'ranged': False,
                'out_of_range': False,
            },
            'standingbt' : {
                'grapple': True,
                'melee': False,
                'ranged': False,
                'out_of_range': False,
            },
            'sitting' : {
                'grapple': True,
                'melee': True,
                'ranged': False,
                'out_of_range': False,
            },
            'supine': {
                'grapple': True,
                'melee': True,
                'ranged': False,
                'out_of_range': False,
            },
            'prone' : {
                'grapple': True,
                'melee': True,
                'ranged': False,
                'out_of_range': False,
            },
            'sleeping': {
                'grapple': True,
                'melee': True,
                'ranged': False,
                'out_of_range': False,
            },
        }
        if range_and_position_dict[character.db.info['Position']][character.ndb.range] == True:
            log_file(f"reconcile check for range and positition for {character.name} passed.", \
                     filename='combat_step.log')
            return
        else:
            log_file(f"reconcile check for range and positition for {character.name} failed. See error log", \
                     filename='combat_step.log')
            log_file(f"Round: {self.db.round_count} Range: {character.ndb.range} and Position: {character.db.info['Position']} for {character.name} do not match up. Killing {self.key}.", \
                     filename='error.log')
            self.stop()
