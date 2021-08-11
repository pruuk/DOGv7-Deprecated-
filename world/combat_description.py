# -*- coding: utf-8 -*-
"""
This file contains dictionmaries of common attacks or defenses for use in
describing combat. It also contains functions for parsing those descriptions.
These functions will be called by functions in the combat_messaging file.
"""
import random
from evennia.utils.logger import log_file

# general purpose lists and dictionaries
damage_hit_locations = [
'jaw', 'nose', 'temple', 'eyebrow', 'forehead', 'right ear', \
'left ear', 'neck', 'right shoulder', 'left shoulder', 'torso', \
'chest', 'upper back', 'lower back', 'waist', 'right arm', 'left arm', \
'right Leg', 'left leg', 'right foot', 'left foot', 'right ankle', 'left ankle', \
'right hand', 'left hand', 'left calf', 'right calf', 'liver']

# unarmed strikes normal lists
generic_unarmed_strike_normal = {
'Actor' :
    [
    "land a vicious headbutt to",
    "land a series of hammer fists to",
    "land an overhand right to",
    "fire an overhand left at",
    "punch",
    "kick",
    "knee"
    ],
'Actee' :
    [
    "lands a vicious headbutt to",
    "lands a series of hammer fists to",
    "lands an overhand right to",
    "fires an overhand left at",
    "punches",
    "kicks",
    "knees"
    ],
'Observer' :
    [
    "lands a vicious headbutt to",
    "lands a series of hammer fists to",
    "lands an overhand right to",
    "fires an overhand left at",
    "punches",
    "kicks",
    "knees"
    ]
}
beginner_unarmed_strike_normal = {
'Actor' :
    [
    "land a left front kick to",
    "karate chop",
    "spin your arms wildly, landing a bolo punch on",
    "connect with a looping haymaker to",
    "deliver a stinging slap to",
    "leap into the air head-first at",
    "spin around awkwardly, landing an inadvertent headbutt on"
    ],
'Actee' :
    [
    "lands a left front kick to",
    "karate chops",
    "spins their arms wildly, landing a bolo punch on",
    "connects with a looping haymaker to",
    "delivers a stinging slap to",
    "leaps into the air head-first at",
    "spins around awkwardly, landing an inadvertent headbutt on"
    ],
'Observer' :
    [
    "lands a left front kick to",
    "karate chops",
    "spins their arms wildly, landing a bolo punch on",
    "connects with a looping haymaker to",
    "delivers a stinging slap to",
    "leaps into the air head-first at",
    "spins around awkwardly, landing an inadvertent headbutt on"
    ]
}
intermediate_unarmed_strike_normal = {
'Actor':
    [
    "lunge forward with an extended elbow thrust to",
    "repeatedly knee to",
    "fire off a stiff jab at",
    "wind up and land a huge left uppercut to",
    "shuffle forward and palm strike",
    "feint a jab and follow up with a left hook to",
    "feint an uppercut and then land a right hook to",
    "spin around, landing a big backhanded bitchslap to",
    "land a left foot sidekick to",
    "fire a right foot sidekick at",
    "deliver a swift right front kick at"
    ],
'Actee':
    [
    "lunges forward with an extended elbow thrust to",
    "repeatedly knees to",
    "fires off a stiff jab at",
    "winds up and lands a huge left uppercut to",
    "shuffles forward and palm strikes",
    "feints a jab and follows up with a left hook to",
    "feints an uppercut and then lands a right hook to",
    "spins around, landing a big backhanded bitchslap to",
    "lands a left foot sidekick to",
    "fires a right foot sidekick at",
    "delivers a swift right front kick at"
    ],
'Observer':
    [
    "lunges forward with an extended elbow thrust to",
    "repeatedly knees to",
    "fires off a stiff jab at",
    "winds up and lands a huge left uppercut to",
    "shuffles forward and palm strikes",
    "feints a jab and follows up with a left hook to",
    "feints an uppercut and then lands a right hook to",
    "spins around, landing a big backhanded bitchslap to",
    "lands a left foot sidekick to",
    "fires a right foot sidekick at",
    "delivers a swift right front kick at"
    ]
}
advanced_unarmed_strike_normal = {
'Actor':
    [
    "fire off a swift thrust kick at",
    "land a combination of quick punches on",
    "connect with a swift knee to",
    "land a flying knee on",
    "spin around and lands a spinning backfist to",
    "jump in the air and land a downward elbow strike to",
    "spin counter-clockwise and land a spinning elbow to",
    "leap into the air to land a superman punch on",
    "do a switchkick to",
    "land a spinning roundhouse kick to",
    "show impressive flexibility, landing an axe kick to"
    ],
'Actee':
    [
    "fires off a swift thrust kick at",
    "lands a combination of quick punches on",
    "connects with a swift knee to",
    "lands a flying knee on",
    "spins around and lands a spinning backfist to",
    "jumps in the air and lands a downward elbow strike to",
    "spins counter-clockwise and lands a spinning elbow to",
    "leaps into the air to land a superman punch on",
    "does a switchkick to",
    "lands a spinning roundhouse kick to",
    "shows impressive flexibility, landing an axe kick to"
    ],
'Observer':
    [
    "fires off a swift thrust kick at",
    "lands a combination of quick punches on",
    "connects with a swift knee to",
    "lands a flying knee on",
    "spins around and lands a spinning backfist to",
    "jumps in the air and lands a downward elbow strike to",
    "spins counter-clockwise and lands a spinning elbow to",
    "leaps into the air to land a superman punch on",
    "does a switchkick to",
    "lands a spinning roundhouse kick to",
    "shows impressive flexibility, landing an axe kick to"
    ]
}
master_unarmed_strike_normal = {
'Actor':
    [
    "stiffen your fingers and deliver a crane beak strike to",
    "perform an eagle claw attack on",
    "precisely target a leopard punch at",
    "hop in the air, performing a wushu butterfly kick at",
    "feint a strait kick and turn it into a crescent kick at",
    "do a fancy backflip to land an uppercut elbow to",
    "jab-step to the left, then deliver a tight right uppercut at",
    "cartwheel left, then roll forward to deliver a wing chun double punch on",
    "spin halfway around, delivering a Ushiro Geri kick to",
    "sumersault and flow into a mouth of hand strike at",
    "shuffle forward with quick steps and deliver a one inch punch to",
    "fly through the air, delivering an awesome hook kick to",
    "wheel around, landing a reverse roundhouse to",
    "jump and fire off a scissor kick at",
    "plant your back foot and deliver a question mark kick at"
    ],
'Actee':
    [
    "stiffens their fingers and delivers a crane beak strike to",
    "performs an eagle claw attack on",
    "precisely targets a leopard punch at",
    "hops in the air, performing a wushu butterfly kick at",
    "feints a strait kick and turns it into a crescent kick at",
    "does a fancy backflip to land an uppercut elbow to",
    "jab-steps to the left, then delivers a tight right uppercut at",
    "cartwheels left, then rolls forward to deliver a wing chun double punch on",
    "spins halfway around, delivering a Ushiro Geri kick to",
    "sumersaults and flows into a mouth of hand strike at",
    "shuffles forward with quick steps and delivers a one inch punch to",
    "flies through the air, delivering an awesome hook kick to",
    "wheels around, land a reverse roundhouse to",
    "jumps and fires off a scissor kick at",
    "plants their back foot and delivers a question mark kick at"
    ],
'Observer':
    [
    "stiffens their fingers and delivers a crane beak strike to",
    "performs an eagle claw attack on",
    "precisely targets a leopard punch at",
    "hops in the air, performing a wushu butterfly kick at",
    "feints a strait kick and turns it into a crescent kick at",
    "does a fancy backflip to land an uppercut elbow to",
    "jab-steps to the left, then delivers a tight right uppercut at",
    "cartwheels left, then rolls forward to deliver a wing chun double punch on",
    "spins halfway around, delivering a Ushiro Geri kick to",
    "sumersaults and flows into a mouth of hand strike at",
    "shuffles forward with quick steps and delivers a one inch punch to",
    "flies through the air, delivering an awesome hook kick to",
    "wheels around, land a reverse roundhouse to",
    "jumps and fires off a scissor kick at",
    "plants their back foot and delivers a question mark kick at"
    ]
}

# unarmed strikes index for dictionary
unarmed_strike_normal_index = {
0 : generic_unarmed_strike_normal,
1 : beginner_unarmed_strike_normal,
2 : intermediate_unarmed_strike_normal,
3 : advanced_unarmed_strike_normal,
4 : master_unarmed_strike_normal
}

# dodge dict
dodge_dict = {
'Actor' :
    [
    "deftly slide to the right, then pivot to the left away from the attack of",
    "roll backwards, away from the attack of",
    "take a small step back, narrowly avoiding the attack of",
    "use the momentum of your last attack to slide past the attack of",
    "dodge the attack of",
    "juke the pants off of",
    "drop to your knees, easily avoiding the haphazrd attack of",
    "take several quick steps to the right, avoiding",
    "take four quick steps to the left, avoiding",
    "flow to the side, dodging",
    "stumble over a rock, luckily avoiding the strikes of",
    "stand still, faking out the complicated attack of",
    "leap into the air, hopping over the attack of",
    "lean over backwards like a limbo artist, avoiding the blows of",
    "slide backwards and to the right, avoiding",
    "mince-step backwards and to the left, circumventing the blows of"
    ],
'Actee' :
    [
    "deftly slides to the right, then pivots to the left away from",
    "rolls backwards, away from",
    "takes a small step back, narrowly avoiding",
    "uses the momentum of their last attack to slide past",
    "dodges",
    "jukes the pants off of you, dodging",
    "drops to their knees, easily avoiding",
    "takes several quick steps to the right, avoiding",
    "takes four quick steps to the left, avoiding",
    "flows to the side, dodging",
    "stumbles over a rock, luckily avoiding",
    "stands still, faking out the complicated moves of",
    "leaps into the air, hopping over",
    "leans over backwards like a limbo artist, avoiding",
    "slides backwards and to the right, avoiding",
    "mince-steps backwards and to the left, circumventing"
    ],
'Observer' :
    [
    "deftly slides to the right, then pivots to the left away from",
    "rolls backwards, away from",
    "takes a small step back, narrowly avoiding",
    "uses the momentum of their last attack to slide past",
    "dodges",
    "jukes the pants off of you, dodging",
    "drops to their knees, easily avoiding",
    "takes several quick steps to the right, avoiding",
    "takes four quick steps to the left, avoiding",
    "flows to the side, dodging",
    "stumbles over a rock, luckily avoiding",
    "stands still, faking out the complicated moves of",
    "leaps into the air, hopping over",
    "leans over backwards like a limbo artist, avoiding",
    "slides backwards and to the right, avoiding",
    "mince-steps backwards and to the left, circumventing"
    ]
}

block_dict = {
'Actor' :
    [
    "step to the side and use an aborted kick to block the attack of",
    "use your shoulder to disrupt the balance and attack of",
    "deftly use the edge of your hand to redirect the attack of",
    "lunge forward, grappling the wrist of",
    "swirl the cloth of your sleeve out, entangling the attempted attack of",
    "block the blow of",
    "fend off the wild attacks of",
    "use your forearm and a nifty step to the left to obstruct the blow of",
    "feint with stiffened fingers at the eyes, flabbergasting",
    "partially block, while simutaneously tuggling at the clothing of"
    ],
'Actee' :
    [
    "steps to the side and uses an aborted kick to block",
    "uses their shoulder to disrupt the balance of",
    "deftly uses the edge of their hand to redirect",
    "lunges forward, grappling your wrist, aborting",
    "swirls the cloth of their sleeve out, entangling",
    "block",
    "fends off the wild attacks of",
    "uses their forearm and a nifty step to the left to obstruct the blow of",
    "feints with stiffened fingers at the eyes, flabbergasting",
    "partially blocks, while simutaneously tuggling at the clothing of"
    ],
'Observer' :
    [
    "steps to the side and uses an aborted kick to block",
    "uses their shoulder to disrupt the balance of",
    "deftly uses the edge of their hand to redirect",
    "lunges forward, grappling your wrist, aborting",
    "swirls the cloth of their sleeve out, entangling",
    "block",
    "fends off the wild attacks of",
    "uses their forearm and a nifty step to the left to obstruct the blow of",
    "feints with stiffened fingers at the eyes, flabbergasting",
    "partially blocks, while simutaneously tuggling at the clothing of"
    ]
}

# damage descriptions based upon life remaining
def return_damage_gradient_text(perc_of_life_taken):
    """
    This function takes in a percentage and returns a textual description of how
    hard the hit was.
    """
    log_file("start of return damage gradient func", filename='combat_step.log')
    if perc_of_life_taken > 95:
        return '|500obliterated|n'
    elif perc_of_life_taken > 89:
        return '|400nearly obliterated|n'
    elif perc_of_life_taken > 55:
        return '|300critically wounded|n'
    elif perc_of_life_taken > 34:
        return '|200brutally wounded|n'
    elif perc_of_life_taken > 21:
        return '|100severely wounded|n'
    elif perc_of_life_taken > 13:
        return '|420badly wounded|n'
    elif perc_of_life_taken > 8:
        return '|320wounded|n'
    elif perc_of_life_taken > 5:
        return '|Ylightly wounded|n'
    elif perc_of_life_taken > 3:
        return '|ynicked|n'
    elif perc_of_life_taken > 2:
        return '|gscratched|n'
    else:
        return '|Gtickled|n'


def return_hit_location():
    """
    Returns a random body part for a strike to land on.
    """
    log_file("start of return hit loc func", filename='combat_step.log')
    # TODO: Make this more sophisticated later
    return random.choice(damage_hit_locations)


def return_unarmed_damage_normal_text(pcs_and_npcs_in_room, damage):
    """
    This function returns a random choice from the dict of textual descriptions
    for unarmed combat strikes w/o any natural weapon mutations.
    """
    log_file("Start of return unarmed damage normal text func", \
             filename='combat_step.log')
    log_file(f"var check - toons in room: {pcs_and_npcs_in_room} damage: {damage}", \
             filename='combat_step.log')
    damage_texts_dict = {'Actor': '', 'Actee': '', 'Observers': ''}
    attacker = pcs_and_npcs_in_room['Actor']
    defender = pcs_and_npcs_in_room['Actee']
    hit_loc = return_hit_location()
    damage_text = return_damage_gradient_text(damage/defender.traits.hp.current * 100)
    log_file(f"attacker: {attacker.name} defender: {defender.name} hit loc: {hit_loc} damage: {damage_text}", \
             filename='combat_step.log')
    log_file(f"checking {attacker.name}'s unarmed talent level: {attacker.talents.unarmed_striking.actual}", \
             filename='combat_step.log')
    if attacker.talents.unarmed_striking.actual < 150:
        # attacker is a flailing noob. Choose from generic and beginner attack strings
        log_file(f"{attacker.name}'s unarmed talent level is less than 150.", \
                 filename='combat_step.log')
        index = random.randrange(1)
        log_file(f"index: {index}", filename='combat_step.log')
        log_file(f"attack text dict: {unarmed_strike_normal_index[index]}", \
                 filename='combat_step.log')
        random_index_num = random.randrange(1, len(unarmed_strike_normal_index[index]['Actor']))
        log_file(f"random index: {random_index_num}", filename='combat_step.log')
        final_text_dict = {}
        final_text_dict['Actor'] = unarmed_strike_normal_index[index]['Actor'][random_index_num]
        final_text_dict['Actee'] = unarmed_strike_normal_index[index]['Actee'][random_index_num]
        final_text_dict['Observer'] = unarmed_strike_normal_index[index]['Observer'][random_index_num]
        log_file(f"text_dict: {final_text_dict}", filename='combat_step.log')
    else:
        log_file("Somethign went wrong in combat messaging - return unarmed damage normal text.", \
                 filename='error.log')
        log_file(f"attacker's unarmed talent level: {attacker.talents.unarmed_striking.actual}", \
                 filename='combat_step.log')
    return final_text_dict, hit_loc, damage_text


def return_dodge_text(pcs_and_npcs_in_room):
    """
    This function returns a random choice from the dict of textual descriptions
    of a defender dodging an attack.
    """
    log_file("Start of return dodge text func", \
             filename='combat_step.log')
    index = random.randrange(len(dodge_dict['Actor']))
    log_file(f"index: {index}", filename='combat_step.log')
    final_text_dict = {}
    final_text_dict['Actor'] = dodge_dict['Actor'][index]
    final_text_dict['Actee'] = dodge_dict['Actee'][index]
    final_text_dict['Observer'] = dodge_dict['Observer'][index]
    log_file(f"text_dict: {final_text_dict}", filename='combat_step.log')
    return final_text_dict


def return_unarmed_block_text(pcs_and_npcs_in_room):
    """
    This function returns a random choice from the dict of textual descriptions
    of an unarmed combatant blocking an attack.
    """
    log_file("Start of return block text func", \
             filename='combat_step.log')
    index = random.randrange(len(block_dict['Actor']))
    log_file(f"index: {index}", filename='combat_step.log')
    final_text_dict = {}
    final_text_dict['Actor'] = block_dict['Actor'][index]
    final_text_dict['Actee'] = block_dict['Actee'][index]
    final_text_dict['Observer'] = block_dict['Observer'][index]
    log_file(f"text_dict: {final_text_dict}", filename='combat_step.log')
    return final_text_dict
