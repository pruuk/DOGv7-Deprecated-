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
from typeclasses.characters import Character
from evennia import utils
import random


class NPC(Character):
    """
    Superclass for NPCs. While this can be used, it is better to use a subclass.
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

    # allow builders to set a base power for the scores to be rolled around
    def set_base_power(self, base_power_number):
        """
        This function allows for a developer/builder to easily set the base
        starting stats for a given NPC. The base_power_number number passed in
        will be the number sent to the roller for stats. Average human is set at
        100 (and player characters are rolled with a base power of 100). Thus
        passing in 120 would, on average, make this NPC 2 standard deviations
        better at every stat than a starting player.
        """
        # clear traits, ability_scores, talents, and mutations
        self.ability_scores.clear()
        self.traits.clear()
        self.talents.clear()
        self.mutations.clear()
        self.ability_scores.add(key='Dex', name='Dexterity', type='static', \
                        base=rarsc(base_power_number), extra={'learn' : 0})
        self.ability_scores.add(key='Str', name='Strength', type='static', \
                        base=rarsc(base_power_number), extra={'learn' : 0})
        self.ability_scores.add(key='Vit', name='Vitality', type='static', \
                        base=rarsc(base_power_number), extra={'learn' : 0})
        self.ability_scores.add(key='Per', name='Perception', type='static', \
                        base=rarsc(base_power_number), extra={'learn' : 0})
        self.ability_scores.add(key='Cha', name='Charisma', type='static', \
                        base=rarsc(base_power_number), extra={'learn' : 0})
        self.traits.add(key="hp", name="Health Points", type="gauge", \
                        base=((self.ability_scores.Vit.current * 5) + \
                        (self.ability_scores.Cha.current * 2)), extra={'learn' : 0})
        self.traits.add(key="sp", name="Stamina Points", type="gauge", \
                        base=((self.ability_scores.Vit.current * 3) + \
                        (self.ability_scores.Str.current * 2)+ \
                        (self.ability_scores.Dex.current)), extra={'learn' : 0})
        self.traits.add(key="cp", name="Conviction Points", type="gauge", \
                        base=((self.ability_scores.Cha.current * 5) + \
                        (self.ability_scores.Vit.current)), extra={'learn' : 0})
        self.traits.add(key="mass", name="Mass", type='static', \
                        base=rarsc(180, dist_shape='very flat'), extra={'learn' : 0})
        self.traits.add(key="enc", name="Encumberance", type='static', \
                        base=0, max=(self.ability_scores.Str.current * .5), extra={'learn' : 0})
        # apply the initial mutations and talents. Most mutations will be set
        # to zero, as will many talents
        talents.apply_talents(self)
        mutations.initialize_mutations(self)


    def set_an_ability_score(self, ability_name, base_power_number):
        """
        This function allows for a developer/builder to easily set the base
        starting stat for a given NPC for a given ability. The base_power_number
        passed in will be the number sent to the roller for stats. Average human
        is set at 100 (and player characters are rolled with a base power of
        100). Thus passing in 120 would, on average, make this NPC 2 standard
        deviations better at every stat than a starting player.
        """
        # check if the ability score name passed in is valid
        if ability_name in ('Strength', 'Dexterity', 'Vitality', 'Perception',\
                            'Charisma'):
            self.db.ability_scores[ability_name].base = (rarsc(base_power_number))


    # Set of Behavior Functions. These will be called to have the NPCs "act" on
    # their own, performing actions like greeting players that enter a room,
    # patrolling an area, or attacking something that might be food
    def at_char_entered(self, character):
        """
        Execute a greeting if an NPC or character enters,
        after a short delay.
        """
        utils.delay(2, self.greetings(character))


    def greetings(self, character):
        """
        Greets someone when they enter the room after a
        short delay.
        """
        # TODO: Expand this into friendly, neutral, and unfriendly greetings
        dict_of_greetings = [
        f'say Greetings, {character}',
        f'say Good day, {character}',
        f'emote nods at {character} in greeting.',
        f'emote waves hello to {character}.',
        f"say I'm glad to see you, {character}."
        ]
        if self.name != character.name:
            self.execute_cmd(random.choice(dict_of_greetings))
        else:
            pass


class Humanoid_NPC(NPC):
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
