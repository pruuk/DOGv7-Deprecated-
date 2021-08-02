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
from world.combat_rules import resolve_combat_actions
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
                        base=rarsc(100), learn=0)
        self.ability_scores.add(key='Str', name='Strength', type='static', \
                        base=rarsc(100), learn=0)
        self.ability_scores.add(key='Vit', name='Vitality', type='static', \
                        base=rarsc(100), learn=0)
        self.ability_scores.add(key='Per', name='Perception', type='static', \
                        base=rarsc(100), learn=0)
        self.ability_scores.add(key='Cha', name='Charisma', type='static', \
                        base=rarsc(100), learn=0)
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
                        base=rarsc(180, dist_shape='very flat'))
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
                        'Wimpy': 100, 'Yield': 200, 'Title': None}
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
        for item in items:
            if item.db.used_by == self:
                self.traits.enc.current += item.db.mass * .5
            else:
                self.traits.enc.current += item.db.mass
        if self.traits.enc.current == 0:
            self.ndb.enc_mod = 1
        else:
            self.ndb.enc_mod = ((self.traits.enc.current / self.traits.enc.max) ** .15)
        # also calulate total mass
        for item in items:
            self.traits.mass.mod = item.db.mass


    def calc_combat_modifiers(self):
        """
        Rerun all the calculations for combat modifiers and store them as temp
        variables on the character.
        """
        self.calculate_encumberance()
        # modifiers for health/stamina/conviction
        self.ndb.hp_mod = ((self.traits.hp.current / self.traits.hp.max) ** .15)
        self.ndb.sp_mod = ((self.traits.sp.current / self.traits.sp.max) ** .15)
        self.ndb.cp_mod = ((self.traits.cp.current / self.traits.cp.max) ** .15)


    def calc_position_modifier(self):
        """
        Recalculate current modifier for position for combat actions.
        """
        position = self.db.info['Position']
        # ground positions listed from best to worst
        if position == 'tbmount': # mounted opponent and taken their back
            self.ndb.position_mod = 1.5
        elif position == "mount": # mounted opponent, facing them
            self.ndb.position_mod = 1.4
        elif position == "side control": # on top, have side control
            self.ndb.position_mod = 1.2
        elif position == "top": # on top, in their guard
            self.ndb.position_mod = 1.05
        elif position == "in guard": # on bottom, in your guard
            self.ndb.position_mod = .95
        elif position == "side controlled": # on bottom, being side controlled
            self.ndb.position_mod = .85
        elif position == "mounted": # on bottom, mounted
            self.ndb.position_mod = .75
        elif position == "prmounted": # on bottom, face down, back taken
            self.ndb.position_mod = .5
        # standing grappling positions from best to worst
        elif position == "tbstanding": # riding opponent from behind, they're standing
            self.ndb.position_mod = 1.25
        elif position == "clinching": # both standing, you have them in a clinch
            self.ndb.position_mod = 1.05
        elif position == "clinched": # both standing, they have you in a clinch
            self.ndb.position_mod = .95
        elif position == "standingbt": # opponent has taken your back, you're standing
            self.ndb.position_mod = .85
        # non grappling positions, normal
        elif position == "standing":
            self.ndb.position_mod = 1
        elif position == "sitting":
            self.ndb.position_mod = .9
        elif position == "supine":
            self.ndb.position_mod = .85
        elif position == "prone":
            self.ndb.position_mod = .8
        elif position == "sleeping":
            self.ndb.position_mod = .5
        # other environmentally dependant positions
        elif position == "floating": # floating in air or water, limited control
            self.ndb.position_mod = 1
        elif position == "flying": # flying through air under your own power
            self.ndb.position_mod = 1.25
        # all other cases, log an error
        else:
            self.ndb.position_mod = 1
            logger.log_trace("Unknown character position. Check the code for \
                              typeclasses.characters.Character.calc_position_modifier()")


    def check_wimpyield(self):
        """
        Check if character has fallen below their wimpy or yield thresholds. If
        they have, change next combat action to the appropriate action.
        """
        # TODO: Remove these emotes once we've moved the flee/yield to
        # commands
        if self.traits.hp.current <= self.db.info['Wimpy']:
            if len(self.ndb.next_combat_action) > 0:
                self.ndb.next_combat_action.insert(0, 'flee')
            else:
                self.ndb.next_combat_action = ['flee']
            self.execute_cmd("emote is severely wounded and tries to flee.")
        elif self.traits.hp.current <= self.db.info['Yield']:
            if len(self.ndb.next_combat_action) > 0:
                self.ndb.next_combat_action.insert(0, 'yield')
            else:
                self.ndb.next_combat_action = ['yield']
            # self.execute_cmd("emote is heavily wounded and tries to yield.")
        elif self.traits.sp.current <= self.db.info['Wimpy']:
            if len(self.ndb.next_combat_action) > 0:
                self.ndb.next_combat_action.insert(0, 'flee')
            else:
                self.ndb.next_combat_action = ['flee']
            self.execute_cmd("emote is severely exhausted and tries to flee.")
        elif self.traits.sp.current <= self.db.info['Yield']:
            if len(self.ndb.next_combat_action) > 0:
                self.ndb.next_combat_action.insert(0, 'yield')
            else:
                self.ndb.next_combat_action = ['yield']
            # self.execute_cmd("emote is exhausted and tries to yield.")
        elif self.traits.hp.current <= self.db.info['Wimpy']:
            if len(self.ndb.next_combat_action) > 0:
                self.ndb.next_combat_action.insert(0, 'flee')
            else:
                self.ndb.next_combat_action = ['flee']
            self.execute_cmd("emote has zero will to fight and tries to flee.")
        elif self.traits.hp.current <= self.db.info['Yield']:
            if len(self.ndb.next_combat_action) > 0:
                self.ndb.next_combat_action.insert(0, 'yield')
            else:
                self.ndb.next_combat_action = ['yield']
            # self.execute_cmd("emote has no will to fight and tries to yield.")
        else:
            # adding a debugging line to see if we're getting to here.
            # self.execute_cmd("emote is still in fighting shape and spirit.")
            pass


    def at_attack_tick(self):
        """
        This function is called by the ticker created when combat
        was initiated. It will send the last attack command given
        to the world rules function for handling combat hit attempts
        It will default to "hit", the standard attack.
        """
        self.execute_cmd("rprom")
        if self.db.info['In Combat'] == True and self.db.info['Target'] is not None:
            log_file(f"{self.name} firing at_attack_tick func. Calling hit_attempt func from world.combat_rules", filename=self.ndb.combatlog_filename)
            # self.execute_cmd(f"emote is attacking {self.db.info['Target'].name}")
            if len(self.ndb.next_combat_action) > 0:
                resolve_combat_actions(self, self.db.info['Target'])
            else:
                resolve_combat_actions(self, self.db.info['Target'])
        else:
            ticker_id = str("attack_tick_%s" % self.name)
            tickerhandler.remove(interval=4, callback=self.at_attack_tick, idstring=ticker_id, persistent=False)
            self.db.ndb.next_combat_action = []
