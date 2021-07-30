"""
Generic item classes and their base functions.
"""

from typeclasses.objects import Object
from evennia import create_object
from evennia.prototypes.spawner import spawn
from world.traits import TraitHandler

class Item(Object):
    """
    Typeclass for Items.
    Attributes:
        value (int): monetary value of the item in CC
        weight (float): weight of the item
    """
    value = 1 # default value in copper coins
    mass = 0.5 # default mass in kilograms

    def at_object_creation(self):
        "Only called at creation and forced update"
        super(Item, self).at_object_creation()
        self.locks.add(";".join(("puppet:perm(Builder)",
                                 "equip:false()",
                                 "get:true()"
                                 )))
        self.db.value = self.value
        self.db.mass = float(self.mass)
        self.db.hp = 10 #default for objects

    def at_before_move(self, getter):
        """
        Called when a character or NPC tries to get the item. Checks to see if
        adding this amount of weight will make the character/NPC overencumbered.
        """
        if getter.traits.enc.current + self.db.mass > getter.traits.enc.max:
            # this item is too heavy for the getter to pick up, cancel move
            getter.msg(f"{self.name} is too heavy for you to pick up.")
            return False
        else:
            getter.calculate_encumberance()

    def at_get(self, getter):
        "Called just after getter picks up the object"
        getter.calculate_encumberance()

    def at_drop(self, dropper):
        "Called just after dropper drops this object"
        dropper.calculate_encumberance()


class Bundable(Item):
    """
    Items that can be bundled together as stored as a single object to make it
    easier on the db infra.
    """
    def at_object_creation(self):
        "Only called at creation and forced update"
        super(Bundlable, self).at_object_creation()
        self.db.bundle_size = 999
        self.db.prototype_name = None

    # TODO: Add in function for at_get and at_drop that includes bundling


class Bundle(Item):
    """Typeclass for bundles of Items."""
    def expand(self):
        """Expands a bundle into its component items."""
        for i in list(range(self.db.quantity)):
            p = self.db.prototype_name
            spawn(dict(prototype=p, location=self.location))
        self.delete()


class Equippable(Item):
    """
    Typeclass for equippable Items.
    Attributes:
        slots (str, list[str]): list of slots for equipping
        multi_slot (bool): operator for multiple slots. False equips to
            first available slot; True requires all listed slots available.
    """
    slots = None
    multi_slot = False

    def at_object_creation(self):
        "Only called at creation and forced update"
        super(Equippable, self).at_object_creation()
        self.locks.add("puppet:false();equip:true()")
        self.db.slots = self.slots
        self.db.multi_slot = self.multi_slot
        self.db.used_by = None

    def at_equip(self, character):
        """
        Hook called when an object is equipped by character.
        Args:
            character: the character equipping this object
        """
        pass

    def at_remove(self, character):
        """
        Hook called when an object is removed from character equip.
        Args:
            character: the character removing this object
        """
        pass

    def at_drop(self, dropper):
        super(Equippable, self).at_drop(dropper)
        if self in dropper.equip:
            dropper.equip.remove(self)
            self.at_remove(dropper)
