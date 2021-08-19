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
from world.combat_description import return_grappling_takedown_text as takedowntxt
from world.combat_description import return_grappling_position_text as grappling_pos_txt
from world.combat_description import return_grappling_unarmed_damage_normal_text as grudnt
from world.combat_description import return_grappling_submission_text as rgsat
from world.combat_description import return_grappling_escape_text as rgeat
from world.combat_description import return_melee_weapon_strike_text as mwst
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
    log_file("start of send msg to actor func", filename='combat_step.log')
    actor.msg(f"{actor_msg_string}")
    actor.execute_cmd("rprom")


def send_msg_to_actee(actee, actee_msg_string):
    """
    This function takes in the object that is being acted upon, such as the
    player being attacked. It then sens them a message in the third person,
    with their name replaced by 'you'.
    """
    log_file("start of send msg to actee func", filename='combat_step.log')
    actee.msg(f"{actee_msg_string}")
    actee.execute_cmd("rprom")


def send_msg_to_observer(observer, observer_msg_string):
    """
    This function takes in the attacker object and the message string to be
    sent to the attacker. The function then messeages the attacker.
    """
    log_file("start of send msg to observer func", filename='combat_step.log')
    observer.msg(f"{observer_msg_string}")
    observer.execute_cmd("rprom")


def send_msg_to_objects(pcs_and_npcs_in_room, actor_msg_string, actee_msg_string, observer_msg_string):
    """
    This function gathers in the info to call all three of the functions above
    and calls them.
    """
    log_file("start of send msg to all objs func", filename='combat_step.log')
    log_file(f"Roles - Actor: {pcs_and_npcs_in_room['Actor']} Actee: {pcs_and_npcs_in_room['Actee']} Observers: {pcs_and_npcs_in_room['Observers']}", \
             filename='combat_step.log')
    log_file(f"msg strings: {actor_msg_string} {actee_msg_string} {observer_msg_string}", \
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


def build_msgs_for_takedown(attacker, defender, success_lvl):
    """
    This function takes in the necessary args for a takedown attempt and
    messages everyone in the room in an appropriate manner.
    """
    log_file("start of build msgs for takedown func", \
             filename='combat_step.log')
    pcs_and_npcs_in_room = determine_objects_in_room(attacker.location, attacker, defender)
    log_file(f"Room occupants: {pcs_and_npcs_in_room}", filename='combat_step.log')
    final_text_dict = takedowntxt(pcs_and_npcs_in_room, success_lvl)
    log_file(f"text dict: {final_text_dict}", filename='combat_step.log')
    actor_msg_string = f"You |220{final_text_dict['Actor']}|n {defender.name}."
    actee_msg_string = f"{attacker.name} |220{final_text_dict['Actee']}|n you."
    observer_msg_string = f"{attacker.name} |220{final_text_dict['Observer']}|n {defender.name}."
    send_msg_to_objects(pcs_and_npcs_in_room, actor_msg_string, actee_msg_string, observer_msg_string)


def build_msgs_for_grappling_improve_position(attacker, defender):
    """
    This function takes in the necessary args and returns the textual descriptions
    of the grappling attempt, which will include listing out the new positions.
    We'll keep this fairly simple to avoid having to build a dictionary of
    mappings from every possible starting position to every possible ending
    position. The textual description will be tied to the success lvl.
    """
    log_file("start of build msgs for grappling improve position func", \
             filename='combat_step.log')
    pcs_and_npcs_in_room = determine_objects_in_room(attacker.location, attacker, defender)
    log_file(f"Room occupants: {pcs_and_npcs_in_room}", filename='combat_step.log')
    final_text_dict = grappling_pos_txt(pcs_and_npcs_in_room)
    log_file(f"text dict: {final_text_dict}", filename='combat_step.log')
    actor_msg_string = f"You |110{final_text_dict['Actor']}|n {defender.name}, ending with you in {attacker.db.info['Position']}"
    actee_msg_string = f"{attacker.name} |110{final_text_dict['Actee']}|n, ending with you in {defender.db.info['Position']}"
    observer_msg_string = f"{attacker.name} |110{final_text_dict['Observer']}|n, ending with {defender.name} in {defender.db.info['Position']}"
    send_msg_to_objects(pcs_and_npcs_in_room, actor_msg_string, actee_msg_string, observer_msg_string)


def build_msgs_for_grappling_unarmed_strikes_normal(attacker, defender, damage):
    """
    This function returns the messaging for unarmed strikes where the attacker
    doesn't have any mutations to give them natural weapons like sharp claws AND
    the combatants are in a grappling position.
    """
    log_file("start of build msgs for grappling unarmed strikes normal func", \
             filename='combat_step.log')
    pcs_and_npcs_in_room = determine_objects_in_room(attacker.location, attacker, defender)
    log_file(f"Room occupants: {pcs_and_npcs_in_room}", filename='combat_step.log')
    final_text_dict, hit_loc, damage_text = grudnt(pcs_and_npcs_in_room, damage)
    log_file(f"text dict: {final_text_dict} hit loc: {hit_loc} Dam text: {damage_text}", \
             filename='combat_step.log')
    actor_msg_string = f"You |420{final_text_dict['Actor']}|n {defender.name}. Their |h|!W{hit_loc}|n is {damage_text}."
    actee_msg_string = f"{attacker.name} |420{final_text_dict['Actee']}|n you. Your |h|!W{hit_loc}|n is {damage_text}."
    observer_msg_string = f"{attacker.name} |420{final_text_dict['Observer']}|n {defender.name}'s |h|!W{hit_loc}|n, which is {damage_text}."
    send_msg_to_objects(pcs_and_npcs_in_room, actor_msg_string, actee_msg_string, observer_msg_string)


def build_msgs_for_grappling_submission(attacker, defender, damage, success):
    """
    This function returns the combat messaging for submission attempts.
    """
    log_file("start of build msgs for grappling sub func", \
             filename='combat_step.log')
    pcs_and_npcs_in_room = determine_objects_in_room(attacker.location, attacker, defender)
    log_file(f"Room occupants: {pcs_and_npcs_in_room}", filename='combat_step.log')
    final_text_dict, damage_text = rgsat(pcs_and_npcs_in_room, damage, success)
    log_file(f"text dict: {final_text_dict}", filename='combat_step.log')
    actor_msg_string = f"You |111{final_text_dict['Actor']}|n {defender.name}."
    actee_msg_string = f"{attacker.name} |111{final_text_dict['Actee']}|n you."
    observer_msg_string = f"{attacker.name} |111{final_text_dict['Observer']}|n {defender.name}."
    # TODO: Figure out how to work in damage text
    send_msg_to_objects(pcs_and_npcs_in_room, actor_msg_string, actee_msg_string, observer_msg_string)


def build_msgs_for_grappling_escape(attacker, defender, success):
    """
    This function returns the combat messaging for submission escape attempts.
    """
    log_file("start of build msgs for grappling escape func", \
             filename='combat_step.log')
    pcs_and_npcs_in_room = determine_objects_in_room(attacker.location, attacker, defender)
    log_file(f"Room occupants: {pcs_and_npcs_in_room}", filename='combat_step.log')
    final_text_dict = rgeat(pcs_and_npcs_in_room, success)
    log_file(f"text dict: {final_text_dict}", filename='combat_step.log')
    actor_msg_string = f"You {final_text_dict['Actor']} against {defender.name}."
    actee_msg_string = f"{attacker.name} {final_text_dict['Actee']}."
    observer_msg_string = f"{attacker.name} {final_text_dict['Observer']}."
    send_msg_to_objects(pcs_and_npcs_in_room, actor_msg_string, actee_msg_string, observer_msg_string)


def build_msgs_for_melee_weapon_strikes(attacker, defender, damage):
    """
    This function returns the combat messaging for melee weapon strike attempts.
    """
    log_file("start of build msgs for melee weapon strike func", \
             filename='combat_step.log')
    pcs_and_npcs_in_room = determine_objects_in_room(attacker.location, attacker, defender)
    log_file(f"Room occupants: {pcs_and_npcs_in_room}", filename='combat_step.log')
    final_text_dict, hit_loc, damage_text = mwst(pcs_and_npcs_in_room, damage)
    log_file(f"text dict: {final_text_dict} hit loc: {hit_loc} Dam text: {damage_text}", \
             filename='combat_step.log')
    actor_msg_string = f"You |411{final_text_dict['Actor']}|n {defender.name}. Their |h|!W{hit_loc}|n is {damage_text}."
    actee_msg_string = f"{attacker.name} |411{final_text_dict['Actee']}|n you. Your |h|!W{hit_loc}|n is {damage_text}."
    observer_msg_string = f"{attacker.name} |411{final_text_dict['Observer']}|n {defender.name}'s |h|!W{hit_loc}|n, which is {damage_text}."
    send_msg_to_objects(pcs_and_npcs_in_room, actor_msg_string, actee_msg_string, observer_msg_string)
