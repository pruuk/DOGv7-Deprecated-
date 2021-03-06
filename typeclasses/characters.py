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
from world.dice_roller import return_a_roll as roll
from world.dice_roller import return_a_roll_sans_crits as rarsc
from world import talents, mutations
from world.progression_rules import control_progression_funcs
from evennia.utils.logger import log_file
from evennia import gametime
from evennia import create_script
from evennia.utils import evform, evtable


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
                        base=rarsc(100), extra={'learn' : 0})
        self.ability_scores.add(key='Str', name='Strength', type='static', \
                        base=rarsc(100), extra={'learn' : 0})
        self.ability_scores.add(key='Vit', name='Vitality', type='static', \
                        base=rarsc(100), extra={'learn' : 0})
        self.ability_scores.add(key='Per', name='Perception', type='static', \
                        base=rarsc(100), extra={'learn' : 0})
        self.ability_scores.add(key='Cha', name='Charisma', type='static', \
                        base=rarsc(100), extra={'learn' : 0})
        # add in traits for health, stamina, conviction, mass, encumberance
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
        self.traits.add(key="enc", name="Encumberance", type='counter', \
                        base=0, max=(self.ability_scores.Str.current * .5), extra={'learn' : 0})
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
                          ('weapon', ('main hand', 'off hand')) )
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
            'main hand': None,
            'off hand': None
        }
        # Add in info db to store other useful tidbits we'll need
        self.db.info = {'Target': None, 'Mercy': True, 'Default Attack': 'unarmed_strike', \
                        'In Combat': False, 'Position': 'standing', 'Sneaking' : False, \
                        'Wimpy': 100, 'Yield': 200, 'Title': None}
        # money
        self.db.wallet = {'GC': 0, 'SC': 0, 'CC': 0}
        # TODO: Add in character sheet
        # TODO: Add in function for character sheet refresh
        self.db.moving_spotlight_heartbeat = create_script("typeclasses.moving_spotlight.MovingSpotlightTickCharacter", obj=self)
        # we will use this to stop account from changing sheet
        self.db.sheet_locked = False
        self.db.charsheet = evform.EvForm("world/charsheetform.py")
        self.update_character_sheet()


    def calculate_encumberance(self):
        """
        This function will determine how encumbered the object is based upon
        carried weight and their strength. Encumberance will affect how much
        stamina it costs to move, fight, etc...

        Equipped items will not count against encumberance as much as 'loose'
        items in inventory. Certain containers and bags will also reduce
        encmberance.
        """
        log_file(f"start of status encumberance calc func for {self.name}", \
                 filename='combat_step.log')
        self.traits.enc.current = 0
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


    def calc_status_modifiers(self):
        """
        Rerun all the calculations for combat modifiers and store them as temp
        variables on the character.
        """
        log_file(f"start of status modifiers calc func for {self.name}", \
                 filename='combat_step.log')
        # modifiers for health/stamina/conviction
        self.ndb.hp_mod = ((self.traits.hp.current / self.traits.hp.max) ** .15)
        self.ndb.sp_mod = ((self.traits.sp.current / self.traits.sp.max) ** .15)
        self.ndb.cp_mod = ((self.traits.cp.current / self.traits.cp.max) ** .15)
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


    def calc_footwork_and_groundwork_mods(self):
        """
        Runs calculations for footwork and groundwork rolls at the start of
        combat round and applies these to a temp variable on self.
        """
        # checks to ensure temp vars we need have been set. If not, run calcs
        log_file(f"start of foot/groundwork calc func for {self.name}", \
                 filename='combat_step.log')
        # calc groundwork ratio
        groundwork_dice = (self.talents.grappling.actual + \
                           self.traits.mass.actual) * \
                           self.ndb.position_mod * \
                           self.ndb.hp_mod * \
                           self.ndb.sp_mod * self.ndb.cp_mod * \
                           self.ndb.enc_mod
        self.ndb.groundwork_mod = (roll(groundwork_dice, 'flat', \
                                  self.ability_scores.Dex, \
                                  self.talents.grappling)) / 250
        # calc footwork ratio
        footwork_dice = self.talents.footwork.actual * \
                        self.ndb.position_mod * self.ndb.hp_mod * \
                        self.ndb.sp_mod * self.ndb.cp_mod * \
                        self.ndb.enc_mod
        self.ndb.footwork_mod = (roll(footwork_dice, 'flat', \
                                self.ability_scores.Dex, \
                                self.talents.footwork)) / 100


    def calculate_equipment_bonuses(self):
        """
        Runs calculations for bonuses due to equipped items.
        """
        self.ndb.eq_damage = 1
        self.ndb.eq_phy_arm = 1
        self.ndb.eq_men_arm = 1
        for slot, item in self.db.slots.items():
            if item != None:
                if item.attributes.has('physical_armor_value'):
                    self.ndb.eq_phy_arm *= item.db.physical_armor_value
                if item.attributes.has('mental_armor_value'):
                    self.ndb.eq_men_arm *= item.db.mental_armor_value
                if item.attributes.has('damage'):
                    self.ndb.eq_damage *= item.db.damage


    def populate_num_combat_actions(self):
        """
        Rolls to determine the number of actions the character can perform during
        this round of combat.
        """
        log_file(f"start of num of combat actions function for {self.name}.", \
                 filename='combat_step.log')
        # listing out modifiers for readbility
        actions_roll = ((self.ability_scores.Dex.actual + \
                         self.ability_scores.Vit.actual) * \
                         self.ndb.enc_mod)
        log_file(f"{self.name} rolling {actions_roll} for actions. This \
                 will be divided by 100 and then rounded.", filename='combat_step.log')
        self.ndb.num_of_actions = round((roll(actions_roll, 'very flat', \
                                       self.ability_scores.Dex, \
                                       self.ability_scores.Vit)) / 100)
        log_file(f"{self.name} gets {self.ndb.num_of_actions} actions.", \
                 filename='combat.log')


    def check_wimpyield(self):
        """
        Check if character has fallen below their wimpy or yield thresholds. If
        they have, change next combat action to the appropriate action.
        """
        log_file(f"start of wimpy/yield check for {self.name}.", filename='combat_step.log')
        if self.traits.hp.current <= self.db.info['Wimpy']:
            self.execute_cmd('flee')
            log_file(f"{self.name} is fleeing (hps).", filename='combat.log')
        elif self.traits.hp.current <= self.db.info['Yield']:
            self.execute_cmd('yield')
            log_file(f"{self.name} is yielding (hps).", filename='combat.log')
        elif self.traits.sp.current <= self.db.info['Wimpy']:
            self.execute_cmd('flee')
            log_file(f"{self.name} is fleeing(sps).", filename='combat.log')
        elif self.traits.sp.current <= self.db.info['Yield']:
            self.execute_cmd('yield')
            log_file(f"{self.name} is yielding (sps).", filename='combat.log')
        elif self.traits.hp.current <= self.db.info['Wimpy']:
            self.execute_cmd('flee')
            log_file(f"{self.name} is fleeing(cps).", filename='combat.log')
        elif self.traits.hp.current <= self.db.info['Yield']:
            self.execute_cmd('yield')
            log_file(f"{self.name} is yielding (cps).", filename='combat.log')
        else:
            log_file(f"{self.name} is not fleeing or yielding.", filename='combat_step.log')


    def at_heartbeat_tick_regen_me(self):
        """
        This function will be fired off at the heartbeat tick of the global
        MovingSpotlightTick script. It will determine randomly how much health,
        stamina, and conviction to regen at that tick. Being in combat will
        reduce regen. Other factors that influence regen are ability scores,
        mutations, and the phases of the three moons.
        """
        log_file(f"start of regen tick function for {self.name}.", \
                 filename='time_tick.log')
        # first, check if we're in combat
        if self.db.info['In Combat']:
            combat_mod = .25
        else:
            combat_mod = 1
        # next, check position
        pos_mod = 1
        if self.db.info['Position'] == "resting":
            pos_mod = 1.1
        elif self.db.info['Position'] == "sitting":
            pos_mod = 1.1
        elif self.db.info['Position'] == "supine":
            pos_mod = 1.2
        elif self.db.info['Position'] == "prone":
            pos_mod = 1.2
        elif self.db.info['Position'] == "sleeping":
            pos_mod = 1.5
        # TODO: implement moon phase modifier when we have that
        # TODO: Add a multiplier for wounds once we implment those
        # define regen dice and roll for amount to regen
        hp_regen_dice = self.ability_scores.Vit.actual * combat_mod * pos_mod * 2
        sp_regen_dice = self.ability_scores.Vit.actual * combat_mod * pos_mod * 2
        cp_regen_dice = self.ability_scores.Cha.actual * combat_mod * pos_mod
        hp_regen_roll = round(roll(hp_regen_dice, 'normal', \
                        self.ability_scores.Vit, self.traits.hp))
        sp_regen_roll = round(roll(sp_regen_dice, 'normal', \
                        self.ability_scores.Vit, self.traits.sp))
        cp_regen_roll = round(roll(cp_regen_dice, 'normal', \
                        self.ability_scores.Cha, self.traits.cp))
        log_file(f"{self.name} regen tick - HP: {hp_regen_roll} SP: {sp_regen_roll} CP: {cp_regen_roll}", \
                 filename='time_tick.log')
        self.traits.hp.current += hp_regen_roll
        self.traits.sp.current += sp_regen_roll
        self.traits.cp.current += cp_regen_roll


    def at_heartbeat_tick_do_progression_checks(self):
        """
        This function calls the progression checks to see if the character
        learns anything on this heartbeat tick. We will prevent learning
        while in combat.
        """
        if self.db.info['In Combat']:
            return
        else:
            control_progression_funcs(self)


    def exhaustion_check(self):
        """
        Checks if the character is out of stamina. If they are, the character
        falls over into a resting position.
        """
        if self.traits.sp.current < 1:
            self.caller.msg("You collapse to the floor from exhaustion.")
            self.caller.db.info['Position'] = 'prone'


    def reroll(self):
        """
        Rerolls stats and resets talents and mutations. This should only be
        triggered by the dev command reroll and should only be attempted when
        the character is not in combat.

        NOTE: This is equivolent to doing the update command, but won't create a
        duplicate set of scripts on the character.

        """
        self.ability_scores.clear()
        self.traits.clear()
        self.talents.clear()
        self.mutations.clear()
        # add in the ability scores
        self.ability_scores.add(key='Dex', name='Dexterity', type='static', \
                        base=rarsc(100), extra={'learn' : 0})
        self.ability_scores.add(key='Str', name='Strength', type='static', \
                        base=rarsc(100), extra={'learn' : 0})
        self.ability_scores.add(key='Vit', name='Vitality', type='static', \
                        base=rarsc(100), extra={'learn' : 0})
        self.ability_scores.add(key='Per', name='Perception', type='static', \
                        base=rarsc(100), extra={'learn' : 0})
        self.ability_scores.add(key='Cha', name='Charisma', type='static', \
                        base=rarsc(100), extra={'learn' : 0})
        # add in traits for health, stamina, conviction, mass, encumberance
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
        self.db.info = {'Target': None, 'Mercy': True, 'Default Attack': 'unarmed_strike', \
                        'In Combat': False, 'Position': 'standing', 'Sneaking' : False, \
                        'Wimpy': 100, 'Yield': 200, 'Title': None}
        # money
        self.db.wallet = {'GC': 0, 'SC': 0, 'CC': 0}
        self.update_character_sheet()


    def describe_health(self):
        """
        Returns a textual description of the remaining health of this object.
        Used for look command.
        """
        if self.traits.hp.current * 100.0 / self.traits.hp.max >= 95:
            return "|Gunhurt.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 90:
            return "|Ga few scratches.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 85:
            return "|Gscratched up.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 80:
            return "|gbleeding lightly.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max>= 70:
            return "|glightly wounded.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 60:
            return "|gmoderately wounded.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 50:
            return "|ytaken a bit of a thrashing.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 40:
            return "|ypretty beat up.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 25:
            return "|rbleeding heavily|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 15:
            return "|rnearly dead|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max < 5:
            return "|Rdeath's door.|n"


    def describe_fatigue(self):
        """
        Returns a textual description of the remaining stamina of this object.
        Used for look command.
        """
        if self.traits.hp.current * 100.0 / self.traits.hp.max >= 95:
            return "|Grested.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 90:
            return "|Ga single drop of sweat on their brow.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 85:
            return "|Gstill looking fresh.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 80:
            return "|gsweating lightly.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max>= 70:
            return "|gaudibly breathing.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 60:
            return "|gmoderately weezing.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 50:
            return "|ysweat pouring off of them.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 40:
            return "|ypretty tired.|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 25:
            return "|rlooking tired|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max >= 15:
            return "|rnearly exhausted|n"
        elif self.traits.hp.current * 100.0 / self.traits.hp.max < 5:
            return "|Rcompletely spent.|n"


    def update_character_sheet(self):
        """
        This function is called to update the character sheet when the command
        to display the character sheet is run.
        """
        if self.db.info['Title'] is not None:
            if len(self.db.info['Title']) < 25:
                name_and_title = "\t" + str(self.name) + self.db.info['Title']
        else:
            name_and_title = "\t\t\t\t" + str(self.name)
        name_and_title = f"|h|w{name_and_title}|n"
        funds = f"|551Gold:|n {self.db.wallet['GC']}    |445Silver:|n {self.db.wallet['SC']}    |530Copper:|n {self.db.wallet['CC']}"
        # NOTE: money stored in self.db.wallet
        att_table = evtable.EvTable("|035Attribute|n", "|wValue|n",
                        table = [
                            ["Health", "Stamina", "Conviction", "Dexterity", \
                             "Strength", "Vitality", "Perception", "Charisma", \
                             "Weight"],
                            [(str(int(self.traits.hp.current)) + " / " + str(self.traits.hp.max) ), \
                             (str(int(self.traits.sp.current)) + " / " + str(self.traits.sp.max) ), \
                             (str(int(self.traits.cp.current)) + " / " + str(self.traits.cp.max ) ), \
                             self.ability_scores.Dex.current, self.ability_scores.Str.current, \
                             self.ability_scores.Vit.current, self.ability_scores.Per.current, \
                             self.ability_scores.Cha.current, self.traits.mass.current]],
                             align='c', border="incols")
        # get top talents in a simplified dictionary converted to a list of
        # names and a list of scores
        talent_names, talent_scores = self.get_top_talents()
        talent_table = evtable.EvTable("|530Talent|n", "|wValue|n",
                        table = [
                            talent_names,
                            talent_scores],
                            align='c', border="incols")
        # reformat default attack names so they're friendlier for the character
        # sheet
        if self.db.info["Default Attack"] == "unarmed_strike":
            datt = 'Strikes'
        elif self.db.info["Default Attack"] == "melee_weapon_strike":
            datt = 'Melee Weapon'
        elif self.db.info["Default Attack"] == "ranged_weapon_strike":
            datt = 'Ranged Weapon'
        elif self.db.info["Default Attack"] == "mental_attack":
            datt = 'Psi'
        else:
            datt = self.db.info["Default Attack"].capitalize()
        info_table = evtable.EvTable("|530Info|n", "|wValue|n",
                        table = [
                                ["Default Attack", "Mercy", "Wimpy", "Yield", \
                                 "Sneaking"], \
                                [datt, self.db.info["Mercy"], \
                                 self.db.info["Wimpy"], self.db.info["Yield"], \
                                 self.db.info["Sneaking"]]],
                                 align='c', border="incols")
        # get the top mutations in a simplified dictionary converted to a list of
        # names and a list of scores
        mut_names, mut_scores = self.get_top_mutations()
        mutations_table = evtable.EvTable("|035Mutation|n", "|wValue|n",
                        table = [
                            mut_names,
                            mut_scores],
                            align='c', border="incols")
        self.db.charsheet.map(tables={2: att_table, 3: talent_table, \
                                      4: info_table, 5: mutations_table},
                              cells= {1: name_and_title, 6: funds})


    def get_top_talents(self):
        """
        Loops through all of the character's talents and returns the top 10
        talents in their list by current score.
        """
        top_talents_list = list(self.talents.all_dict.items())[:12]
        top_talents_dict = {v['name']: (v['base'] + v['mod']) for k, v in top_talents_list}
        talent_names = list(top_talents_dict.keys())
        talent_scores = list(top_talents_dict.values())
        return talent_names, talent_scores


    def get_top_mutations(self):
        """
        Loops through all of the character's mutations and returns the top 5
        mutations in their list by current score.
        """
        top_mutations_list = list(self.mutations.all_dict.items())[:5]
        top_mutations_dict = {v['name']: (v['base'] + v['mod']) for k, v in top_mutations_list}
        mut_names = list(top_mutations_dict.keys())
        mut_scores = list(top_mutations_dict.values())
        return mut_names, mut_scores


    # prevent movement into a room if the room is full. This is done using an
    # encumberance trait counter on rooms, just like the one on CharacterCmdSet
    def at_before_move(self, getter):
        """
        Called when a character or NPC tries to move into a room.
        """
        if getter.traits.enc.current + self.traits.mass.actual > getter.traits.enc.max:
            # room is full, cancel move
            self.msg("That room has too many things and/or people in it. You can't enter right now.")
            return False
        else:
            return True
