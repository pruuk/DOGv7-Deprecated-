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
    slots = ['main hand', 'off hand']
    multi_slot = False

    damage = 1.1 # this is a multiplier!
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
    slots = ['main hand', 'off hand']
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
class Sword(Weapon):
    """
    Subclass for sword weapon objects.
    Attributes:
        damage (int): primary attack stat
        handedness (int): indicates single- or double-handed weapon
    """
    slots = ['main hand', 'off hand']
    multi_slot = False

    damage = 1.1 # this is a multiplier!
    handedness = 1
    range = 'melee'

    def at_object_creation(self):
        super(Weapon, self).at_object_creation()
        self.db.range = self.range
        self.db.damage = self.damage
        self.db.handedness = self.handedness
        self.db.combat_cmdset = 'commands.combat.MeleeWeaponCmdSet'
        self.db.combat_descriptions = {
        'hit': {
        'self': [
        "tentatively swing at",
        "swing shakily at",
        "barely avoid cutting yourself with {weapon}, but land an off-balance slash on",
        "nearly behead yourself, but land a slash on",
        "wildly swing your {weapon} at",
        "stumble and fall forward, {weapon} extended at",
        "manage to not cut off your own fingers swinging {weapon} at",
        "spin in a circle, loopily swinging {weapon} at",
        "drop {weapon}, picking it up in time to slash at",
        "confuse the business end of {weapon} with the handle, landing a lucky handle strike on",
        "step to the left, then stumble into a swing with {weapon} at",
        "almost drop {weapon} with a clumsy slash at",
        "akwardly swing {weapon} at",
        "execute a series of practiced attacks at air before sheepishly slashing at",
        "move mechanically through an attack at",
        "try a move that just doesn't makes sense, but hits anyway on",
        "try an attack, accidently slash on a backswing on",
        "execute a moderatly competent swing of {weapon} at",
        "are a bit off-balance, but recover well with a slash at",
        "do a simple attack, but do it well at",
        "rush forward, wasting a lot of effort to swing at",
        "land a series of formulatic swings at",
        "run past and slash backward at",
        "settle into a low stance and swing horizontally at",
        "hold your {weapon} perfectly still overhead before swiftly attacking downward at",
        "lunge forward to land a swift slash at",
        "switcs into a new stance while slashing at",
        "move through a series of standard attacks, then slashes at",
        "land with a nifty jump-kick and slash combo at",
        "lean to the right, then slashes backwards at",
        "smoothly slide to the side, swinging your {weapon} in a tight arc at",
        "use the handle of {weapon} to deflect an attack and ripostes at",
        "counter an attack with a wrist flick at",
        "duck under an attack and swing horizontally at",
        "do a cartwheel while slashing in a wide arc at",
        "barely seem to exert effort while moving through a blindly fast flurry of attacks at",
        "extend {weapon} and slash with a quick wrist flick at",
        "move so swiftly you register your reflexive the slash at",
        "use the momentum of a previous attack to land a new attack on",
        "flow like water into a jumping slash at",
        "show an ecoonomy of movement, then land a masterful attack at",
        "flick the end of {weapon} out at",
        "backflip in a one-handed handstand while slashing at",
        "slash with your {weapon} at",
        "swing your {weapon} downward at",
        "swing your {weapon} horizontally at",
        "shuffle right to make room for an uppercut slash with your {weapon} at",
        "step left to make room for an uppercut slash with your {weapon} at",
        "land a shaky thrust at",
        "clumsily push the end of your {weapon} into",
        "poke forward with your {weapon} at",
        "dances around uselessly as a distraction, then thrust {weapon} at",
        "steps forward and put your weight into a thrust at",
        "reverse your grip on your {weapon}, thrusting the tip at",
        "land a vicious thrust at",
        "never pause as you flow through a flurry of attacks ending with a downward thrust at",
        "thrust your {weapon} at",
        "use your {weapon} to pierce",
        ],
        'others': [
        "tentatively swings their {weapon} at",
        "swings their {weapon} shakily at",
        "barely avoids cutting themselves with {weapon}, but lands an off-balance slash on",
        "nearly beheads themselves, but lands a slash on",
        "wildly swings their {weapon} at",
        "stumbles and falls forward, {weapon} extended at",
        "manages to not cut off their own fingers swinging {weapon} at",
        "spins in a circle, loopily swinging {weapon} at",
        "drops {weapon}, picking it up in time to slash at",
        "confuses the business end of {weapon} with the handle, landing a lucky handle strike on"
        "steps to the left, then stumbles into a swing with {weapon} at",
        "almost drops {weapon} with a clumsy slash at",
        "akwardly swings {weapon} at",
        "executes a series of practiced attacks at air before sheepishly slashing at",
        "moves mechanically through an attack at",
        "tries a move that just doesn't makes sense, but hits anyway on",
        "tries an attack, accidently slashes on the backswing on"
        "executes a moderatly competent swing of {weapon} at",
        "is a bit off-balance, but recovers well with a slash at",
        "does a simple attack, but does it well at",
        "rushes forward, wasting a lot of effort to swing at",
        "lands a series of formulatic swings at",
        "runs past and slashes backward at",
        "settles into a low stance and swings {weapon} horizontally at"
        "holds their {weapon} perfectly still overhead before swiftly attacking downward at",
        "lunges forward to land a swift slash at",
        "switches into a new stance while slashing at",
        "moves through a series of standard attacks, then slashes at",
        "lands with a nifty jump-kick and slash combo at",
        "leans to the right, then slashes backwards at"
        "smoothly slides to the side, swinging their {weapon} in a tight arc at",
        "uses the handle of {weapon} to deflect an attack and ripostes at",
        "counters an attack with a wrist flick at",
        "ducks under an attack and swings horizontally at",
        "does a cartwheel while slashing in a wide arc at"
        "barely seems to exert effort while a blindly fast flurry of attacks at",
        "extends {weapon} and slashes with a quick wrist flick at",
        "moves so swiftly you barely see the slash at",
        "uses the momentum of a previous attack to land a new attack on",
        "flows like water into a jumping slash at",
        "shows an ecoonomy of movement, but lands a masterful attack at",
        "flicks the end of {weapon} out at their exposed",
        "backflips in a one-handed handstand while slashing at"
        "slashes with their {weapon} at",
        "swings their {weapon} downward at",
        "swings their {weapon} horizontally at",
        "shuffles right to make room for an uppercut slash with their {weapon} at",
        "steps left to make room for an uppercut slash with their {weapon} at",
        "lands a shaky thrust at",
        "clumsily pushes the end of their {weapon} into"
        "pokes forward with their {weapon} at",
        "dances around uselessly as a distraction, then thrusts {weapon} at"
        "steps forward and puts their weight into a thrust at"
        "reverses their grip on their {weapon}, thrusting the tip at"
        "lands a vicious thrust at"
        "never pauses as they flow through a flurry of attacks ending with a downward thrust at"
        "thrusts their {weapon} at",
        "uses their {weapon} to pierce",
        ],
        },
        'killing_blow' : {
        'self': [
        "decapitate",
        "behead",
        "slip your weapon between the ribs of",
        "gouge the eyes out of",
        ],
        'others': [
        "decapitates",
        "beheads",
        "slips their weapon between the ribs of",
        "gouges the eyes out of",
        ],
        },
        }

    def at_equip(self, character):
        pass

    def at_remove(self, character):
        pass

## TODO: Same as above, for ranged weapons
