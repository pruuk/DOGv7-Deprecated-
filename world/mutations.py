# -*- coding: utf-8 -*-
"""
Mutations module.

This module is modeled after the skills module for the Ainneve mud based upon
Evennia. I've borrowed heavily from the code and style at:
https://github.com/evennia/ainneve/blob/master/world/skills.py

This module contains the data and functions related to object Mutations.

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

Classes:
    'mutation': convenience object for mutation display data

Module Functions:

    - initialize_mutations(character)
        Initializes a character or NPCs starting mutations. These are limited in
        number and mostly represent the types of mutations measured around the
        base of 100 (human normal). All other mutations will be initialized with
        a score of 0 (meaning the character or NPC does not have that mutation yet)

    - 'load_mutation(mutation)'
        Loads an instance of the Skill class by name for display of skill name
        and description.

    - 'validate_mutation(character)'
        Validates a player or NPC's mutation penalty and bonus modifiers. Takes in
        the entire object as an argument to make full use of all info on the
        character or NPC.

"""
# imports
from world.dice_roller import return_a_roll_sans_crits as rarsc

class MutationException(Exception):
    def __init__(self, msg):
        self.msg = msg

# list of mutations, stored in a dict by related ability score (stored in traits)
_MUTATION_DATA = {
    # Dex based mutations
    'extreme_flexibility': {
        'name': 'Extreme Flexibility',
        'base': 'Dex',
        'desc': ("|mExtreme Flexibility|n is a mutation that improves the "
                 "ability to dodge and block in combat, reduces damage from "
                 "some grappling attacks, and allows the character to fit in "
                 "tight locations. This is a prerequisite to the rubber body "
                 "power."),
        'prerequisites': None,
        'starting_score': 'Dex',
        'range': {'min': 25, 'max': 500}
    },
    'rubber_body': {
        'name': 'Rubber Body',
        'base': 'Dex',
        'desc': ("|mRubber Body|n is a mutation that makes the body soft and "
                 "extremely flexible. Characters with this mutation are "
                 "resistant to bludgeoning damage and some grappling attacks. "
                 "Rubber body allows the character to fit in tight locations "
                 "and in some cases  "
                 "power."),
        'prerequisites': {'mutations.extreme_flexibility.actual': 200},
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'improved_balance': {
        'name': 'Improved Balance',
        'base': 'Dex',
        'desc': ("|mImproved Balance|n is a mutation that makes the character "
                 "more difficult to knock down, trip, throw, etc.. It also has"
                 "a minor effect on the footwork skill."),
        'prerequisites': None,
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    # Str based mutations
    
}
