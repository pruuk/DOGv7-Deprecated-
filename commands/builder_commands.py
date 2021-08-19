"""
This file will contain the set of commands reserved for use by builders/devs
for the MUD.
"""
from evennia import Command
from evennia import CmdSet
from evennia import default_cmds, utils
from evennia.utils.logger import log_file
import random

class CmdHeal(Command):
    """
    Fully heals up self if no target given.
    If target given, fully heals them instead unless that target is invalid.
    If the target is invalid, defaults to healing self.

    Usage:
        heal
        heal <target>

    """
    key = "heal"
    help_category = "Combat"
    locks = "cmd: perm(Builders)"

    def func(self):
        "Executes the command"
        caller = self.caller
        if self.args:
            target = self.caller.search(self.args)
            if target:
                target.traits.hp.fill_gauge()
                target.traits.sp.fill_gauge()
                target.traits.cp.fill_gauge()
                target.execute_cmd("rprom")
                self.caller.execute_cmd(f"emote heals {target.name}.")
        else:
            self.caller.traits.hp.fill_gauge()
            self.caller.traits.sp.fill_gauge()
            self.caller.traits.cp.fill_gauge()
            self.caller.execute_cmd("rprom")
            self.caller.execute_cmd("emote heals themself.")


class CmdSetBasePower(Command):
    """
    Allows a player with builder (or higher) permissions to reroll the ability
    scores of an NPC with a "roll dice number" of their choosing. Player
    character objects are rolled with an average of 100 (human normal). This
    command also allows the immortal to reroll specific ability scores on an
    NPC. This command *will not* work on a character object.

    Usage:
        setbasepower <npc> <number>
        setbasepower <npc> <ability score name> = <number>

    Aliases:
        setbp

    Note:
        If an invalid ability score name or an invalud number are passed in,
        this command will not work.

    """
    key = "setbasepower"
    aliases = ["setbp"]
    locks = "cmd: perm(Builders)"
    help_category = "Building"

    def func(self):
        "Set the ability score or all ability scores"
        if not self.args:
            self.caller.execute_cmd("help setbasepower")
            return
        string = self.args.split()
        npc = string.pop(0)
        if "=" in string:
            # it appears the caller is trying to set a specific score
            try:
                number = int(string.pop())
            except:
                self.caller.execute_cmd("help setbasepower")
                return
            ability_name = string.pop(0)
        else:
            ability_name = None
            try:
                number = int(string.pop())
            except:
                self.caller.execute_cmd("help setbasepower")
                return
        # search for the npc
        npc = self.caller.search(npc)
        if not npc:
            self.caller.msg("Please choose a valid NPC to set the base power for.")
        else:
            if utils.inherits_from(npc, 'typeclasses.npcs.NPC'):
                if ability_name == None:
                    # set all scores at once
                    npc.set_base_power(number)
                    self.caller.msg(f"Rolling new scores for {npc}.")
                    self.caller.execute_cmd(f"exam {npc}/ability_scores")
                else:
                    # set a specific score
                    npc.set_an_ability_score(ability_name, number)
                    self.caller.msg(f"Rolling new score for {npc}'s {ability_name}.")
                    self.caller.execute_cmd(f"exam {npc}/ability_scores")
            else:
                self.caller.msg("You're trying to edit a non-NPC object. Forget about it!")
                return


class CmdReroll(Command):
    """
    Wipes and rerolls the ability scores, talents, mutations and other
    attributes of a character. This is a dangerous command and should not
    be used on a character or NPC that is in combat or taking actions of
    any kind.

    Usage:
        reroll <character/NPC name>
    """
    key = "reroll"
    locks = "cmd: perm(Builders)"
    help_category = "Building"

    def func(self):
        "Reroll all ability scores"
        if not self.args:
            self.caller.execute_cmd("help reroll")
            return
        else:
            target = self.caller.search(self.args)
            if utils.inherits_from(target, 'typeclasses.npcs.NPC') or utils.inherits_from(target, 'typeclasses.characters.Character'):
                target.reroll()
                self.caller.msg(f"All ability scores and other attributes rerolled for {target.name}.")
            else:
                self.caller.msg("target is not a character or NPC.")
                log_file(f"{self.caller} tried to use reroll command on {target.name} of type {type(target)}.", \
                         filename='error.log')


class CmdShowColors(Command):
    """
    Sends a text colo palate for every possible numbered color palate to the
    caller, so they can see what colors are mapped to what.

    usage:
        rainbow

    """
    key = "rainbow"
    locks = "cmd: perm(Builders)"
    help_category = "Building"

    def func(self):
        """
        Give me that sweet unicorn puke!
        """
        colors = f" Text Colors by number: "
        for first_digit in range(6):
            for second_digit in range(6):
                for third_digit in range(6):
                    colors += f"|{first_digit}{second_digit}{third_digit}{first_digit}{second_digit}{third_digit}|n "
        self.caller.msg(f"{colors}")





class BuilderCmdSet(CmdSet):
    """
    Adds the set of commands a player or NPC object that are related to combat,
    but are available both inside and outside combat.
    """
    key = "builder_cmdset"
    mergetype = "Union" # we'll use this for now. Maybe we will use something else later
    priority = 10
    no_exits = False
    def at_cmdset_creation(self):
        self.add(CmdHeal())
        self.add(CmdSetBasePower())
        self.add(CmdReroll())
        self.add(CmdShowColors())
