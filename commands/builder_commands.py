"""
This file will contain the set of commands reserved for use by builders/devs
for the MUD.
"""
from evennia import Command
from evennia import CmdSet
from evennia import default_cmds, utils

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
