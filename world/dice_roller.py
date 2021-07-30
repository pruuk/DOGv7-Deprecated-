"""
Dice roller is a bit of a misnomer in this case because we are generating
random numbers from a distribution rather than a dice roll so that results will
be crowded closer to the mean, reducing the randomness of normal dice style
random generators for action checks.

There will be two types of dice rollers:
One that returns a value without the posibility of re-rolling because of a crit
and one that allows for crits to tack on additional value, but at a diminishing
return for each subsequent 'critical' roll.

A critical roll will be anything more than two standard deviations outside the
normal for that roller. The function for rolling with crits will need more info
passed in because we are controlling character progression/chances to learn
based upon critcal successes and failures (on the theory that we learn our
trimpuphs and our fuckups). The roller that allows criticals will also have a
few different options for randomness (flattened, normal, and steep). Flattened
distributions will have more variance (be more random in a sense), normal
distributions will look like a bell curve, and steep distributions will have
a smaller deviation from mu.

Critical successes and failures will be stored as extra info on traits/skills/
powers and then cleared when that trait/skill/power 'levels up'. See the
progression handler for more details.
"""
# import
import numpy as np
from evennia import logger

# simpliest check, without criticals
def return_a_roll_sans_crits(number, dist_shape='normal'):
    """
    Takes in a number (integer, float, etc)
    and outputs a random number from a normal distribution
    with the skill rating at the mean.

    Generally, scores should be around 100 for human "normal". They'll be
    higher than 100 for exceptionally skilled or talented individuals. For
    example, someone that powerlifts might have a strength score approaching
    200 or 300.

    Unlike the function below, however, this function will not reroll "crits",
    so the average number returned should be close to the number passed in.
    Ability scores and item durability are a good use for this function.

    A non-normal distribution can be specified, but by default, we'll return
    a random choice from a normal distribution with a mean of the variable
    'number' that was passed in and a standard deviation of 1/10 of the mean.

    dist_shape choices:
        normal
        flat
        very flat
        steep
        very steep

    """
    try:
        if dist_shape =='normal':
            return  int(np.random.default_rng().normal(loc=number, scale=number/10))
        elif dist_shape =='flat':
            return  int(np.random.default_rng().normal(loc=number, scale=number/7.5))
        elif dist_shape =='very flat':
            return  int(np.random.default_rng().normal(loc=number, scale=number/5))
        elif dist_shape =='steep':
            return  int(np.random.default_rng().normal(loc=number, scale=number/15))
        elif dist_shape =='very steep':
            return  int(np.random.default_rng().normal(loc=number, scale=number/20))
    except Exception:
        logger.log_trace("We produced an error with the return_a_roll_sans_crits \
                          function in world.dice_roller. Check your inputs and \
                          make sure the correct vars are passed in.")


def roll(number, dist_shape='normal', *ability_skill_or_powers):
    """
    Returns a semi-random number from a distribution with a mean of the number
    passed in.

    A non-normal distribution can be specified, but by default, we'll return
    a random choice from a normal distribution with a mean of the variable
    'number' that was passed in and a standard deviation of 1/10 of the mean.

    dist_shape choices:
        normal
        flat
        very flat
        steep
        very steep

    Any individual rolls more than 2 deviations above or below the mean will be
    considered to be critical successes(above) or critical failures (below).
    With the idea that we learn best from our failures and triumphs, these will
    increase the learn properties of any skills, powers, or ability scores
    passed in (as **kwargs) for each critical success or failure. Critical
    sucesses will also trigger an additional roll, but each subsequent critical
    suceess will add less and less to the total output "roll".

    When passing in the *args, make sure to format them like this:
        object_rolling.ability_score_key.learn
        object_rolling.skill_key.learn
        object_rolling.power_key.learn

        For example:
            Meirok.ability_scores.Dex.learn

    """
    # define variables we'll need
    total_roll = 0
    num_of_crits = 1
    # determine the scale based upon dist_shape desired
    if dist_shape =='normal':
        scale = number/10
    elif dist_shape =='flat':
        scale = number/7.5
    elif dist_shape =='very flat':
        scale = number/5
    elif dist_shape =='steep':
        scale = number/15
    elif dist_shape =='very steep':
        scale = number/20
    # while loop for rolling until we stop rolling critical successes
    while True:
        this_roll = np.random.default_rng().normal(loc=number, scale=scale)
        total_roll += this_roll/num_of_crits
        # check for rolls that are not critical successes
        if this_roll <= number + (scale * 2):
            # check to make sure the roll is at least 1
            if total_roll < 1:
                # less than 1 is definitely a critical failure
                for ability_skill_or_power in ability_skill_or_powers:
                    learned_something(ability_skill_or_power)
                return 1
            elif this_roll < number - (scale * 2):
                # critical failure, but over 1
                for ability_skill_or_power in ability_skill_or_powers:
                    learned_something(ability_skill_or_power)
                return int(total_roll)
            else:
                return int(total_roll)
            # break out of the look since we're getting no bonus roll from a
            # critical suceess
            break
        # critical sucess
        elif this_roll > (number + scale * 2):
            for ability_skill_or_power in ability_skill_or_powers:
                learned_something(ability_skill_or_power)
            num_of_crits += 1
        else:
            logger.log_trace("We produced an error with the regular roller.")


def learned_something(ability_skill_or_power_learn_attribute):
    """
    Takes in a single ability, skill, or power. Adds one to the learn attribute
    for that ability score, skill, or power. This should only be called after
    a critical success on a roll, a critical failure on a roll, or after the
    completion of certain quests.
    """
    try:
        ability_skill_or_power_learn_attribute += 1
    except Exception:
        logger.log_trace(f"We produced an error trying to increase the learning \
                          value on {ability_skill_or_power_learn_attribute}")
    return
