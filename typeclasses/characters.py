"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter
from evennia.utils import lazy_property
from world.equip import EquipHandler
from world.traits import TraitHandler
from world.dice_roller import return_a_roll_sans_crits as rarsc
from world import talents, mutations
from evennia.utils.logger import log_file


class Character(DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

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
        # clear traits, ability_scores, talents, and mutations
        self.ability_scores.clear()
        self.traits.clear()
        self.talents.clear()
        self.mutations.clear()
        # add in the ability scores
        self.ability_scores.add(key='Dex', name='Dexterity', type='static', \
                        base=rarsc(100))
        self.ability_scores.add(key='Str', name='Strength', type='static', \
                        base=rarsc(100))
        self.ability_scores.add(key='Vit', name='Vitality', type='static', \
                        base=rarsc(100))
        self.ability_scores.add(key='Per', name='Perception', type='static', \
                        base=rarsc(100))
        self.ability_scores.add(key='Cha', name='Charisma', type='static', \
                        base=rarsc(100))
        # add in traits for health, stamina, conviction, mass, encumberance
        self.traits.add(key="hp", name="Health Points", type="gauge", \
                        base=((self.ability_scores.Vit.current * 5) + \
                        (self.ability_scores.Cha.current * 2)))
        self.traits.add(key="sp", name="Stamina Points", type="gauge", \
                        base=((self.ability_scores.Vit.current * 3) + \
                        (self.ability_scores.Str.current * 2)+ \
                        (self.ability_scores.Dex.current)))
        self.traits.add(key="cp", name="Conviction Points", type="gauge", \
                        base=((self.ability_scores.Cha.current * 5) + \
                        (self.ability_scores.Vit.current)))
        self.traits.add(key="mass", name="Mass", type='static', \
                        base=rarsc(160, dist_shape='very flat'))
        self.traits.add(key="enc", name="Encumberance", type='static', \
                        base=0, max=(self.ability_scores.Str.current * .5))
        # apply the initial mutations and talents. Most mutations will be set
        # to zero, as will many talents
        talents.apply_talents(self)
        mutations.initialize_mutations(self)
        # set up intial equipment slots for the character. Since the character
        # is new and has no mutations, there won't be slots like tail or extra
        # arms
        self.db.limbs = ( ('head', ('head', 'face', 'ears', 'neck')), \
                          ('torso', ('chest', 'back', 'waist', 'quiver')), \
                          ('arms', ('shoulders', 'arms', 'hands', 'ring')), \
                          ('legs', ('legs', 'feet')), \
                          ('weapon', ('wield1', 'wield2')) )
        # define slots that go with the limbs.
        # TODO: Write a function for changing slots if/when mutations cause
        # new limbs to be grown or damage causes them to be lost
        self.db.slots = {
            'head': None,
            'face': None,
            'ears': None,
            'neck': None,
            'chest': None,
            'back': None,
            'waist': None,
            'quiver': None,
            'shoulders': None,
            'arms': None,
            'hands': None,
            'ring': None,
            'legs': None,
            'feet': None,
            'wield1': None,
            'wield2': None
        }
        # Add in info db to store other useful tidbits we'll need
        self.db.info = {'Target': None, 'Mercy': True, 'Default Attack': 'unarmed_strikes', \
                        'In Combat': False, 'Position': 'standing', \
                        'Wimpy': 100, 'Title': None}
        # money
        self.db.wallet = {'GC': 0, 'SC': 0, 'CC': 0}
        # TODO: Add in character sheet
        # TODO: Add in function for character sheet refresh
        # TODO: Add in progression script

    def calculate_encumberance(self):
        """
        This function will determine how encumbered the object is based upon
        carried weight and their strength. Encumberance will affect how much
        stamina it costs to move, fight, etc...

        Equipped items will not count against encumberance as much as 'loose'
        items in inventory. Certain containers and bags will also reduce
        encmberance.
        """
        items = self.contents
        self.traits.enc.current = 0
        self.traits.enc.max = self.ability_scores.Str.current * .5
        for item in items:
            if item.db.used_by == self:
                self.traits.enc.current += item.db.mass * .5
            else:
                self.traits.enc.current += item.db.mass
        self.ndb.enc_multiplier = (self.traits.enc.current / self.traits.enc.max) ** .3
        # also calulate total mass
        for item in items:
            self.traits.mass.mod = item.db.mass

    def at_attack_tick(self):
        """
        This function is called by the ticker created when combat
        was initiated. It will send the last attack command given
        to the world rules function for handling combat hit attempts
        It will default to "hit", the standard attack.
        """
        self.execute_cmd("rprom")
        if self.db.info['In Combat'] == True:
            log_file(f"{self.name} firing at_attack_tick func. Calling hit_attempt func from world.combat_rules", filename=self.ndb.combatlog_filename)
            hit_attempt(self, self.db.info['Target'], self.db.info['Default Attack'])
        else:
            ticker_id = str("attack_tick_%s" % self.name)
            tickerhandler.remove(interval=3, callback=self.at_attack_tick, idstring=ticker_id, persistent=False)
