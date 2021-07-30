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
    # Dexterity based mutations
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
    # Strength based mutations
    'bone_density': {
        'name': 'Bone Density',
        'base': 'Str',
        'desc': ("|mBone Density|n is a measure of the density of the "
                 "density of the character's bones. This mutation can raise or "
                 "lower the density of the character's bones, which can affect "
                 "a number of other mutations, the maximum Strength of the "
                 "character, the mass of the character, how expensive (in "
                 "Stamina cost) it is to move between rooms. The minimum for"
                 "this score is 25 and the maximum is 1000. 100 is human normal."),
        'prerequisites': None,
        'starting_score': 'Str',
        'range': {'min': 25, 'max': 1000}
    },
    # Vitality based mutations
    'increased_regeneration': {
        'name': 'Increased Regeneration',
        'base': 'Vit',
        'desc': ("|mIncreased Regeneration|n is a mutation that increases the "
                 "rate that a character heals health and stamina."),
        'prerequisites': None,
        'starting_score': 'Vit',
        'range': {'min': 0, 'max': 500}
    },
    'regrow_limbs': {
        'name': 'Regrow Limbs',
        'base': 'Vit',
        'desc': ("|mRegrow Limbs|n is a mutation that allows the character to "
                 "heal egregious wounds, such as losing a limb."),
        'prerequisites': {'mutations.increased_regeneration.actual': 300},
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'extra_limbs': {
        'name': 'Extra Limbs',
        'base': 'Vit',
        'desc': ("|mExtra Limbs|n is a mutation that increases the number of "
                 "limbs that a character has. The extra limbs can be extra "
                 "arms, legs, or wings. Extra limbs are only useful once they "
                 "have mutated to a score of 100. For every 100 points (rounded "
                 "down), the character has a useable extra limb."),
        'prerequisites': {'mutations.regrow_limbs.actual': 200},
        'starting_score': 0,
        'range': {'min': 0, 'max': 600}
    },
    'wings': {
        'name': 'Wings',
        'base': 'Vit',
        'desc': ("|mWings|n is a mutation that allows a character to grow wings "
                 "which can eventually allow Winged Flight if other "
                 "prerequisites are met."),
        'prerequisites': {'mutations.extra_limbs.actual': 200},
        'starting_score': 0,
        'range': {'min': 0, 'max': 600}
    },
    'tail': {
        'name': 'Tail',
        'base': 'Vit',
        'desc': ("|mTailn|n is a mutation that allows a character to grow a "
                 "tail which can eventually allow Winged Flight if other "
                 "prerequisites are met. The tail can also be used to natural "
                 "weapon attacks (like claws)."),
        'prerequisites': {'mutations.extra_limbs.actual': 100},
        'starting_score': 0,
        'range': {'min': 0, 'max': 300}
    },
    'armored_hide': {
        'name': 'Armored Hide',
        'base': 'Vit',
        'desc': ("|mArmored Hide|n is a mutation that allows a character to grow "
                 "armored hide, scales, or plates which mitigate damage from "
                 "many types of damage. This mutation changes the appearance "
                 "of the character and increases their mass."),
        'prerequisites': None,
        'starting_score': 0,
        'range': {'min': 0, 'max': 300}
    },
    'bladed_body': {
        'name': 'Bladed Body Ridges',
        'base': 'Vit',
        'desc': ("|mBladed Body Ridges|n is a mutation that allows a character "
                 "to grow sharp body ridges which can do damage to attackers or "
                 "cause many grappling attacks to do damage."),
        'prerequisites': {'powers.armored_hide': 200},
        'starting_score': 0,
        'range': {'min': 0, 'max': 300}
    },
    'sharp_claws': {
        'name': 'Sharp Claws',
        'base': 'Vit',
        'desc': ("|mSharp Claws|n is a mutation that allows a character to grow "
                 "sharp claws on their hands and feet, which can increase the "
                 "damage of unarmed strikes, but make equipping shoes and gloves "
                 "difficult unless the equipment is custom crafted."),
        'prerequisites': None,
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'limb_length': {
        'name': 'Limb Length',
        'base': 'Vit',
        'desc': ("|mLimb Length|n is a mutation that measures how long a "
                 "character's limbs are compared to human normal of 100. Longer "
                 "limbs affect reach and distance in combat as well as damage "
                 "for certain types of attacks."),
        'prerequisites': None,
        'starting_score': {'rarsc': 100},
        'range': {'min': 50, 'max': 250}
    },
    'gut_biome': {
        'name': 'Interesting Gut Biome',
        'base': 'Vit',
        'desc': ("|mInteresting Gut Biome|n is a mutation that allows a "
                 "character's to eat many things a normal character couldn't. "
                 "At advanced levels, some characters may be able to control "
                 "their gut biome well enough to synthesize compounds within "
                 "their own gut."),
        'prerequisites': None,
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'poison_bite': {
        'name': 'Poison Bite',
        'base': 'Vit',
        'desc': ("|mPoison Bite|n is a mutation that allows a character to"
                 "inflict a poisonous or bacterially damaging bite upon a "
                 "victim. Please note that effective use of this mutation "
                 "requires using a combat talent that involves biting."),
        'prerequisites': {'mutations.gut_biome': 200},
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'poison_spit': {
        'name': 'Poison Spit',
        'base': 'Vit',
        'desc': ("|mPoison Spit|n is a mutation that allows a character to"
                 "inflict a poisonous or bacterially damaging ranged attack "
                 "upon a victim. Please note that effective use of this mutation "
                 "requires using a combat talent that involves spitting."),
        'prerequisites': {'mutations.poison_bite': 200},
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'sticky_spit': {
        'name': 'Sticky Spit',
        'base': 'Vit',
        'desc': ("|mSticky Spit|n is a mutation that allows a character to"
                 "produce very sticky spit that can be used an a debilitating "
                 "attack or as an adhesive. Please note that effective use of "
                 "this mutation requires using a combat talent that involves "
                 "spitting."),
        'prerequisites': {'mutations.gut_biome': 300},
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'gills': {
        'name': 'Gills',
        'base': 'Vit',
        'desc': ("|mGills|n is a mutation that allows a character to breathe"
                 "underwater. It makes wearing certain body armors harder, "
                 "possibly requiring custom armor."),
        'prerequisites': None,
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'webbed_feet': {
        'name': 'Webbed Feet',
        'base': 'Vit',
        'desc': ("|mWebbed Feet|n is a mutation that allows a character to grow"
                 "webbed feet. It makes wearing certain foot armors harder, "
                 "possibly requiring custom armor. Travel ubnderwater will be "
                 "easier for the character, but they will be slower on land."),
        'prerequisites': None,
        'starting_score': 0,
        'range': {'min': 0, 'max': 300}
    },
    'slow_aging': {
        'name': 'Slow Aging',
        'base': 'Vit',
        'desc': ("|mSlow Aging|n is a mutation that allows a character to "
                 "manipulate their own aging process, slowing it to a crawl."),
        'prerequisites': {'powers.gut_biome': 400,
                          'mutations.increased_regeneration': 800},
        'starting_score': 0,
        'range': {'min': 0, 'max': 300}
    },

    # Perception based mutations
    'enhanced_reactions': {
        'name': 'Enhanced Reactions',
        'base': 'Per',
        'desc': ("|mEnhanced Reactions|n is a mutation that gives the character "
                 "a unnaturally fast reaction time. This mutation improves the"
                 "chance to dodge and block attacks,  and avoid certain traps."),
        'prerequisites': None,
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'visual_sensitivity': {
        'name': 'Visual Sensitivity',
        'base': 'Per',
        'desc': ("|mVisual Sensitivity|n is a mutation that gives the character "
                 "a unnaturally sensitive sense of vision. At high enough levels "
                 "the character wil gain access to low light vision, infrared "
                 "vision, and x-ray vision. This mutation comes at the cost of "
                 "being vulnerable to certain attack types involving energy."),
        'prerequisites': None,
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'sonic_sensitivity': {
        'name': 'Sonic Sensitivity',
        'base': 'Per',
        'desc': ("|mSonic Sensitivity|n is a mutation that gives the character "
                 "a unnaturally sensitive sense of hearing. At high enough levels "
                 "the character can develop talents like echo location, sonic "
                 "attacks, etc. This mutation comes at the cost of being "
                 "vulnerable to certain attack types involving sound."),
        'prerequisites': None,
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'tactile_sensitivity': {
        'name': 'Tactile Sensitivity',
        'base': 'Per',
        'desc': ("|mTactile Sensitivity|n is a mutation that gives the character "
                 "a unnaturally sensitive sense of touch. This mutation comes "
                 "at the cost of being vulnerable to certain attack types."),
        'prerequisites': None,
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'olefactory_sensitivity': {
        'name': 'Olefactory Sensitivity',
        'base': 'Per',
        'desc': ("|mOlefactory Sensitivity|n is a mutation that gives the character "
                 "a unnaturally sensitive sense of taste and smell. This "
                 "mutation comes at the cost of being vulnerable to certain "
                 "attack types."),
        'prerequisites': None,
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'magnetic_sensitivity': {
        'name': 'Magnetic Sensitivty',
        'base': 'Per',
        'desc': ("|mMagnetic Sensitivty|n is a mutation that gives the character "
                 "the ability to sense magnetic fields. Characters with this"
                 "power rarely get lost."),
        'prerequisites': None,
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'chromatic_flesh': {
        'name': 'Chromatic Flesh',
        'base': 'Per',
        'desc': ("|mChromatic Flesh|n is a mutation that gives the character "
                 "the ability to alter the surface apperance of their flesh. "
                 "This mutation unlocks talents like natural camo."),
        'prerequisites': None,
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'extrasensory_perception': {
        'name': 'Extrasensory Perception',
        'base': 'Per',
        'desc': ("|mExtrasensory Perception|n is a mutation that gives the "
                 "character the ability to perceive outside the normal set of "
                 "senses. It is related to psychokinesis and pychoprojection "
                 "in that all three of these mutations are psionic type powers. "
                 "This mutation unlocks a number of talents, but comes at the "
                 "cost of making the character more vulnerable to certain "
                 "environments and attack types.",
        'prerequisites': None,
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    # Charisma based mutations
    'psychokinesis': {
        'name': 'Psychokinesis',
        'base': 'Cha',
        'desc': ("|mPsychokinesis|n is a mutation that gives the character "
                 "the ability to interact with physical systems with their will. "
                 "At higher levels, they can attack by throwing small objects, "
                 "unlock doors, or even fly (if their mass is low enough). "
                 "This mutation unlocks a number of talents."),
        'prerequisites': 'mutations.extrasensory_perception': 200,
        'starting_score': 0,
        'range': {'min': 0, 'max': 1000}
    },
    'psychoprojection': {
        'name': 'Psychoprojection',
        'base': 'Cha',
        'desc': ("|mPsychoprojection|n is a mutation that gives the character "
                 "the ability to interact with non-physical systems with their "
                 "will. At higher levels, they can unlock a number of talents, "
                 "such as astral projection, atomic phasing, invisibility, etc."),
        'prerequisites': 'mutations.extrasensory_perception': 200,
        'starting_score': 0,
        'range': {'min': 0, 'max': 1000}
    },
    'malleable_flesh': {
        'name': 'Chromatic Flesh',
        'base': 'Cha',
        'desc': ("|mChromatic Flesh|n is a mutation that gives the character "
                 "the ability to alter the shape and texture of their own"
                 "flesh with the force of their will. This mutation unlocks"
                 "certain talents such as disguise and aids natural camo."),
        'prerequisites': {'mutations.rubber_body.actual': 200},
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    }
}

# mutation groupings by ability scores
ALL_MUTATIONS = ('extreme_flexibility', 'rubber_body', 'improved_balance',
              'bone_density', 'increased_regeneration',
              'regrow_limbs', 'extra_limbs', 'wings', 'tail', 'armored_hide',
              'bladed_body', 'sharp_claws', 'limb_length', 'gut_biome',
              'poison_bite', 'poison_spit', 'sticky_spit', 'hold_breath',
              'gills', 'webbed_feet', 'slow_aging', 'sonic_attack',
              'enhanced_reactions', 'visual_sensitivity', 'sonic_sensitivity',
	          'tactile_sensitivity', 'olefactory_sensitivity',
              'magnetic_sensitivity', 'chromatic_flesh',
              'extrasensory_perception', 'psychokinesis', 'psychoprojection',
              'malleable_flesh')
DEX_MUTATIONS = [m for m in ALL_MUTATIONS if _MUTATION_DATA[m]['base'] == 'Dex']
STR_MUTATIONS = [m for m in ALL_MUTATIONS if _MUTATION_DATA[m]['base'] == 'Str']
VIT_MUTATIONS = [m for m in ALL_MUTATIONS if _MUTATION_DATA[m]['base'] == 'Vit']
PER_MUTATIONS = [m for m in ALL_MUTATIONS if _MUTATION_DATA[m]['base'] == 'Per']
CHA_MUTATIONS = [m for m in ALL_MUTATIONS if _MUTATION_DATA[m]['base'] == 'Cha']

def initialize_mutations(character):
    """
    Sets up a character or NPC's initial mutations. Many of these will start at 0
    and require prerequisites to be met, quests to be completed, and/or events
    to happen to or near the character or NPC to trigger the mutation that leads
    to the discovery of that mutation.

    Args:
        character (Character): the character being initialized
    """
    for mutation, data in _MUTATION_DATA.items():
        if data['starting_score'] != 0:
            if data['starting_score'] in ('Dex', 'Str', 'Vit', 'Per', 'Cha'):
                character.mutations.add(
                    key=mutation,
                    type='static',
                    base=character.ability_scores[data['base']].actual,
                    mod=0,
                    name=data['name'],
                    extra=[data['range']]
                )
            elif data['starting_score'] == {'rarsc': 100}:
                character.mutations.add(
                    key=mutation,
                    type='static',
                    base=rarsc(100),
                    mod=0,
                    name=data['name'],
                    extra=[data['range']]
                )
            else:
                logger.log_trace("Initialization of one of the mutations failed")

def load_mutation(mutation):
    """
    Retrieves an instance of a 'mutation' class.

    Args:
        mutation (string): case sensitive mutation name

    Returns:
        (mutation): instance of a named mutation
    """
    mutation = mutation.lower()
    if mutation in ALL_MUTATIONS:
        return Mutation(**_MUTATION_DATA[mutation])
    else:
        raise MutationException('Invalid mutation name.')

# TODO: Add a function for discoving new mutations

class Mutation(object):
    """Represents a mutation's display attributes for use in help files.
    Args:
        name (str): display name for mutation
        desc (str): description of mutation
    """
    def __init__(self, name, desc, base):
        self.name = name
        self.desc = desc
        self.base = base
