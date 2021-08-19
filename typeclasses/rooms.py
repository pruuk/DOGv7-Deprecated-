"""
Room

Rooms are simple containers that has no location of their own.

"""
from evennia import utils as utils
from evennia import DefaultRoom
from evennia.utils.logger import log_file
from evennia.utils import lazy_property
from world.traits import TraitHandler
import time
from world.dice_roller import return_a_roll as roll


class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    @lazy_property
    def traits(self):
        """TraitHandler that manages room traits."""
        return TraitHandler(self)

    def at_object_creation(self):
        "Ran only at object creation"
        super().at_object_creation()
        self.traits.clear()
        # traits to add at room creation
        self.traits.add(key="elevation", name="Elevation", type="static", \
                        base=1000) # elevation above sea level
        # ruggedness of terrain from 0.01 to 1. How hard is it to move across
        # this room? combination of slope and terrain obstacles
        self.traits.add(key="rot", name="Ruggedness of Terrain", \
                        type="static", base=0.05)
        # size of room, rough measure in square meters, default is large outdoor
        # room 100m X 100m
        self.traits.add(key="size", name="Room Size", \
                        type="static", base=10000)
        # maximum number of tracks to store. Some terrain allows for tracks to
        # be readable even with a large amount of foot traffic.
        self.traits.add(key="trackmax", name="Maximum Readable Tracks", \
                        type="static", base=(round(self.traits.size.actual / 500))) # default of 20
        # add encumberance to room to limit the amount of junk that can be
        # dropped in a given room
        self.traits.add(key="enc", name="Encumberance", type='counter', \
                        base=0, max=(self.traits.size.actual * 10))
        # boolean info attributes of the room
        self.db.info = {'Non-Combat Room': False, 'Outdoor Room': True, \
                        'Zone': None, 'Environment Type': None}
        # empty db attribute dictionary for storing tracks
        self.db.tracks = {}


    def store_tracks(self, character_or_npc, target_location):
        """
        Stores the tracks of a character or NPC moving through the room.
        """
        timestamp = int(time.time())
        if character_or_npc.db.info['Sneaking'] == True:
            track_depth = round(roll(character_or_npc.talents.sneak.actual, 'normal', \
                            character_or_npc.talents.sneak))
        else:
            track_depth = 100
        self.db.tracks[timestamp] = (character_or_npc, target_location, track_depth)
        log_file(f"{timestamp} - Storing tracks for {character_or_npc}. Track depth: {track_depth}", \
                 filename='tracks.log')
        if len(self.db.tracks) > self.traits.trackmax.actual:
            # too many tracks, remove one
            self.remove_old_tracks()


    def remove_old_tracks(self):
        """
        Loops through tracks and removes really old tracks
        """
        self.db.tracks.popitem()


    def remove_tracks_weather(self):
        """
        Loops through tracks and removes tracks due to weather events
        """
        pass


    ## Adding custom hook to allow NPCs to "notice" when a character
    ## enters the room they are in.
    def at_object_receive(self, obj, source_location):
        if utils.inherits_from(obj, 'typeclasses.npcs.NPC') or utils.inherits_from(obj, 'typeclasses.characters.Character'):
            # An NPC has entered or a player has entered.
            ## cause the NPC or player to look around
            # obj.execute_cmd('look')
            for item in self.contents:
                # message everyone that is in the room except the one that just entered
                # TODO: Account for stealth and suppress the message if the movement into
                #       the room was unnoticed
                if item != obj:
                    item.msg(f"{obj} has entered from {source_location}.")
                if utils.inherits_from(item, 'typeclasses.npcs.NPC'):
                    # An NPC is in the room
                    if obj.db.info['Sneaking'] == False:
                        item.at_char_entered(obj)
                    else:
                        sneak_roll = round(roll(obj.talents.sneak.actual, 'flat', \
                                                obj.talents.sneak, obj.ability_scores.Dex, \
                                                obj.ability_scores.Per))
                        notice_roll = round(roll(item.ability_scores.Per.actual, 'flat', \
                                                item.ability_scores.Per))
                        if notice_roll <= sneak_roll:
                            item.at_char_entered(obj)
        else:
            self.calculate_encumberance()


    # apply tracks as character or NPC leaves the room
    def at_object_leave(self, obj, target_location):
        if utils.inherits_from(obj, 'typeclasses.npcs.NPC') or utils.inherits_from(obj, 'typeclasses.characters.Character'):
            self.store_tracks(obj, target_location)
            # also, tax the character's stamina for moving through the room
            # sneaking makes this more expensive
            if obj.db.info['Sneaking'] == True:
                obj.traits.sp.current -= (self.traits.rot.actual * self.traits.size.actual / 30)
            else:
                obj.traits.sp.current -= (self.traits.rot.actual * self.traits.size.actual / 100)
            # also refresh the prompt
            obj.execute_cmd("rprom")
        else:
            self.calculate_encumberance()


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
                 filename='room.log')
        self.traits.enc.current = 0
        items = self.contents
        log_file(f"Contents of room: {items}", \
                 filename='room.log')
        for item in items:
            log_file(f"calculating mass for {item.name}", \
                     filename='room.log')
            if utils.inherits_from(item, 'typeclasses.npcs.NPC') or utils.inherits_from(item, 'typeclasses.characters.Character'):
                log_file(f"Item is a char or NPC- mass:{item.traits.mass.actual}", \
                         filename='room.log')
                self.traits.enc.current += item.traits.mass.actual
            elif utils.inherits_from(item, 'typeclasses.exits.Exit'):
                pass
            else:
                log_file(f"Item is a regular item- mass:{item.db.mass}", \
                         filename='room.log')
                self.traits.enc.current += item.db.mass
