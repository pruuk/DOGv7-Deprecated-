"""
This file will contain the commands that are related to various talents like
sneak, track, appraise, etc that have an activated command.
"""
from evennia import Command
from evennia import CmdSet
from evennia import default_cmds
from evennia import search_object
from evennia.utils.logger import log_file
from world.dice_roller import return_a_roll as roll
import time
import random

class TalentCmdSet(CmdSet):
    """
    Contains the activation commands for character talents.
    """
    key = "talent_cmdset"
    mergetype = "Union" # we'll use this for now. Maybe we will use something else later
    priority = 10
    no_exits = False # stops the character from moving from the room

    def at_cmdset_creation(self):
        # self.add(CmdCollapse())
        self.add(CmdSneak())
        self.add(CmdTrack())


class CmdSneak(Command):
    """
    Toggles whether or not the character is trying to sneak around and be
    stealthy.

    Trying to sneak while moving costs more stamina to traverse from room
    to room.
    """
    key = "sneak"
    help_category = "Talents"

    def func(self):
        "Implements the command"
        if self.caller.db.info['Sneaking'] == False:
            self.caller.db.info['Sneaking'] = True
            self.caller.msg("You start sneaking around.")
        else:
            self.caller.db.info['Sneaking'] = False
            self.caller.msg("You stop sneaking around.")


class CmdTrack(Command):
    """
    Attempts to use the track command. If no target is given, the character
    will survey the current room for tracks. If a target is given, the
    character will attempt to look for tracks for the target.

    Usage:
        track
        track <target>
    """
    key = "track"
    help_category = "Talents"

    def func(self):
        "Implements the command"
        # roll skill for threshold
        track_roll = round(roll(self.caller.talents.tracking.actual * .8, \
                                'flat', self.caller.talents.tracking, \
                                self.caller.ability_scores.Per))
        if not self.args:
            # no target, survey the room for tracks
            self.survey_room(track_roll)
            return
        target = self.caller.search(self.args)
        if not target:
            # invalid target, survey the room for tracks
            self.survey_room(track_roll)
        else:
            # valid target, search for most recent tracks of target
            self.survey_target_tracks(target, track_roll)


    def survey_room(self, track_roll):
        "No target, survey for tracks"
        self.caller.msg("You search the room for tracks.")
        num_of_tracks = random.randrange(3)
        success = False
        for timestamp, track_info in self.caller.location.db.tracks.items():
            # age of track in days. note that game time is twice as fast as
            # real time.
            track_age = (int(time.time()) - int(timestamp)) / (60 * 60 * 12)
            trackee = track_info[0]
            destination = track_info[1]
            difficulty_to_track = track_info[2] + (track_age * 10)
            # log_file(f"Tracking Rolls - {self.caller.name} - roll: {track_roll} Age: {track_age} trackee: {trackee} destination: {destination} diff: {difficulty_to_track}", \
            #          filename='tracks.log')
            if track_roll > difficulty_to_track and num_of_tracks > 0:
                if trackee != self.caller:
                    self.caller.msg(f"You found some tracks of {trackee} heading to {destination} that are about {round(track_age)} days old.")
                else:
                    self.caller.msg(f"You find a track you left heading to {destination} that is about {round(track_age)} days old.")
                num_of_tracks -= 1
                success = True
        if success == False:
            self.caller.msg("You can't make head nor tails of the tracks.")


    def survey_target_tracks(self, target, track_roll):
        "Survey for tracks of the target"
        if target != self.caller:
            self.caller.msg(f"You survey the room for tracks of {target}")
        else:
            self.caller.msg("You survey the room for any tracks you left.")
        success = False
        for timestamp, track_info in self.caller.location.db.tracks.items():
            # age of track in days. note that game time is twice as fast as
            # real time.
            track_age = (int(time.time()) - int(timestamp)) / (60 * 60 * 12)
            trackee = track_info[0]
            destination = track_info[1]
            difficulty_to_track = track_info[2] + (track_age * 10)
            # log_file(f"Tracking Rolls - {self.caller.name} - roll: {track_roll} Age: {track_age} trackee: {trackee} destination: {destination} diff: {difficulty_to_track}", \
            #          filename='tracks.log')
            if track_roll > difficulty_to_track and trackee == target:
                if trackee != self.caller:
                    self.caller.msg(f"You found some tracks of {trackee} heading to {destination} that are about {round(track_age)} days old.")
                else:
                    self.caller.msg(f"You find a track you left heading to {destination} that is about {round(track_age)} days old.")
                # we found a track, break out of Loop
                return
        if success == False:
            self.caller.msg("You can't make head nor tails of the tracks.")
