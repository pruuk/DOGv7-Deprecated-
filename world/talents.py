# -*- coding: utf-8 -*-
"""
Talents Module.

This module is modeled after the skills module for the Ainneve mud based upon
Evennia. I've borrowed heavily from the code and style at:
https://github.com/evennia/ainneve/blob/master/world/skills.py

This module contains the data and functions related to character & NPC Talents.

In DOG, characters/NPCs have three similar storage mechanisms for determining
the relative power and abilities of the character/NPC:
1. Traits - These are also used for objects and rooms. They define the
            base power and attribuites that describe an object. How striong is
            this character? How coordinated are they? How much damage can this
            box take before it is smashed to bits? How large is this room?
2. Mutations - In DOG, a virus has infected animal and plant life which causes
               rapid mutations. These mutations mostly follow the type of
               actions/events related to the character/NPC/animal/plant. By
               performing actions, a character has a chance (upon critical
               success or critical failure) to mutate in a way related to the
               action. For example, if the character takes a large amount of
               damage, they might mutate and develop denser bones or faster
               reactions or think armored/scaled skin. As a general rule, most
               mutations affect the numerical values of traits such as ability
               scores, health, stamina, etc. High tier mutations that require
               other prerequisite mutations can enable certain Talents, such as
               flight or psionic abilities.
3. Talents - These are abilities that give characters/NPCs/etc new action
             action options. Examples include skill-based abilities such as
             melee combat, climbing, lockpicking, crafting. Other types of
             talents are unlocked by prerequisite mutations or other talents
             (or a combination of both) such as flight or psionic abilities.

Please see:
https://docs.google.com/document/d/1YoCURidXUJab1nQy1L5_66MF5n8D1QwQlojroV4XuGw/edit
and:
https://docs.google.com/document/d/1ATy_q5RCEiCPj043pZbpJKFWbaruv5Vb2iP8yKWGv1c/edit
for more information about the world of DOG and the plan for implementing the
first sets of mutations and talents.

Module Functions:
    - `apply_talents(char)`
        Initializes a character's db.talents attribute to support talent
        traits. In OA, all talents start matching their base trait before
        the player allocates a number of +1 and -1 counters.
    - `load_talent(talent)`
        Loads an instance of the talent class by name for display of
        talent name and description.
    - `validate_talents(char)`
        Validates a player's talent penalty and bonus token allocations.
        Because the requirements depend on the char's INT trait, it
        accepts the entire char as its argument.
    - `finalize_talents(talents)`
        Finalizes and "saves" the player's allocations and deletes the
        'plus' and 'minus' extra keys used during chargen.
"""
from math import ceil
