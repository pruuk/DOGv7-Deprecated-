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

class TalentException(Exception):
    "Called when a talent related function fails somehow"
    def __init__(self, msg):
        self.msg = msg

# storing talent data in a dictionary seperated by related ability score
_TALENT_DATA = {
    # Dexterity based talents
    'footwork': {
        'name': 'Footwork',
        'base': 'Dex',
        'desc': ("|mFootwork|n is the measure of how well a character or NPC "
                 "moves on their feet. This skill is primarily used in combat "
                 "to determine positional advantage relative to an opponent or "
                 "to put the character/NPC into position to strike using the "
                 "preferred distance for their style of attack. Footwork is "
                 "also used to determine balance checks foir things like "
                 "walking on a narrow ledge"),
        'prerequisites': None,
        'starting_score': 'Dex'
    },
    'melee_weapons': {
        'name': 'Melee Weapons Combat',
        'base': 'Dex',
        'desc': ("|mMelee Weapons Combat|n is the measure of how well a "
                 "character or NPC attacks with a melee weapon. This skill is "
                 "primarily used in combat to determine if an opponent can be "
                 "hit by an attack. It also has some effect on the att speed of "
                 "the character or NPC, though that is primarily determined by "
                 "the speed of the weapon being wielded and the encumberance "
                 "of the wielder."),
        'prerequisites': None,
        'starting_score': 'Dex'
    },
    'ranged_weapons': {
        'name': 'Ranged Weapons Combat',
        'base': 'Dex',
        'desc': ("|mRanged Weapons Combat|n is the measure of how well a "
                 "character or NPC attacks with a ranged weapon. This skill is "
                 "primarily used in combat to determine if an opponent can be "
                 "hit by an attack. It also has some effect on the att speed of "
                 "the character or NPC, though that is primarily determined by "
                 "the speed of the weapon being wielded and the encumberance "
                 "of the wielder."),
        'prerequisites': None,
        'starting_score': 'Dex'
    },
    'unarmed_striking': {
        'name': 'Unarmed Striking',
        'base': 'Dex',
        'desc': ("|mUnarmed Striking|n is the measure of how well a character"
                 "or NPC attacks with their bare hands or with natural weapons "
                 "like claws, horns, teeth, hooves, etc. This skill is "
                 "primarily used in combat to determine if an opponent can be "
                 "hit by an attack. It also has some effect on the att speed "
                 "of the character or NPC, though that is primarily determined "
                 "by the encumberance of the wielder. It also affects damage "
                 "for unarmed strikes indirectly."),
        'prerequisites': None,
        'starting_score': 'Dex'
    },
    'grappling': {
        'name': 'Grappling',
        'base': 'Dex',
        'desc': ("|mGrappling|n is the measure of how well a character"
                 "or NPC attacks with attacks that involve wrestling, throws, "
                 "submissions, trips, and other uses of leverage to gain an "
                 "advantage in position in close combat. Bashing with a shield "
                 "is considered part of grappling, as are constricting attacks "
                 "such as those employed by a large snake."),
        'prerequisites': None,
        'starting_score': 'Dex'
    },
    'sneak': {
        'name': 'Sneak',
        'base': 'Dex',
        'desc': ("|mSneak|n is the talent of remaining unseen and unheard by "
                 "enemies while moving stealthily. It also affects checks "
                 "like doing sleight of hand, pickpocking, concealing weapons "
                 "for surprise attacks. Sneak also affects how easily a "
                 "character or NPC can be tracked."),
        'prerequisites': None,
        'starting_score': 'Dex'
    },
    'fly': {
        'name': 'Fly',
        'base': 'Dex',
        'desc': ("|mFly|n is the talent that allows controlled flight through "
                 "the air. In order to enable fly, the character must have a "
                 "number of mutations. There are two paths to flying: winged "
                 "flight and psychokinesis based flight."),
        'prerequisites': {'mutations.wings.actual': 300,
                         'mutations.bone_density.actual': '<75',
                         'mutations.tail.actual': 200},
        'starting_score': 0
    },
    # Strength based talents
    'climbing': {
        'name': 'Climbing',
        'base': 'Str',
        'desc': ("|mClimb|n represents the proficiency in climbing difficult "
                 "slopes or sheer walls."),
        'prerequisites': None,
        'starting_score': 'Str'
    },
    # Vitality based skills
    'swimming': {
        'name': 'Swimming',
        'base': 'Vit',
        'desc': ("|mSwimming|n is the measure of how well a character or NPC "
                 "is able to move through the water. It also determines how well "
                 "they are able to position themselves ion underwater combat."),
        'prerequisites': None,
        'starting_score': 'Vit'
    },
    # Perception based talents
    'appraise': {
        'name': 'Appraise',
        'base': 'Per',
        'desc': ("|mAppraise|n is the ability to determine an accurate value "
                 "of an item's worth and abilities."),
        'prerequisites': None,
        'starting_score': 'Per'
    },
    'tracking': {
        'name': 'Tracking',
        'base': 'Per',
        'desc': ("|mAppraise|n is the ability to determine the direction and "
                 "type of tracks in a room. This is affected by the type of "
                 "terrain in the room and the time since the tracks were left."),
        'prerequisites': None,
        'starting_score': 'Per'
    },
    'lockpicking': {
        'name': 'Lock Picking',
        'base': 'Per',
        'desc': ("|mLock Pick|n represents the proficiency in manipulating "
                 "pins and tumblers to open a lock without a key."),
        'prerequisites': None,
        'starting_score': 'Per'
    },
    'sense_danger': {
        'name': 'Sense Danger',
        'base': 'Per',
        'desc': ("|mSense Danger|n is the ability to assess the level of "
                 "danger that enemies and situations possess."),
        'prerequisites': None,
        'starting_score': 'Per'
    },
    'first_aid': {
        'name': 'First Aid',
        'base': 'Per',
        'desc': ("|mFirst Aid|n is the practice of applying a quick fix to "
                 " wounds and other ailments. A character who practices "
                 "medicine can improve healing rate or adverse conditions, or "
                 "slow certain poisons."),
        'prerequisites': None,
        'starting_score': 'Per'
    },
    'blacksmithing': {
        'name': 'Blacksmithing',
        'base': 'Per',
        'desc': ("|mBlacksmithing|n is the craft of creating and repairing "
                 "metal items, equipment, and components. A character who "
                 "practices blacksmithing can craft armor and weapons if they "
                 "have the correct components or repair existing metal items."),
        'prerequisites': None,
        'starting_score': 'Per'
    },
    'leatherworking': {
        'name': 'Leatherworking',
        'base': 'Per',
        'desc': ("|mLeatherworking|n is the craft of creating and repairing "
                 "leather items, equipment, and components. A character who "
                 "practices leatherworking can craft armor, weapons and bags if "
                 "they have the correct components or repair existing items."),
        'prerequisites': None,
        'starting_score': 'Per'
    },
    'woodworking': {
        'name': 'Woodworking',
        'base': 'Per',
        'desc': ("|mWoodworking|n is the craft of creating and repairing "
                 "wood items, equipment, and components. A character who "
                 "practices woodworking can craft bows, arrows, and handles if "
                 "they have the correct components or repair existing items."),
        'prerequisites': None,
        'starting_score': 'Per'
    },
    'tailoring': {
        'name': 'Tailoring',
        'base': 'Per',
        'desc': ("|mTailoring|n is the craft of creating and repairing "
                 "cloth items, equipment, and components. A character who "
                 "practices tailoring can craft clothing, bags, and components "
                 "if they have the correct components or repair existing items."),
        'prerequisites': None,
        'starting_score': 'Per'
    },
    'alchemy': {
        'name': 'Alchemy',
        'base': 'Per',
        'desc': ("|mAlchemy|n is the craft of creating potions, poultices, and "
                 "other healing items and components. A character who practices "
                 "alchemy can craft potions and components need for other skills "
                 "if they have the correct components or repair existing items."),
        'prerequisites': None,
        'starting_score': 'Per'
    },
    'alter_appearance': {
        'name': 'Alter Appearance',
        'base': 'Per',
        'desc': ("|mAlter Appearance|n is a talent that gives the character "
                 "the ability to alter their apperance. At high levels, they "
                 "can impersonate others, become forgettable, or become highly "
                 "attractive. This talent potentially unlocks a number of"
                 "talents related to appearance. This talent can be used "
                 "without regents if you have a advanced mutation in chromatic "
                 "flesh. This talent also enhances camoflauge and sneak."),
        'prerequisites': None,
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'light_attack': {
        'name': 'Light Attack',
        'base': 'Per',
        'desc': ("|mLight Attack|n is a talent that gives the character "
                 "the ability to produce incribly bright flashes of light, "
                 "potentially blinding others. This talent requires a high "
                 "level of the chromatic flesh mutation."),
        'prerequisites': {'mutations.chromatic_flesh': 300},
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'invisibility': {
        'name': 'Invisibility',
        'base': 'Per',
        'desc': ("|mInvisibility|n is a talent that gives the character "
                 "the ability to manipulate their body and the light in the "
                 "room so well they become invisible to most other beings."),
        'prerequisites': {'talents.light_attack': 400,
                          'talents.atomic_phasing': 200},
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'echo_location': {
        'name': 'Echo Location',
        'base': 'Per',
        'desc': ("|mEcho Location|n is a talent that gives the character "
                 "an ability to produce sounds and then navigate without using "
                 "their eyes. This can be affected by noisy areas but is very "
                 "effective underwater and underground. It also negates the "
                 "use of invisibility by other beings."),
        'prerequisites': {'mutations.sonic_sensitivity': 300},
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    # Charisma based talents
    'sonic_attack': {
        'name': 'Sonic Attack',
        'base': 'Cha',
        'desc': ("|mSonic Attack|n is a talent that gives the character "
                 "the ability to produce sounds in ranges and volumes that can "
                 "do damage."),
        'prerequisites': {'mutations.sonic_sensitivity': 200},
        'starting_score': 0,
        'range': {'min': 0, 'max': 500}
    },
    'husbandry': {
        'name': 'Husbandry',
        'base': 'Cha',
        'desc': ("|mHusbandry|n is the innate feat of being able to calm "
                 "and communicate non-verbally with a creature of less-than "
                 "humanoid intelligence."),
        'prerequisites': None,
        'starting_score': 'Cha'
    },
    'barter': {
        'name': 'Barter',
        'base': 'Cha',
        'desc': ("|mBarter|n is the the timeless art of negotiation in an "
                 "effort to lower the price on an item for sale. This ability "
                 "affects and is affected by previous interactions with the "
                 "same merchant."),
        'prerequisites': None,
        'starting_score': 'Cha'
    },
    'leadership': {
        'name': 'Leadership',
        'base': 'Cha',
        'desc': ("|mLeadership|n is the natural ability to raise the spirits "
                 "and morale of those around you. It also enhances grouping."),
        'prerequisites': None,
        'starting_score': 'Cha'
    },
    'telekensis': {
        'name': 'Telekensis',
        'base': 'Cha',
        'desc': ("|mTelekensis|n is a talent that gives the character "
                 "the ability to move objects with the force of their will. "
                 "This can be used to enable attacks similar to throwing "
                 "weapons, attacks to confer a positional advantage (similar "
                 "in outcome to grappling), or to bring loose objects to the "
                 "character from a distance."),
        'prerequisites': {'mutations.psychokinesis': 200},
        'starting_score': 0,
        'range': {'min': 0, 'max': 1000}
    },
    'pyrokensis': {
        'name': 'Pyrokensis',
        'base': 'Cha',
        'desc': ("|mPyrokensis|n is a talent that gives the character "
                 "the ability to transfer energy from one place to another. "
                 "In practice, this means they can attack with fire, electricity, "
                 "affect the magnetically sensitive. This mutation unlocks a "
                 "number of attacks and commands."),
        'prerequisites': {'mutations.psychokinesis': 300},
        'starting_score': 0,
        'range': {'min': 0, 'max': 1000}
    },
    'atomic_phasing': {
        'name': 'Atomic Phasing',
        'base': 'Cha',
        'desc': ("|mAtomic Phasing|n is a talent that gives the character "
                 "the ability to control the motion of their own atoms so "
                 "well that they can pass through doors and other solid objects, "
                 "have attacks pass through their body, or travel underground. "
                 "Using this power can be very risky if a check is failed. "
                 "This talent unlocks a number of commands."),
        'prerequisites': {'mutations.psychoprojection': 700,
                          'mutations.psychokinesis': 500},
        'starting_score': 0,
        'range': {'min': 0, 'max': 1000}
    },
    'ethereal_body': {
        'name': 'Ethereal Body',
        'base': 'Cha',
        'desc': ("|mEthereal Body|n is a talent that gives the character "
                 "the ability to alter the nature of their own body's matter to "
                 "the point that they are virtually invulnerable to physical "
                 "attacks. This allows means they cannot attack physically "
                 "and moving around costs Conviction instead of Stamina. "
                 "Running out of Conviction when in this form results in death. "
                 "Characters in this form can only be tracked by characters or "
                 "NPCs with Magnetic Sensitivity and Tracking. This talent "
                 "unlocks a number of commands."),
        'prerequisites': {'talents.atomic_phasing': 800},
        'starting_score': 0,
        'range': {'min': 0, 'max': 1000}
    },
    'mental_domination': {
        'name': 'Mental Domination',
        'base': 'Cha',
        'desc': ("|mMental Domination|n is a talent that gives the character "
                 "the ability to control NPCs in some situations. While this is "
                 "useful, failing a check will automatically cause the NPC and "
                 "any other NPCs that witness the domination to hate the "
                 "character forever. This talent unlocks a number of commands. "
                 "Maintaining domination over another being drains conviction "
                 "over time."),
        'prerequisites': {'mutations.psychoprojection': 600,
                          'mutations.extrasensory_perception': 700},
        'starting_score': 0,
        'range': {'min': 0, 'max': 1000}
    },
}

# talent groupings by associated ability score
ALL_TALENTS = (
    'footwork', 'melee_weapons', 'ranged_weapons', 'unarmed_striking',
    'sneak', 'grappling', 'fly', 'climbing', 'swimming', 'appraise', 'tracking',
    'lockpicking', 'sense_danger', 'first_aid', 'blacksmithing',
    'leatherworking', 'woodworking', 'tailoring', 'alchemy', 'alter_appearance',
    'light_attack', 'invisibility', 'echo_location', 'sonic_attack', 'husbandry',
    'barter', 'leadership', 'telekensis', 'pyrokensis', 'atomic_phasing',
    'ethereal_body', 'mental_domination'
)
DEX_TALENTS = [t for t in ALL_TALENTS if _TALENT_DATA[t]['base'] == 'Dex']
STR_TALENTS = [t for t in ALL_TALENTS if _TALENT_DATA[t]['base'] == 'Str']
VIT_TALENTS = [t for t in ALL_TALENTS if _TALENT_DATA[t]['base'] == 'Vit']
PER_TALENTS = [t for t in ALL_TALENTS if _TALENT_DATA[t]['base'] == 'Per']
CHA_TALENTS = [t for t in ALL_TALENTS if _TALENT_DATA[t]['base'] == 'Cha']

def apply_talents(character):
    """
    Sets up a character's initial talent traits.

    Args:
        talent (string): case sensitive talent name

    Returns:
        (Talent): instance of the named talent
    """
    character.talents.clear()
    for talent, data in _TALENT_DATA.items():
        character.talents.add(
            key=talent,
            type='static',
            base=character.ability_scores[data['base']].actual,
            mod=0,
            name=data['name'],
            extra={'learn' : 0}
        )


def load_talent(talent):
    """
    Retrieves an instance of the 'Talent' class.

     Args:
        talent (str): case insensitive talent name
    Returns:
        (Talent): instance of the named Talent
    """
    talent = talent.lower()
    if talent in ALL_TALENTS:
        return Talent(**_TALENT_DATA[talent])
    else:
        raise TalentException('Invalid talent name.')

# TODO: Add in a validation func
# TODO: Add in function for talent increasing due to learning

class TALENT(object):
    """Represents a Talent's display attributes for use in help files
    Args:
        name (str): display name for talent
        desc (str): description of talent
    """
    def __init__(self, name, desc, base):
        self.name = name
        self.desc = desc
        self.base = base
