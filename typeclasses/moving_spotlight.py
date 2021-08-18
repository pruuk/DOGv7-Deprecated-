# -*- coding: utf-8 -*-
"""
The moving spotlight script is intended to force the 'tick' of time as NOW moves
forward toward the future. In practical terms, this script will trigger a
number of actions related to the passage of time for game objects in DOG,
including:
- Character/NPC progression (learning new skills, mutating new powers, etc)
- Object progression (objects acquiring new attributes & powers based upon
  events that the object was involved in)
- Character/NPC aging
- Weather and weather events
- The movement of celestial bodies. In particular tracking the movement of the
  three moons around Gaius and the game modifiers the moon phases enable
- Character/NPC regen of health, stamina, and conviction pools
- Object decay for things like food items
- Natural disasters like volcanoes, floods, wildfires
"""
import random
from evennia import DefaultScript
from evennia.utils.logger import log_file


# superclass
class MovingSpotlightTick(DefaultScript):
    """
    Master global script for tracking the global 'heartbeat' of the DOG MUD.
    All other objects that are affected by the passage of time will have their
    time related functions called by this script.

    Please use a subclass of this abstract class based upon the object type.
    """
    def at_script_creation(self):
            self.key = 'moving_spotlight_heartbeat'
            self.desc = "Triggers all time related events in DOG"
            self.interval = 60 # 60 second timeout # TODO: Tune this later
            self.persistent = True # will survive reload

    def at_repeat(self):
        "called every self.interval seconds."
        pass

# subclass for characters and NPCs
class MovingSpotlightTickCharacter(MovingSpotlightTick):
    """
    Subclass of time ticker script to be attached to characters or NPC at
    the time of their creation (or if they are updated).
    """
    def at_repeat(self):
        "called every self.interval seconds."
        # call regen func
        self.obj.at_heartbeat_tick_regen_me()
        # call progression func
        self.obj.at_heartbeat_tick_do_progression_checks()
