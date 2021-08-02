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
