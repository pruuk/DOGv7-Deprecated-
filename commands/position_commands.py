"""
This file will contain the commands that change the position of the character,
such as stand, sit, rest, etc... All commands except stand will result in
a command set being applied that prevents movement.
"""
from evennia import Command
from evennia import CmdSet
from evennia import default_cmds
from evennia import search_object
from evennia.utils.logger import log_file

class CmdStand(Command):
    """
    Causes the character to stand.

    Aliases:
        st
    """
    key = "stand"
    aliases = ['st']
    help_category = "General"

    def func(self):
        "Implements the command"
        self.caller.msg("You stand to your feet.")
        self.caller.db.info['Position'] = 'standing'


class CmdCollapse(Command):
    """ Causes the character to collapse in a heap """
    key = "collapse"
    help_category = "General"

    def func(self):
        "Implements the command"
        self.caller.msg("You collapse to the floor from exhaustion.")
        self.caller.db.info['Position'] = 'prone'


class CmdSit(Command):
    """ Causes the character to sit """
    key = "sit"
    help_category = "General"

    def func(self):
        "Implements the command"
        self.caller.msg("You sit down.")
        self.caller.db.info['Position'] = 'sitting'


class CmdRest(Command):
    """
    Causes the character to rest, which improves recovery rate for health,
    stamina, and conviciton.
    """
    key = "rest"
    help_category = "General"

    def func(self):
        "Implements the command"
        self.caller.msg("You get comfortable and rest.")
        self.caller.db.info['Position'] = 'resting'


class CmdSleep(Command):
    """
    Causes the character to sleep, which improves recovery rate for health,
    stamina, and conviciton.
    """
    key = "sleep"
    help_category = "General"

    def func(self):
        "Implements the command"
        self.caller.msg("You lie down and fall into a slumber.")
        self.caller.db.info['Position'] = 'sleeping'


class CmdBashedToGround(Command):
    """
    Causes the character to get bashed onto their backside
    """
    key = "bashedtoground"
    help_category = "General"

    def func(self):
        "Implements the command"
        self.caller.msg("You are propelled onto your back.")
        self.caller.db.info['Position'] = 'supine'


class PreventMoveUntilStandCmdSet(CmdSet):
    """
    This Command Set only contain stand, which will allow the character to move
    again. This Command Set prevents movement and is triggered by getting knocked
    down or moving into a non-standing position.
    """
    key = "prevent_move_cmdset"
    mergetype = "Union" # we'll use this for now. Maybe we will use something else later
    priority = 10
    no_exits = True # stops the character from moving from the room

    def at_cmdset_creation(self):
        self.add(CmdStand())


class NonStandingPositionCmdSet(CmdSet):
    """
    This command set contains the set of commands to move into a non-standing
    position. Although the character will execute the command, some of these
    commands will be executed involuntarily, such as collapsing from exhaustion
    or being knocked on their ass by a bash in combat.
    """
    key = "non-standing_positions_cmdset"
    mergetype = "Union" # we'll use this for now. Maybe we will use something else later
    priority = 10
    no_exits = False # stops the character from moving from the room

    def at_cmdset_creation(self):
        # self.add(CmdCollapse())
        self.add(CmdSit())
        self.add(CmdRest())
        # self.add(CmdBashedToGround())
        self.add(CmdSleep())
