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
        if not self.args:
            self.caller.msg("Usage: attack <target>")
            return
        target = self.caller.search(self.args)
        if not target:
            return
        else:
            self.caller.db.info['Target'] = target
        # set up combat
        if target.ndb.combat_handler:
            # target is already in combat - join it
            log_file(f"{target.name} already in combat. {self.name} joining \
                     combat using handler: {target.ndb.combat_handler}", \
                     filename='combat_step.log')
            target.ndb.combat_handler.add_character(self.caller)
            target.ndb.combat_handler.msg_all("%s joins combat!" % self.caller)
        else:
            # create a new combat handler
            log_file("New combat. creating handler script", \
                     filename='combat_step.log')
            # set range per preferred attack
            if self.caller.db.info['Default Attack'] in ['unarmed_strike', \
                              'melee_weapon_strike', 'bash', 'grapple',]:
                self.caller.ndb.range = 'melee'
            elif self.caller.db.info['Default Attack'] in ['ranged_weapon_strike', \
                              'mental_attack', 'taunt', 'defend']:
                self.caller.ndb.range = 'ranged'
            else:
                self.caller.ndb.range = 'out_of_range'
            # set target if not set
            if self.caller.db.info['Target'] == None:
                self.caller.db.info['Target'] = target
            # matching target range with caller since they weren't in combat
            target.ndb.range = self.caller.ndb.range
            # matching target's target to caller
            target.db.info['Target'] = self.caller
            # make combat handler
            chandler = create_script("combat_handler.CombatHandler")
            chandler.add_character(self.caller)
            chandler.add_character(target)
            self.caller.msg("You attack %s! You are in combat." % target)
            target.msg("%s attacks you! You are in combat." % self.caller)
            log_file(f"New handler script: {chandler.name}", \
                     filename='combat_step.log')
            log_file(f"Script created. Chars add: {chandler.db.characters}.", \
                     filename='combat_step.log')

COMBAT_ACTIONS = ('unarmed_strike', 'melee_weapon_strike', 'bash', 'grapple', \
                  'ranged_weapon_strike', 'mental_attack', 'taunt', 'defend')


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
        # self.caller.db.info['In Combat'] = False
        self.caller.msg("You try to disengage from combat.")
        log_file(f"Attempting to add disengage to {self.caller.ndb.combat_handler} for {self.caller}",
                 filename='combat_step.log')
        self.caller.ndb.combat_handler.add_action("disengage", self.caller)


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
        self.caller.msg("You attempt to flee.")
        log_file(f"Attempting to add flee to {self.caller.ndb.combat_handler} for {self.caller}",
                 filename='combat_step.log')
        self.caller.ndb.combat_handler.add_action("flee", self.caller)



class CmdYield(Command):
    """
    Tries to yield to your current opponent. This will only be successful if the
    opponent has mercy enabled.

    Usage:
        yield

    """
    key = "yield"
    help_category = "Combat"

    def func(self):
        "Implements the command"
        caller = self.caller
        self.caller.msg("You attempt to yield.")
        log_file(f"Attempting to add yield to {self.caller.ndb.combat_handler} for {self.caller}",
                 filename='combat_step.log')
        self.caller.ndb.combat_handler.add_action("yield", self.caller)


class CmdDefend(Command):
    """
    Forgoes attacking in favor of just trying to defend. This will spend your
    combat actions just like attacking would, but will provide a defense bonus
    until your next combat round.

    Usage:
        defend

    """
    key = "defend"
    help_category = "Combat"

    def func(self):
        "Implements the command"
        caller = self.caller
        self.caller.msg("You attempt to defend.")
        log_file(f"Attempting to add defend to {self.caller.ndb.combat_handler} for {self.caller}",
                 filename='combat_step.log')
        self.caller.ndb.combat_handler.add_action("defend", self.caller)


class CmdTarget(Command):
    """
    This command allows a character to set another
    character or NPC as their default target for later
    actions by default. This is also called when combat
    is initiated by commands like "kill <target>".

    Usage:
        target <target>

    """
    key = "target"
    help_category = "Combat"

    def func(self):
        "Sets the caller's default target"
        caller = self.caller
        if not self.args:
            self.caller.msg('Please input a valid target')
        else:
            if self.caller.search(self.args):
                self.caller.db.info['Target'] = self.caller.search(self.args)
                self.caller.msg(f"Target set to: {self.caller.db.info['Target']}")
            else:
                self.caller.msg("That is not a valid target")


class CmdDefaultAttack(Command):
    """
    This command allows a character to set their default command, For example,
    the player could choose to default to 'defend' instead of 'unarmed strike'.
    A total pacifist could even default to 'flee' (this is not recommended).

    Usage:
        default <default attack>

    Valid examples:
        default unarmed_strike
        default melee_weapon_strike
        default bash
        default grapple
        default ranged_weapon_strike
        default mental_attack
        default taunt
        default defend
        default disengage
        default flee
        default yield


    """
    key = "default"
    help_category = "Combat"

    def func(self):
        "Sets the default attack option"
        caller = self.caller
        valid_defaults = ['unarmed_strike', 'melee_weapon_strike', 'bash', \
                          'grapple', 'ranged_weapon_strike', 'mental_attack', \
                          'taunt', 'defend', 'disengage', 'flee', 'yield',]

        if self.args:
            self.caller.msg(f"You set your default attack as:{self.args}")
            self.caller.db.info['Default Attack'] = self.args.lstrip()
        else:
            self.caller.msg('Please input a valid default attack. See help default')
            self.caller.msg(f'You tried default{self.args}')


class CmdConsider(Command):
    """
    Allows the character or NPC to estimate the relative values of certain
    attaributes in a comparison between themself and the target. Some NPCs
    consider being considered offensive.
    Consider returns three text messages:
        - A comparison of the force of your conviction and the target's
        - A comparison of vigor (health + stamina)
        - A comparison of mass

    Usage:
        consider <target>

    Aliases:
        con <target>

    """
    key = "consider"
    aliases = ['con']
    help_category = "Combat"

    def func(self):
        "Implements the command"
        if not self.args:
            self.caller.msg("Usage: consider <target>")
            return
        else:
            target = self.caller.search(self.args.strip())
            if not target:
                self.caller.msg("Target not in room. Usage: consider <valid target>")
                return
            # check to ensure target inherits from character class
            if not utils.inherits_from(target, 'typeclasses.npcs.NPC') and \
               not utils.inherits_from(target, 'typeclasses.characters.Character') and \
               not utils.inherits_from(target, 'typeclasses.npcs.Humanoid_NPC'):
                self.caller.msg("You can only compare yourself to other character or NPCs.")
                log_file(f"Consider command failed. {target.name} checked as non \
                         character/non-NPC. type: {type(target)}", \
                         filename='error.log')
                return
        # get the info from the target of the command and compare it to caller
        conv_str = self.compare_values('force of your will', self.caller.traits.cp.current, \
                                  target.traits.cp.current)
        vigor_str = self.compare_values('vigor', self.caller.traits.hp.current + \
                                    self.caller.traits.sp.current, \
                                    target.traits.hp.current + \
                                    target.traits.sp.current,)
        mass_str = self.compare_values('mass', self.caller.traits.mass.current, \
                                  target.traits.mass.current)
        self.caller.execute_cmd(f"emote sizes up {target.name}.")
        self.caller.msg(f"\tThe |h|!W{conv_str}|n {target.name}'s.")
        self.caller.msg(f"\tYour |h|!W{vigor_str}|n {target.name}'s.")
        self.caller.msg(f"\tYour |h|!W{mass_str}|n {target.name}'s.")


    def compare_values(self, attribute_name, caller_attribute_value, target_attribute_value):
        # generic compare func. returns a text string
        compare_description = ''
        if caller_attribute_value > target_attribute_value * 5:
            compare_description = f"{attribute_name} is vastly superior to"
        elif caller_attribute_value > target_attribute_value * 2.5:
            compare_description = f"{attribute_name} is superior to"
        elif caller_attribute_value > target_attribute_value * 1.1:
            compare_description = f"{attribute_name} is greater than"
        elif caller_attribute_value * 5 < target_attribute_value:
            compare_description = f"{attribute_name} is vastly inferior to"
        elif caller_attribute_value * 2.5 < target_attribute_value:
            compare_description = f"{attribute_name} is inferior to"
        elif caller_attribute_value * 1.1 < target_attribute_value:
            compare_description = f"{attribute_name} is less than"
        else:
            compare_description = f"{attribute_name} is roughly the same as"
        return compare_description


class CmdStrike(Command):
    """
    Use the next combat action to try to do an unarmed strike.

    Usage:
        strike

    Aliases:
        unarmed

    """
    key = "strike"
    aliases = ['unarmed']
    help_category = "Combat"

    def func(self):
        "Implements the command"
        caller = self.caller
        self.caller.msg("You attempt to use unarmed strikes.")
        log_file(f"Attempting to add unarmed_strike to {self.caller.ndb.combat_handler} for {self.caller}",
                 filename='combat_step.log')
        self.caller.ndb.combat_handler.add_action("unarmed_strike", self.caller)


class CmdGrapple(Command):
    """
    Use the next combat action to try to do a grappling attack.
    If you are currently in a standing position, you'll try to clinch your
    opponent or take them down. If you're already in a grappling position,
    you'll do one of two actions: try to improve your position or attempt
    a submission until you reach an advantage. Once you're in an advantageous
    ground position, the grapple command occasionally does unarmed strikes as
    well. The position you are currently in greatly affects the chance of a
    successful submission and some unarmed strikes.

    Usage:
        grapple

    Aliases:
        grappling
        wrestle
        wrestling

    """
    key = "grapple"
    aliases = ['grappling', 'wrestle', 'wrestling']
    help_category = "Combat"

    def func(self):
        "Implements the command"
        caller = self.caller
        self.caller.msg("You attempt to grapple.")
        log_file(f"Attempting to add grapple to {self.caller.ndb.combat_handler} for {self.caller}",
                 filename='combat_step.log')
        self.caller.ndb.combat_handler.add_action("grapple", self.caller)


class CombatRelatedCmdSet(CmdSet):
    """
    Adds the set of commands a player or NPC object that are related to combat,
    but are available both inside and outside combat.
    """
    key = "combat_related_cmdset"
    mergetype = "Union" # we'll use this for now. Maybe we will use something else later
    priority = 10
    no_exits = False
    def at_cmdset_creation(self):
        self.add(CmdAttack())
        self.add(CmdConsider())
        self.add(CmdDefaultAttack())
        self.add(CmdTarget())



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
        self.add(CmdDisengage())
        self.add(CmdFlee())
        self.add(CmdYield())
        self.add(CmdDefend())
        self.add(CmdDefaultAttack())
        self.add(CmdTarget())
        self.add(CmdStrike())
        self.add(CmdGrapple())
