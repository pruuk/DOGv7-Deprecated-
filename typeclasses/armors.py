"""
Armor typeclasses

These are the subclasses of equippable items intended to protect from damage
from attacks by other beings.

The code is mostly copied from:
https://github.com/evennia/ainneve/blob/master/typeclasses/armors.py

"""
from typeclasses.items import Equippable
from world.traits import TraitHandler

class Armor(Equippable):
    """
    Typeclass for armor objects.
    Attributes:
        physical_armor_value (int): primary defensive stat for physical hits
        mental_armor_value (int): primary defensive stat for mental hits

    """
    toughness = 0
    slots = [] # slot will need to be added at object creation
    mass = 3

    def at_object_creation(self):
        super(Armor, self).at_object_creation()
        self.db.physical_armor_value = 1 # default value
        self.db.mental_armor_value = 0 # default value

    def at_equip(self, character):
        pass

    def at_remove(self, character):
        pass

class Shield(Armor):
    """Typeclass for shield prototypes."""
    slots = ['wield1', 'wield2']
    multi_slot = False
    mass = 8


class Hat(Armor):
    "subtype to be worn on head"
    slots = ['head']
    multi_slot = False


class Helmet(Armor):
    "subtype to be worn on head"
    slots = ['head', 'face', 'ears', 'neck']
    multi_slot = True
    mass = 5


class Mask(Armor):
    "subtype to be worn on face"
    slots = ['face']
    multi_slot = False


class Earrings(Armor):
    "subtype to be worn on ears"
    slots = ['ears']
    multi_slot = False


class Neck(Armor):
    """subtype to be worn on neck. Includes necklaces, torques, etc."""
    slots = ['neck']
    multi_slot = False


class Vest(Armor):
    """subtype to be worn on chest."""
    slots = ['chest']
    multi_slot = False
    mass = 5


class Chestplate(Armor):
    """subtype to be worn on chest, shoulders, and arms. Lighter armor"""
    slots = ['chest', 'shoulders', 'armors']
    multi_slot = True
    mass = 10


class FullBodyArmor(Armor):
    """subtype that is a full suit of armor. Usually heavy armor"""
    slots = ['head', 'face', 'ears', 'neck', 'chest', 'waist', 'shoulders', \
             'arms', 'hands', 'legs', 'feet']
    multi_slot = True
    mass = 35


class Back(Armor):
    "subtype to be worn on back. Includes capes, backpacks, and cloaks"
    slots = ['back']
    multi_slot = False


class Quiver(Armor):
    """subtype to be worn as quiver to hold ammo"""
    slots = ['quiver']
    multi_slot = False
    mass = 2


class Belt(Armor):
    """subtype to be worn around the waist."""
    slots = ['waist']
    multi_slot = False
    mass = 2


class Glove(Armor):
    """subtype to be worn on hands."""
    slots = ['hands']
    multi_slot = False
    mass = 1


class Gauntlets(Armor):
    """subtype to be worn on hands. prevents wearing rings"""
    slots = ['hands', 'ring']
    multi_slot = True
    mass = 3


class Ring(Armor):
    """subtype to be worn on fingers."""
    slots = ['ring']
    multi_slot = False


class Legs(Armor):
    """subtype to be worn on legs. Includes pants."""
    slots = ['legs']
    multi_slot = False
    mass = 3


class Feet(Armor):
    """subtype to be worn on feet. Includes boots, shoes, etc"""
    slots = ['feet']
    multi_slot = False
    mass = 2


class Greaves(Armor):
    """subtype to be worn on legs and feet."""
    slots = ['legs', 'feet']
    multi_slot = True
    mass = 5
