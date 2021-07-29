"""

Action Check

This file will contain the caclulations and logic for performing a success check
on any and all actions a player or NPC might undertake, such as combat, climbing,
hiding, tracking, taunting, crafting, etc...

Some action checks will be one player/NPC rolling a check and another player/NPC
rolling a check or a series of checks to determine which action "wins". This will
be most common in combat. For example, a player may try to strike an NPC named
Frank with a largfe mace. The player would "roll" for success using their abilities,
knacks, modifiers, etc while Frank would "roll" to defender using theirs. The
highest numerical outcome would be successful.

Other action checks will be "rolled" against a specific success threshold. For
example, a player might need to "roll" a 15 to break open a wooden door.

NOTE: Roll is a bit of a misnomer in this case because we will be using something
      akin to a distribution graph (like a bell curve, but not quite a normal
      distribution) and picking a random number from the distribution. This will
      create random numbers much closer to the mean than a dice toll would,
      except in the case of crits. See note #2 below.

NOTE2: In the case that a roll is more than ~ 2 standard deviation outside the
       norm, it will be considered a critical success or failure. Critical
       successes will cause an additional "roll". Each additional crit will
       provide diminishing returns compared to the previous crit AND a
       subsequent crit will be less likely. A roll more than 2 standard
       deviations below the mean will be a critical failure and the result will
       be halved. Both critical successes and critical failures will give the
       player or NPC a chance for progression (to learn more about an existing
       knack, learn a new knack, or increase an ability score slightly).

"""
# imports
import numpy as np
from world.progression_rules import parse_action_type_expand_progression_dict as patepdrules

## Simple function to return a numerical result for an action check
def return_a_roll(number, object_rolling, skill_used):
    """
    Takes in a number (integer, float, etc)
    and outputs a random number from a normal distribution
    with the skill rating at the mean.

    Generally, scores should be around 100 for human "normal". They'll be
    higher than 100 for exceptionally skilled or talented individuals. For
    example, someone that powerlifts might have a strength score approaching
    200 or 300.

    If the random number is more than 2 standard deviations
    above the mean, it will reroll and add the result to
    the total roll. Each subsequent crit will be harder to achieve and
    have less effect.

    A roll more than 2 std below the mean will get halved.

    Note that both can return True if a critical success(es) is rolled followed
    by a critical failure on the bonus roll. Multiple critical_success rolls
    have no additional effect for progression chances.

    We've had the object rolling (i.e. a player object) passed in so we can
    advance the progression counter for that object if appropriate.
    """
    # define vars we need
    total_roll = 0
    num_of_crits = 1
    while True:
        this_roll = np.random.default_rng().normal(loc=number, scale=number/5.25)
        total_roll += this_roll/num_of_crits
        # list of possible outcomes that aren't a critical success for this roll
        if this_roll <= number * (1.35 + ((num_of_crits - 1) * .0025)):
            # if num_of_crits > 2:
                # print(f"Multiple crits: {num_of_crits-1}")
            # total roll is 1 or less, return 1 (the minimum possible)
            if total_roll < 1:
                # adding items to the progression dict so object can learn later
                patepdrules(object_rolling, skill_used)
                return 1
            # check for over 1, but a critical failure on the "roll"
            elif this_roll < (number * .65):
                patepdrules(object_rolling, skill_used)
                return round((total_roll - this_roll/2), 2)
            # the roll is not a critical_success or critical_failure
            else:
                return round(total_roll, 2)
            # no bonus roll this time, break out of loop
            break
        # critical success
        elif this_roll > number * (1.35 + ((num_of_crits - 1) * .0025)):
            patepdrules(object_rolling, skill_used)
            num_of_crits += 1
        # check for other possibilities we didn't think of
        else:
            print("Something went wrong with our logic.")


def return_a_roll_sans_crits(number):
    """
    Takes in a number (integer, float, etc)
    and outputs a random number from a normal distribution
    with the skill rating at the mean.

    Generally, scores should be around 100 for human "normal". They'll be
    higher than 100 for exceptionally skilled or talented individuals. For
    example, someone that powerlifts might have a strength score approaching
    200 or 300.

    Unlike the function above, however, this function will not reroll "crits",
    so the average number returned should be close to the number passed in.
    Ability scores and item durability are a good use for this function.
    """
    # define vars we need
    total_roll = 0
    # return a simple roll
    return  int(np.random.default_rng().normal(loc=number, scale=number/8.5))
