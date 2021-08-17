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
    "blocks",
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
    "blocks",
    "fends off the wild attacks of",
    "uses their forearm and a nifty step to the left to obstruct the blow of",
    "feints with stiffened fingers at the eyes, flabbergasting",
    "partially blocks, while simutaneously tuggling at the clothing of"
    ]
}

takedown_dict = {
'Actor' : {
    'mount' :
        [
        'take down and mount'
        ],
    'side control' :
        [
        'take down and side control'
        ],
    'top' :
        [
        'take down and sweep'
        ],
    'clinching' :
        [
        'attempt a takedown, but end up in a clinch with',
        'close the distance and clinch with'
        ],
    'normal_failure' :
        [
        'attempt a takedown, but fail against',
        'try and fail to leg trip',
        'try a double leg takedown, but are avoided by the skillful sprawl of',
        'attempt and fail to leg pick'
        ],
    'side controlled' :
        [
        'attempt a takedown, failing miserably against',
        'lose a contested scramble with'
        ],
    'mounted' :
        [
        'attempt a hip toss and end up mounted by',
        'slip and fall onto your back, mounted by'
        ],
},
'Actee' : {
    'mount' :
        [
        'takes down and mounts'
        ],
    'side control' :
        [
        'takes down and side controls'
        ],
    'top' :
        [
        'takes down and sweeps'
        ],
    'clinching' :
        [
        'attempts a takedown, but ends up in a clinch with',
        'closes the distance and clinches with'
        ],
    'normal_failure' :
        [
        'attempts a takedown, but fails against',
        'tries and fails to leg trip',
        'tries a double leg takedown, but fails against',
        'attempts and fails to leg pick'
        ],
    'side controlled' :
        [
        'attempts a takedown, failing miserably against',
        'loses a contested scramble with'
        ],
    'mounted' :
        [
        'attempts a hip toss and ends up mounted by',
        'slips and falls onto their back, mounted by'
        ],
},
'Observer' : {
    'mount' :
        [
        'takes down and mounts'
        ],
    'side control' :
        [
        'takes down and side controls'
        ],
    'top' :
        [
        'takes down and sweeps'
        ],
    'clinching' :
        [
        'attempts a takedown, but ends up in a clinch with',
        'closes the distance and clinches with'
        ],
    'normal_failure' :
        [
        'attempts a takedown, but fails against',
        'tries and fails to leg trip',
        'tries a double leg takedown, but is avoided by the skillful sprawl of',
        'attempts and fails to leg pick'
        ],
    'side controlled' :
        [
        'attempts a takedown, failing miserably against',
        'loses a contested scramble with'
        ],
    'mounted' :
        [
        'attempts a hip toss and ends up mounted by',
        'slips and falls onto their back, mounted by'
        ],
},
}

grappling_change_position_dict = {
    'Actor' :
    [
    'engage in a wild grappling scramble with',
    'roll around, grappling with',
    'try a series of wrestling moves on',
    'execute a series of grappling attacks on',
    'feint an arm bar on',
    'fake a leg lock attempt on',
    'use wrist control to manuever',
    'use a shoulder cammora to roll',
    ],
    'Actee' :
    [
    'engages in a wild grappling scramble with',
    'rolls around, grappling with',
    'tries a series of wrestling moves on',
    'executes a series of grappling attacks on',
    'feints an arm bar on',
    'fakes a leg lock attempt on',
    'uses wrist control to manuever',
    'uses a shoulder cammora to roll',
    ],
    'Observer' :
    [
    'engages in a wild grappling scramble with',
    'rolls around, grappling with',
    'tries a series of wrestling moves on',
    'executes a series of grappling attacks on',
    'feints an arm bar on',
    'fakes a leg lock attempt on',
    'uses wrist control to manuever',
    'uses a shoulder cammora to roll',
    ]
}

grappling_unarmed_strikes_normal = {
'Actor' :
[
"land a series of hammer fists to",
"land an overhand right to",
"fire an overhand left at",
"punch",
"kick",
"knee",
"headbutt",
"elbow",
"shoulder check",
"feint a submission and then strike"
],
'Actee' :
[
"lands a series of hammer fists to",
"lands an overhand right to",
"fires an overhand left at",
"punches",
"kicks",
"knees",
"headbutts",
"elbows",
"shoulder checks",
"feints a submission and then strikes"
],
'Observer' :
[
"lands a series of hammer fists to",
"lands an overhand right to",
"fires an overhand left at",
"punches",
"kicks",
"knees",
"headbutts",
"elbows",
"shoulder checks",
"feints a submission and then strikes"
]
}

ground_grappling_position_index = {
1 : 'tbmount',
2 : 'mount',
3 : 'side control',
4 : 'top',
5 : 'in guard',
6 : 'side controlled',
7 : 'mounted',
8 : 'prmounted'
}
standing_grappling_position_index = {
1 : 'tbstanding',
2 : 'clinching',
3 : 'clinched',
4 : 'standingbt'
}

grappling_submission_dict = {
'tbmount': {
    'Actor' :
    [
    'start locking in a rear naked choke on',
    'use a rotating motion of your body to lock in a bow and arrow choke on',
    'use your position to do a short choke on',
    'do a crucifix choke on',
    'do a neck crank on',
    'apply a twister to the body of',
    'choke',
    'armbar',
    'leglock',
    'toelock',
    'wristlock',
    ],
    'Actee' :
    [
    'starts locking in a rear naked choke on',
    'uses a rotating motion of their body to lock in a bow and arrow choke on',
    'uses their position to do a short choke on',
    'does a crucifix choke on',
    'does a neck crank on',
    'applies a body twister to',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
    'Observer' :
    [
    'starts locking in a rear naked choke on',
    'uses a rotating motion of their body to lock in a bow and arrow choke on',
    'uses their position to do a short choke on',
    'does a crucifix choke on',
    'does a neck crank on',
    'applies a body twister to',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
},

'mount': {
    'Actor' :
    [
    'slip your leg over the neck of your opponent and attempt a straight armbar on',
    'attempt an American Armlock on',
    'lock in a head and arm choke on',
    'do a neck crank on',
    'choke',
    'armbar',
    'leglock',
    'toelock',
    'wristlock',
    ],
    'Actee' :
    [
    'slips their leg over your neck and attempts a straight armbar on',
    'attempts an American Armlock on',
    'locks in a head and arm choke on you',
    'does a neck crank on',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
    'Observer' :
    [
    'slips their leg over the neck of their opponent and attempts a straight armbar on',
    'attempts an American Armlock on',
    'locks in a head and arm choke on',
    'does a neck crank on',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
},
'side control': {
    'Actor' :
    [
    'slip your leg over the neck of your opponent and attempt a straight armbar on',
    'wrap your leg behind the head of your opponent and engage a triagle choke on',
    'do a Kimaura Armlock on your opponent\'s shoulder',
    'do a kneebar on',
    'attempt a D\'Arcee choke on',
    'choke',
    'armbar',
    'leglock',
    'toelock',
    'wristlock',
    ],
    'Actee' :
    [
    'slips their leg over your neck and attempts a straight armbar on',
    'wraps their leg behind your head and engages a triagle choke on ',
    'does a Kimaura Armlock on your shoulder',
    'does a kneebar on',
    'attempts a D\'Arcee choke on',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
    'Observer' :
    [
    'slips their leg over the neck of their opponent and attempts a straight armbar on',
    'wraps their leg behind the head of their opponent and engages a triagle choke on',
    'does a Kimaura Armlock on their opponent\'s shoulder to submit',
    'does a kneebar on',
    'attempts a D\'Arcee choke on',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
},
'top': {
    'Actor' :
    [
    'slip your leg over the neck of your opponent and attempt a straight armbar on',
    'wrap your leg behind the head of your opponent and engage a triagle choke on',
    'do a kneebar on',
    'lock in a head and arm choke on',
    'do a heel hook on',
    'roll into an anaconda choke on',
    'do a neck crank on',
    'choke',
    'armbar',
    'leglock',
    'toelock',
    'wristlock',
    ],
    'Actee' :
    [
    'slips their leg over your neck and attempts a straight armbar on',
    'wrap their leg behind your headand engages a triagle choke on',
    'does a kneebar on',
    'locks in a head and arm choke on',
    'does a heel hook on',
    'rolls into an anaconda choke on',
    'does a neck crank on',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
    'Observer' :
    [
    'slips their leg over the neck of their opponent and attempts a straight armbar',
    'wraps their leg behind the head of their opponent and engages a triagle choke',
    'does a kneebar on',
    'locks in a head and arm choke on',
    'does a heel hook on',
    'rolls into an anaconda choke on',
    'does a neck crank on',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
},
'in guard': {
    'Actor' :
    [
    'slip your leg over the neck of your opponent and attempt a straight armbar on',
    'wrap your leg behind the head of your opponent and engage a triagle choke on',
    'attempt a guillotine choke on',
    'do a straight ankle lock on',
    'do a kneebar on',
    'perform a painful biceps slicer on',
    'perform a painful calf crusher on',
    'do a heel hook on',
    'do a reverse heel hook on',
    'do a neck crank on',
    'choke',
    'armbar',
    'leglock',
    'toelock',
    'wristlock',
    ],
    'Actee' :
    [
    'slips their leg over the you neck and attempts a straight armbar on',
    'wraps their leg behind your head and engages a triagle choke on',
    'attempts a guillotine choke on',
    'does a straight ankle lock on',
    'does a kneebar on',
    'performs a painful biceps slicer on',
    'performs a painful calf crusher on',
    'does a heel hook on',
    'does a reverse heel hook on',
    'does a neck crank on',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
    'Observer' :
    [
    'slips their leg over the neck of their opponent and attempts a straight armbar on',
    'wraps their leg behind the head of their opponent and engages a triagle choke on',
    'attempts a guillotine choke on',
    'does a straight ankle lock on',
    'does a kneebar on',
    'performs a painful biceps slicer on',
    'performs a painful calf crusher on',
    'does a heel hook on',
    'does a reverse heel hook on',
    'does a neck crank on',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
},
'side controlled': {
    'Actor' :
    [
    'slip your leg over the neck of your opponent and attempt a straight armbar on',
    'wrap your leg behind the head of your opponent and engage a triagle choke on',
    'do a kneebar on',
    'perform a painful calf crusher on',
    'choke',
    'armbar',
    'leglock',
    'toelock',
    'wristlock',
    ],
    'Actee' :
    [
    'slips their leg over the your neck and attempts a straight armbar on',
    'wraps their leg behind the your head and engages a triagle choke on',
    'does a kneebar on you',
    'performs a painful calf crusher on you',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
    'Observer' :
    [
    'slips their leg over the neck of their opponent and attempts a straight armbar on',
    'wraps their leg behind the head of their opponent and engages a triagle choke on',
    'does a kneebar on',
    'performs a painful calf crusher on',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
},
'mounted': {
    'Actor' :
    [
    'do a wrist lock on',
    'choke',
    'armbar',
    'leglock',
    'toelock',
    'wristlock',
    ],
    'Actee' :
    [
    'does a wrist lock on',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
    'Observer' :
    [
    'does a wrist lock on',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
},
'prmounted': {
    'Actor' :
    [
    'do a wrist lock on',
    'choke',
    'armbar',
    'leglock',
    'toelock',
    'wristlock',
    ],
    'Actee' :
    [
    'does a wrist lock on',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
    'Observer' :
    [
    'does a wrist lock on',
    'chokes',
    'armbars',
    'leglocks',
    'toelocks',
    'wristlocks',
    ],
},
'tbstanding' : {
    'Actor' :
    [
    'start locking in a rear naked choke on',
    'do a wrist lock on',
    'choke',
    'armbar',
    'wristlock',
    ],
    'Actee' :
    [
    'moves behind you and starts locking in a rear naked choke on',
    'does a wrist lock on',
    'chokes',
    'armbars',
    'wristlocks',
    ],
    'Observer' :
    [
    'starts locking in a rear naked choke on',
    'does a wrist lock on',
    'chokes',
    'armbars',
    'wristlocks',
    ],
},
'clinching': {
    'Actor' :
    [
    'attempt a guillotine choke on',
    'start locking in a rear naked choke',
    'do a wrist lock on',
    'choke',
    'armbar',
    'wristlock',
    ],
    'Actee' :
    [
    'attempts a guillotine choke on you',
    'moves behind you and starts locking in a rear naked choke on',
    'does a wrist lock on',
    'chokes',
    'armbars',
    'wristlocks',
    ],
    'Observer' :
    [
    'attempts a guillotine choke on',
    'starts locking in a rear naked choke on',
    'does a wrist lock on',
    'chokes',
    'armbars',
    'wristlocks',
    ],
},
'clinched': {
    'Actor' :
    [
    'attempt a guillotine choke on',
    'start locking in a rear naked choke',
    'do a wrist lock on',
    'choke',
    'armbar',
    'wristlock',
    ],
    'Actee' :
    [
    'attempts a guillotine choke on you',
    'moves behind you and starts locking in a rear naked choke on',
    'does a wrist lock on',
    'chokes',
    'armbars',
    'wristlocks',
    ],
    'Observer' :
    [
    'attempts a guillotine choke on',
    'starts locking in a rear naked choke on',
    'does a wrist lock on',
    'chokes',
    'armbars',
    'wristlocks',
    ],
},
'standingbt': {
    'Actor' :
    [
    'do a wrist lock on',
    'choke',
    'armbar',
    'wristlock',
    ],
    'Actee' :
    [
    'does a wrist lock on',
    'chokes',
    'armbars',
    'wristlocks',
    ],
    'Observer' :
    [
    'does a wrist lock on',
    'chokes',
    'armbars',
    'wristlocks',
    ],
},
}

grappling_escape_dict = {
    'default' : {
        'Actor' :
        [
        'slip away from close range combat and stand to your feet'
        ],
        'Actee' :
        [
        'slips away from close range combat and stands to their feet'
        ],
        'Observer' : [
        'slips away from close range combat and stands to their feet'
        ],
    },
    'success' : {
        'Actor' :
        [
        'slip away from close range combat and stand to your feet'
        ],
        'Actee' :
        [
        'slips away from close range combat and stands to their feet'
        ],
        'Observer' : [
        'slips away from close range combat and stands to their feet'
        ],
    },
    'fail' : {
        'Actor' :
        [
        'try to escape close combat and get to your feet, but fail'
        ],
        'Actee' :
        [
        'tries to escape close combat and get to their feet, but fails'
        ],
        'Observer' : [
        'tries to escape close combat and get to their feet, but fails'
        ],
    },
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
    # TODO: Add logic for higher talent levels
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


def return_grappling_takedown_text(pcs_and_npcs_in_room, success_lvl):
    """
    This function returns a random choice from the dict of textual descriptions
    of a takedown attempt.
    """
    log_file("Start of return takedown text func", \
             filename='combat_step.log')
    index = random.randrange(len(takedown_dict['Actor'][success_lvl]))
    final_text_dict = {}
    final_text_dict['Actor'] = takedown_dict['Actor'][success_lvl][index]
    final_text_dict['Actee'] = takedown_dict['Actee'][success_lvl][index]
    final_text_dict['Observer'] = takedown_dict['Observer'][success_lvl][index]
    log_file(f"text_dict: {final_text_dict}", filename='combat_step.log')
    return final_text_dict


def return_grappling_position_text(pcs_and_npcs_in_room):
    """
    This function returns a random choice from the dict of textual descriptions
    of an attacker trying to improve their grappling position.
    """
    log_file("Start of return grappling change position text func", \
             filename='combat_step.log')
    index = random.randrange(len(grappling_change_position_dict['Actor']))
    log_file(f"index: {index}", filename='combat_step.log')
    attacker = pcs_and_npcs_in_room['Actor']
    defender = pcs_and_npcs_in_room['Actee']
    final_text_dict = {}
    final_text_dict['Actor'] = grappling_change_position_dict['Actor'][index]
    final_text_dict['Actee'] = grappling_change_position_dict['Actee'][index]
    final_text_dict['Observer'] = grappling_change_position_dict['Observer'][index]
    log_file(f"text_dict: {final_text_dict}", filename='combat_step.log')
    return final_text_dict


def return_grappling_unarmed_damage_normal_text(pcs_and_npcs_in_room, damage):
    """
    This function returns a random choice from the dict of textual descriptions
    for grappling unarmed combat strikes w/o any natural weapon mutations.
    """
    log_file("Start of return grappling unarmed damage normal text func", \
             filename='combat_step.log')
    attacker = pcs_and_npcs_in_room['Actor']
    defender = pcs_and_npcs_in_room['Actee']
    hit_loc = return_hit_location()
    damage_text = return_damage_gradient_text(damage/defender.traits.hp.current * 100)
    log_file(f"attacker: {attacker.name} defender: {defender.name} hit loc: {hit_loc} damage: {damage_text}", \
             filename='combat_step.log')
    index = random.randrange(len(grappling_unarmed_strikes_normal['Actor']))
    final_text_dict = {}
    final_text_dict['Actor'] = grappling_unarmed_strikes_normal['Actor'][index]
    final_text_dict['Actee'] = grappling_unarmed_strikes_normal['Actee'][index]
    final_text_dict['Observer'] = grappling_unarmed_strikes_normal['Observer'][index]
    log_file(f"text_dict: {final_text_dict}", filename='combat_step.log')
    return final_text_dict, hit_loc, damage_text


def return_grappling_submission_text(pcs_and_npcs_in_room, damage, success):
    """
    This function returns a random choice from the dict of textual descriptions
    for grappling submissions.
    """
    log_file("Start of return grappling submission text func", \
             filename='combat_step.log')
    attacker = pcs_and_npcs_in_room['Actor']
    defender = pcs_and_npcs_in_room['Actee']
    damage_text = return_damage_gradient_text((damage * .75)/defender.traits.sp.current * 100)
    index = random.randrange(len(grappling_submission_dict[attacker.db.info['Position']]['Actor']))
    final_text_dict = {}
    final_text_dict['Actor'] = grappling_submission_dict[attacker.db.info['Position']]['Actor'][index]
    final_text_dict['Actee'] = grappling_submission_dict[attacker.db.info['Position']]['Actee'][index]
    final_text_dict['Observer'] = grappling_submission_dict[attacker.db.info['Position']]['Observer'][index]
    log_file(f"text_dict: {final_text_dict}", filename='combat_step.log')
    return final_text_dict, damage_text


def return_grappling_escape_text(pcs_and_npcs_in_room, success):
    """
    This function returns a text string describing an attempt to escape from
    being grappled.
    """
    log_file("Start of return grappling escape text func", \
             filename='combat_step.log')
    attacker = pcs_and_npcs_in_room['Actor']
    defender = pcs_and_npcs_in_room['Actee']
    index = random.randrange(len(grappling_escape_dict[success]['Actor']))
    final_text_dict = {}
    final_text_dict['Actor'] = grappling_escape_dict[success]['Actor'][index]
    final_text_dict['Actee'] = grappling_escape_dict[success]['Actee'][index]
    final_text_dict['Observer'] = grappling_escape_dict[success]['Observer'][index]
    log_file(f"text_dict: {final_text_dict}", filename='combat_step.log')
    return final_text_dict
