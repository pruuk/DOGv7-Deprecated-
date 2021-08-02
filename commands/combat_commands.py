"""
This file will contain the commands used by players and NPC to initiate and/or
take actions during combat.
"""
# imports
from evennia import Command
from evennia import CmdSet
from evennia import default_cmds
from evennia import create_script
from evennia import utils
from world.combat_rules import hit_attempt
from evennia import TICKER_HANDLER as tickerhandler
import random
from evennia import search_object
from evennia.utils.logger import log_file
from evennia import gametime

class CmdAttack(Command):
    """
    Initiates combat

    Usage:
        attack <target>

    Aliases:
        kill <target>
        murder <target>

    This will initiate combat with the target. If the target is already in
    combat, you will join the combat.

    Note: You'll use your default attack unless you add actions to your
          combat action queue after combat starts.

    """
    key = "attack"
    aliases = ['kill', 'murder']
    help_category = "Combat"

    def func(self):
        "Handle command"
        caller = self.caller
        if not self.args:
            if self.caller.db.info['Target'] != None:
                if self.caller.location != self.caller.db.info['Target'].location:
                    self.caller.msg("Target not in room. Usage: attack <valid target>")
                    return
                else:
                    self.build_tickers(self.caller, self.caller.db.info['Target'])
                    return
            else:
                self.caller.msg("Usage: attack <target>")
                return
        else:
            target = self.caller.search(self.args.strip())
            if not target:
                self.caller.msg("Target not in room. Usage: attack <valid target>")
                return
            else:
                self.caller.db.info['Target'] = target
        # set up combat
        attacker = self.caller
        defender = self.caller.db.info['Target']
        if self.caller.location.db.nocombatroom != True:
            self.build_tickers(attacker, defender)
        else:
            self.caller.msg("Combat is not allowed in this room.")


    def build_tickers(self, attacker, defender):
        ## Add tickerhandlers for self and target (if they're
        ## not already in combat.
        ## Building attacker ticker
        attacker.db.info['In Combat'] = True
        ticker_id = str("attack_tick_%s" % attacker.name)
        tickerhandler.add(interval=4, callback=attacker.at_attack_tick, idstring=ticker_id, persistent=False)
        attacker.msg(f"You attack {defender}.")
        # Build the log file and establish the start of combat. Set references on
        # combatants so they can write to the same log file for the same combat
        # event.
        logfile_name_string = f"combat_log_{attacker.name}_{gametime.gametime()}"
        attacker.ndb.combatlog_filename = logfile_name_string
        defender.ndb.combatlog_filename = logfile_name_string
        log_file(f"{attacker.name} attacked {defender.name}", filename=logfile_name_string)
        attacker.cmdset.add("commands.combat_commands.CombatCmdSet")
        attacker.ndb.next_combat_action = []
        attacker.ndb.defending_bonus_mod = 1
        # set initial combat range in a temp variable
        if attacker.db.info['Default Attack'] == 'grapple':
            attacker.ndb.range = 'grapple'
        elif attacker.db.info['Default Attack'] in ['unarmed_strikes', \
            'melee_weapon_strike', 'bash', 'defend']:
            attacker.ndb.range = 'melee'
        elif attacker.db.info['Default Attack'] in ['ranged_weapon_strike', \
            'mental_attack', 'taunt']:
            attacker.ndb.range = 'ranged'
        else:
            attacker.ndb.range = 'out_of_range'
        ## Build defender ticker if they're not in combat already
        if defender.db.info['In Combat'] == False or defender.db.info['Target'] == attacker:
            defender.db.info['Target'] = attacker
            defender.db.info['In Combat'] = True
            defender.ndb.range = attacker.ndb.range
            ticker_id = str("attack_tick_%s" % defender.name)
            tickerhandler.add(interval=4, callback=defender.at_attack_tick, idstring=ticker_id, persistent=False)
            # defender.execute_cmd("emote is defending themselves!")
            defender.ndb.next_combat_action = []
            defender.ndb.defending_bonus_mod = 1
            defender.cmdset.add("commands.combat_commands.CombatCmdSet")
        else:
            if defender.ndb.range is not None:
                defender.ndb.range = attacker.ndb.range
            if defender.ndb.next_combat_action is not None:
                defender.ndb.next_combat_action = []
            if defender.defending_bonus_mod is not None:
                defender.ndb.defending_bonus_mod = 1
            if defender.db.info['Target'] is not None:
                defender.db.info['Target'] = attacker
        return


class CmdDisengage(Command):
    """
    Tries to disengage from combat.

    Usage:
      disengage

    """
    key = "disengage"
    aliases = ["disen"]
    help_category = "Combat"

    def func(self):
        "Implements the command"
        caller = self.caller
        # self.caller.db.toggles['In Combat'] = False
        self.caller.msg("You try to disengage from combat.")
        self.caller.ndb.next_combat_action.insert(0, "disengage")
        self.caller.db.info['In Combat'] = False


class CmdFlee(Command):
    """
    Tries to flee to an adjacent room.

    Usage:
      flee

    Aliases:
        escape

    """
    key = "flee"
    aliases = ['escape']
    help_category = "Combat"

    def func(self):
        "Implements the command"
        caller = self.caller
        self.caller.db.info['In Combat'] = False
        self.caller.ndb.next_combat_action.insert(0, "flee")
        exits = []
        for exit in self.caller.location.exits:
            exits.append(exit)
        self.caller.cmdset.delete("commands.combat_commands.CombatCmdSet")
        utils.delay(1,self.caller.execute_cmd(f"{random.choice(exits)}"))


class CombatCmdSet(CmdSet):
    """
    Adds the set of commands a player or NPC object will have available during
    combat. These should be removed after combat is over.
    """
    key = "combat_cmdset"
    mergetype = "Union" # we'll use this for now. Maybe we will use something else later
    priority = 10
    no_exits = True # stops the combatant from fleeing by just moving

    def at_cmdset_creation(self):
        self.add(CmdAttack())
        self.add(CmdDisengage())
        self.add(CmdFlee())
