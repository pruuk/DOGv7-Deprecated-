"""
Typeclass file for NPCs. Most NPCs will be some kind of subclass of NPC, but
spawning from class NPC is fine. Most of the attributes for NPC class will be
inherited from the characters.Character class, so if you are instantiating a
standard NPC, you should probably be planning on making a human NPC.
"""
# imports
from evennia import DefaultCharacter
from evennia.utils import lazy_property
from world.equip import EquipHandler
from world.traits import TraitHandler
from world.dice_roller import return_a_roll_sans_crits as rarsc
from world import talents, mutations


class Humanoid_NPC(Character):
    """
    Instantiates a NPC object. This base class should be primarily used for
    human and human-like NPCs. For animals and other NPC types, please use an
    appropriate subclass.
    """
    # pull in handlers for traits, equipment, mutations, talents
    @lazy_property
    def traits(self):
        """TraitHandler that manages character traits."""
        return TraitHandler(self)

    @lazy_property
    def ability_scores(self):
        """TraitHandler that manages character ability scores."""
        return TraitHandler(self, db_attribute='ability_scores')

    @lazy_property
    def talents(self):
        """TraitHandler that manages character talents."""
        return TraitHandler(self, db_attribute='talents')

    @lazy_property
    def mutations(self):
        """TraitHandler that manages character mutations."""
        return TraitHandler(self, db_attribute='mutations')

    @lazy_property
    def equip(self):
        """Handler for equipped items."""
        return EquipHandler(self)

    def at_object_creation(self):
        "Called only at object creation and with update command."
        super().at_object_creation()


    # Set of Behavior Functions. These will be called to have the NPCs "act" on
    # their own, performing actions like greeting players that enter a room,
    # patrolling an area, or attacking something that might be food
    def at_char_entered(self, character):
        """
        Execute a greeting if an NPC or character enters,
        after a short delay.
        """
        utils.delay(1, self.greetings)
        self.char = character


    def greetings(self):
        """
        Greets someone when they enter the room after a
        short delay.
        """
        # TODO: Expand this into friendly, neutral, and unfriendly greetings
        character = self.char
        dict_of_greetings = [
        f'say Greetings, {character}',
        f'say Good day, {character}',
        f'emote nods at {character} in greeting.',
        f'emote waves hello to {character}.',
        f"say I'm glad to see you, {character}."
        ]
        if self.name != self.char.name:
            self.execute_cmd(random.choice(dict_of_greetings))
        else:
            pass
