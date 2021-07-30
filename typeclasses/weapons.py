"""
Weapon typeclasses.

These are a subtype of item that are intended to be used as a weapon to harm
other beings. Many normal items can be used as weapons, but with far less
effectiveness as a regular weapon.

Most of this code is copied from Ainneve mud:
https://github.com/evennia/ainneve/blob/master/typeclasses/weapons.py

"""
from typeclasses.items import Equippable

class Weapon(Equippable):
    """
    Typeclass for weapon objects.
    Attributes:
        damage (int): primary attack stat
        handedness (int): indicates single- or double-handed weapon
    """
    slots = ['wield1', 'wield2']
    multi_slot = False

    damage = 0
    handedness = 1
    range = 'melee'

    def at_object_creation(self):
        super(Weapon, self).at_object_creation()
        self.db.range = self.range
        self.db.damage = self.damage
        self.db.handedness = self.handedness
        self.db.combat_cmdset = 'commands.combat.MeleeWeaponCmdSet'
        self.db.combat_descriptions = {
        'hit': "hits for",
        'miss': "misses",
        'dodged': 'attacks, but is dodged by',
        'blocked': 'attacks, but is blocked by'
        }

    def at_equip(self, character):
        pass

    def at_remove(self, character):
        pass

class RangedWeapon(Weapon):
    """
    Typeclass for thrown and single-handed ranged weapon objects.
    Attributes:
        range (int): range of weapon in (units?)
        ammunition Optional(str): type of ammunition used (thrown if None)
    """
    range = 'ranged'
    ammunition = None

    def at_object_creation(self):
        super(RangedWeapon, self).at_object_creation()
        self.db.ammunition = self.ammunition
        self.db.combat_cmdset = 'commands.combat.RangedWeaponCmdSet'

    def at_equip(self, character):
        pass

    def at_remove(self, character):
        pass

    def get_ammunition_to_fire(self):
        """Checks whether there is proper ammunition and returns one unit."""
        ammunition = [obj for obj in self.location.contents
                      if (obj.is_typeclass('typeclasses.items.Bundlable')
                          or obj.is_typeclass('typeclasses.weapons.RangedWeapon'))
                      and self.db.ammunition in obj.aliases.all()]

        if not ammunition:
            # no individual ammo found, search for bundle
            bundle = [obj for obj in self.location.contents
                      if "bundle {}".format(self.db.ammunition)
                          in obj.aliases.all()
                      and obj.is_typeclass('typeclasses.items.Bundle')]

            if bundle:
                bundle = bundle[0]
                bundle.expand()
                return self.get_ammunition_to_fire()
            else:
                return None
        else:
            return ammunition[0]


class TwoHanded(object):
    """Mixin class for two handed weapons."""
    slots = ['wield1', 'wield2']
    multi_slot = True
    handedness = 2


class TwoHandedWeapon(TwoHanded, Weapon):
    """Typeclass for two-handed melee weapons."""
    pass


class TwoHandedRanged(TwoHanded, RangedWeapon):
    """Typeclass for two-handed ranged weapons."""
    pass


## TODO: Add in subclasses of melee weapons and reference a file with cooler
## combat descriptions that can be pulled in to make attacks more interesting
## TODO: Same as above, for ranged weapons
