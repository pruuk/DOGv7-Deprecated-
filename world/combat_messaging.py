# -*- coding: utf-8 -*-
"""
This file will contains the functions for controlling messaging to the
characters and NPCs in a room where combat is happening. The messaging will be
divided into three kinds of occupants of the room:
- Actor - The person that is taking an action like hitting, blocking, etc.
- Actee - The person that is beiong acted upon. They've been hit, dodged, etc
- Observer - Any characters or NPCs that are in the room, but are not the
             actor or actee. They may or may not be a part of the combat, but
             that is independent of the role determination


The messaging functions will be called by combat_actions script objects or the
combat handler script object. The messaging functions in turn will pull phrasing
for combat action descriptions from a number of sources:
- The combat description file - Contains 90% of the combat descriptions or more.
                                These are stored in dictionaries.
- From item objects - For example, weapons can have their owbn unique attack
                      phrases. As weapons become more powerful, this gets more
                      common
- From character objects - Some characters will have mutations that give them
                           unique attack phrases.
- From room objects - Some rooms will have unique movement phrases. For example,
                      a character may fail to close range because of slipping in
                      mud.
"""
from evennia import utils
from world.combat_description import return_unarmed_damage_normal_text as rudnt
from world.combat_description import return_dodge_text as dodgetxt
from world.combat_description import return_unarmed_block_text as blocktxt
from evennia.utils.logger import log_file

## functions for delivering messages
# what characters and NPCs are in the room?
def determine_objects_in_room(location, actor, actee):
    """
    This function takes in a room object where combat is happening, checks the
    contents of the room, and determines which objects should get a message.
    """
    log_file("start of determine objects in room func", filename='combat_step.log')
    # empty dictionary for use later
    pcs_and_npcs_in_room = {'Actor': [], 'Actee': [], 'Observers': []}
    # get room contents
    objects_in_room = location.contents
    log_file(f"Room: {location} contents: {location.contents}", \
             filename='combat_step.log')
    # loop through contents and determine if they are the correct typeclasses
    # to be messaged at
    for obj in objects_in_room:
        log_file(f"Testing {obj} to see if they are a char or NPC.", \
                 filename='combat_step.log')
        # TODO: Add NPC typeclasses to this when we create them
        if utils.inherits_from(obj, 'typeclasses.npcs.NPC') or utils.inherits_from(obj, 'typeclasses.characters.Character'):
            log_file(f"Role assignment for {obj.name}", filename='combat_step.log')
            if obj == actor:
                pcs_and_npcs_in_room['Actor'] = actor
                log_file(f"{obj.name} is the actor.", filename='combat_step.log')
            elif obj == actee:
                pcs_and_npcs_in_room['Actee'] = actee
                log_file(f"{obj.name} is the actee.", filename='combat_step.log')
            else:
                pcs_and_npcs_in_room['Observers'].append(obj)
                log_file(f"{obj.name} is an observer.", filename='combat_step.log')
        else:
            log_file(f"{obj} not a char or NPC. type: {type(obj)}", \
                     filename='combat_step.log')
            pass
    # return dict of player and NPC objects
    return pcs_and_npcs_in_room


def send_msg_to_actor(actor, actor_msg_string):
    """
    This function takes in the object performing an action, like attack or
    dodging plus a message string formatted in the first person tense. It then
    sends them that message.
    """
    log_file("start of seng msg to actor func", filename='combat_step.log')
    actor.msg(f"{actor_msg_string}")


def send_msg_to_actee(actee, actee_msg_string):
    """
    This function takes in the object that is being acted upon, such as the
    player being attacked. It then sens them a message in the third person,
    with their name replaced by 'you'.
    """
    log_file("start of seng msg to actee func", filename='combat_step.log')
    actee.msg(f"{actee_msg_string}")


def send_msg_to_observer(observer, observer_msg_string):
    """
    This function takes in the attacker object and the message string to be
    sent to the attacker. The function then messeages the attacker.
    """
    log_file("start of seng msg to observer func", filename='combat_step.log')
    observer.msg(f"{observer_msg_string}")


def send_msg_to_objects(pcs_and_npcs_in_room, actor_msg_string, actee_msg_string, observer_msg_string):
    """
    This function gathers in the info to call all three of the functions above
    and calls them.
    """
    log_file("start of seng msg to all objs func", filename='combat_step.log')
    log_file(f"Roles - Actor: {pcs_and_npcs_in_room['Actor']} Actee: {pcs_and_npcs_in_room['Actee']} Observers: {pcs_and_npcs_in_room['Observers']}", \
             filename='combat_step.log')
    for role, character in pcs_and_npcs_in_room.items():
        if role == 'Actor':
            send_msg_to_actor(character, actor_msg_string)
        elif role == 'Actee':
            send_msg_to_actee(character, actee_msg_string)
        elif role == 'Observers':
            for observer in pcs_and_npcs_in_room['Observers']:
                log_file(f"attempting to send msg for {observer.name}", \
                         filename='combat_step.log')
                send_msg_to_observer(observer, observer_msg_string)


def build_msgs_for_unarmed_strikes_normal(attacker, defender, damage):
    """
    This function returns the messaging for unarmed strikes where the attacker
    doesn't have any mutations to give them natural weapons like sharp claws.
    """
    log_file("start of build msgs for unarmed strikes normal func", \
             filename='combat_step.log')
    pcs_and_npcs_in_room = determine_objects_in_room(attacker.location, attacker, defender)
    log_file(f"Room occupants: {pcs_and_npcs_in_room}", filename='combat_step.log')
    final_text_dict, hit_loc, damage_text = rudnt(pcs_and_npcs_in_room, damage)
    log_file(f"text dict: {final_text_dict} hit loc: {hit_loc} Dam text: {damage_text}", \
             filename='combat_step.log')
    actor_msg_string = f"You |420{final_text_dict['Actor']}|n {defender.name}. Their |h|!W{hit_loc}|n is {damage_text}."
    actee_msg_string = f"{attacker.name} |420{final_text_dict['Actee']}|n you. Your |h|!W{hit_loc}|n is {damage_text}."
    observer_msg_string = f"{attacker.name} |420{final_text_dict['Observer']}|n {defender.name}'s |h|!W{hit_loc}|n, which is {damage_text}."
    send_msg_to_objects(pcs_and_npcs_in_room, actor_msg_string, actee_msg_string, observer_msg_string)


def build_msgs_for_successful_dodge(attacker, defender):
    """
    This function takes in the necessary args about an attack being dodged and
    messages everyone in the room in an appropriate manner.
    """
    log_file("start of build msgs for dodges func", \
             filename='combat_step.log')
    pcs_and_npcs_in_room = determine_objects_in_room(defender.location, defender, attacker)
    log_file(f"Room occupants: {pcs_and_npcs_in_room}", filename='combat_step.log')
    final_text_dict = dodgetxt(pcs_and_npcs_in_room)
    log_file(f"text dict: {final_text_dict}", filename='combat_step.log')
    actor_msg_string = f"You |c{final_text_dict['Actor']}|n {attacker.name}."
    actee_msg_string = f"{defender.name} |c{final_text_dict['Actee']}|n your attack."
    observer_msg_string = f"{defender.name} |c{final_text_dict['Observer']}|n {attacker.name}."
    send_msg_to_objects(pcs_and_npcs_in_room, actor_msg_string, actee_msg_string, observer_msg_string)


def build_msgs_for_successful_block(attacker, defender):
    """
    This function takes in the necessary args about an attack being dodged and
    messages everyone in the room in an appropriate manner.
    """
    # TODO: expand this depending on if the defender is armed later
    log_file("start of build msgs for dodges func", \
             filename='combat_step.log')
    pcs_and_npcs_in_room = determine_objects_in_room(defender.location, defender, attacker)
    log_file(f"Room occupants: {pcs_and_npcs_in_room}", filename='combat_step.log')
    final_text_dict = blocktxt(pcs_and_npcs_in_room)
    log_file(f"text dict: {final_text_dict}", filename='combat_step.log')
    actor_msg_string = f"You |g{final_text_dict['Actor']}|n {attacker.name}."
    actee_msg_string = f"{defender.name} |g{final_text_dict['Actee']}|n your attack."
    observer_msg_string = f"{defender.name} |g{final_text_dict['Observer']}|n {attacker.name}."
    send_msg_to_objects(pcs_and_npcs_in_room, actor_msg_string, actee_msg_string, observer_msg_string)
