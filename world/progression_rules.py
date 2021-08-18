"""
This file will contain the rulesets for character and NPC progression...
It will use the moving spotlight heartbeat tick to trigger a check for all
ability_scores, traits, talents, and mutations that can be raised or lowered.
It will also (eventually) have checks for learning new talents or spawning
new mutations.
"""
import random
from evennia.utils.logger import log_file
from world.dice_roller import return_a_roll as roll
from world import talents, mutations

# controller for progression functions
def control_progression_funcs(character):
    """
    Call all of the progression functions as needed, in the right order.
    """
    log_file("calling ability score progression", filename='progression.log')
    check_ability_score_progression(character)
    log_file("calling trait progression", filename='progression.log')
    check_trait_progression(character)
    log_file("calling talent progression", filename='progression.log')
    check_talent_progression(character)


# progress ability scores
def check_ability_score_progression(character):
    """
    Check if an ability score can be progressed. If it can, roll the appropriate
    check to determine if it is progressed, then reset the learn counter on that
    ability score.
    """
    ability_scores = [character.ability_scores.Dex, character.ability_scores.Str, \
                      character.ability_scores.Vit, character.ability_scores.Per, \
                      character.ability_scores.Cha]
    for ability_score in ability_scores:
        log_file(f"Checking progression for {character.name} - {ability_score.name}", \
                 filename='progression.log')
        if ability_score.learn >= ability_score.actual:
            # we have a chance to learn something
            # set the threshold for gaining points and make it harder as the
            # score gets higher
            progression_threshold = (ability_score.actual) ** 1.18
            progression_roll = round(roll(ability_score.actual, 'flat'))
            log_file(f"Roll: {progression_roll} Threshold: {progression_threshold}", \
                     filename='progression.log')
            if progression_roll >= progression_threshold:
                log_file(f"{character.name} learned {ability_score.name}", \
                         filename='progression.log')
                ability_score.mod += 1
                character.msg(f"|GYou've learned something about |h{ability_score.name}|n.")
                # reset the learn counter
                ability_score.learn = 0
                # check if we mutated
                check_mutation_progression(character, ability_score)


# progress traits
def check_trait_progression(character):
    """
    Check if a trait can be progressed. If it can, roll the appropriate
    check to determine if it is progressed, then reset the learn counter on that
    trait.
    """
    progressable_traits = [character.traits.hp, character.traits.sp, \
                           character.traits.cp,]
    for trait in progressable_traits:
        log_file(f"Checking progression for {character.name} - {trait.name}", \
                 filename='progression.log')
        if trait.learn >= trait.actual:
            # we have a chance to learn something
            # set the threshold for gaining points and make it harder as the
            # score gets higher
            progression_threshold = (trait.actual) ** 1.1
            progression_roll = round(roll(trait.actual, 'flat'))
            log_file(f"Roll: {progression_roll} Threshold: {progression_threshold}", \
                     filename='progression.log')
            if progression_roll >= progression_threshold:
                trait.mod += 1
                character.msg(f"|GYou've learned something about |h{trait.name}|n.")
                # reset the learn counter
                trait.learn = 0


# progress talents
def check_talent_progression(character):
    """
    Check if a talent can be progressed or changed. If it can, roll the
    appropriate check to determine if it is progressed, then reset the learn
    counter on that mutation.
    """
    ALL_TALENTS = (
        character.talents.footwork, character.talents.melee_weapons, \
        character.talents.ranged_weapons, character.talents.unarmed_striking, \
        character.talents.sneak, character.talents.grappling, character.talents.fly, \
        character.talents.climbing, character.talents.swimming, \
        character.talents.appraise, character.talents.tracking, \
        character.talents.lockpicking, character.talents.sense_danger, \
        character.talents.first_aid, character.talents.blacksmithing, \
        character.talents.leatherworking, character.talents.woodworking, \
        character.talents.tailoring, character.talents.alchemy, \
        character.talents.alter_appearance, character.talents.light_attack, \
        character.talents.invisibility, character.talents.echo_location, \
        character.talents.sonic_attack, character.talents.husbandry, \
        character.talents.barter, character.talents.leadership, \
        character.talents.telekensis, character.talents.pyrokensis, \
        character.talents.atomic_phasing, character.talents.ethereal_body, \
        character.talents.mental_domination
    )
    for talent in ALL_TALENTS:
        log_file(f"Checking progression for {character.name} - {talent.name}", \
                 filename='progression.log')
        if talent.learn >= talent.actual:
            # we have a chance to learn something
            # set the threshold for gaining points and make it harder as the
            # score gets higher
            progression_threshold = (talent.actual) ** 1.15
            progression_roll = round(roll(talent.actual, 'flat'))
            log_file(f"Roll: {progression_roll} Threshold: {progression_threshold}", \
                     filename='progression.log')
            if progression_roll >= progression_threshold:
                talent.mod += 1
                character.msg(f"|GYou've learned something about |h{talent.name}|n.")
                # reset the learn counter
                talent.learn = 0


# progress mutations
def check_mutation_progression(character, ability_score):
    """
    Check if a mutation can be progressed or changed. If it can, roll the
    appropriate check to determine if it is progressed, then reset the learn
    counter on that mutation.
    """
    ALL_MUTATIONS = (character.mutations.extreme_flexibility,
                  character.mutations.rubber_body,
                  character.mutations.improved_balance,
                  character.mutations.bone_density,
                  character.mutations.increased_regeneration,
                  character.mutations.regrow_limbs,
                  character.mutations.extra_limbs,
                  character.mutations.wings, character.mutations.tail,
                  character.mutations.armored_hide,
                  character.mutations.bladed_body,
                  character.mutations.sharp_claws,
                  character.mutations.limb_length,
                  character.mutations.gut_biome,
                  character.mutations.poison_bite,
                  character.mutations.poison_spit,
                  character.mutations.sticky_spit,
                  character.mutations.gills, character.mutations.webbed_feet,
                  character.mutations.slow_aging,
                  character.mutations.enhanced_reactions,
                  character.mutations.visual_sensitivity,
                  character.mutations.sonic_sensitivity,
    	          character.mutations.tactile_sensitivity,
                  character.mutations.olefactory_sensitivity,
                  character.mutations.magnetic_sensitivity,
                  character.mutations.chromatic_flesh,
                  character.mutations.extrasensory_perception,
                  character.mutations.psychokinesis,
                  character.mutations.psychoprojection,
                  character.mutations.malleable_flesh)
    mutations_that_can_go_down = ['Bone Density', 'Limb Length']
    for mutation in character.mutations:
        # filter out mutations character doesn't have yet
        if mutation.actual > 0:
            # cross check and see what ability score
            ability_score_name = mutations.get_ability_score_base_for_mutation(mutation.name)
            if ability_score_name == ability_score.name:
                # now that we've filtered out the non-zero mutations and the
                # mutations not of thios ability score type, we can check if
                # the learn counter is high enough to progress this mutation
                if mutation.learn >= mutation.actual:
                    # we have a chance to learn something
                    # set the threshold for gaining points and make it harder as the
                    # score gets higher
                    progression_threshold = (mutation.actual) ** 1.2
                    progression_roll = round(roll(mutation.actual, 'flat'))
                    log_file(f"Roll: {progression_roll} Threshold: {progression_threshold}", \
                             filename='progression.log')
                    if progression_roll >= progression_threshold:
                        if mutation.name not in mutations_that_can_go_down:
                            mutation.mod += 1
                            character.msg(f"|GYou've mutated! |h{mutation.name}|n. has progressed.")
                        else:
                            delta = random.randrange(-2, 2)
                            mutation.mod += delta
                            if delta > 0:
                                character.msg(f"|GYou've mutated! |h{mutation.name}|n. has progressed.")
                            elif delta > 0:
                                character.msg(f"|GYou've mutated! |h{mutation.name}|n. has regressed.")
                        change_character_description_for_progression(character, mutation)
                        # reset the learn counter
                        mutation.learn = 0


# learn new talents
def check_talent_acquisition(character, talent):
    """
    Check if a talent can be learned for the first time. If it can, roll the
    appropriate check to determine if it is progressed, then reset the learn
    counter on that mutation.
    """
    pass


# acquire new mutations
def check_mutation_acquisition(character, mutation):
    """
    Check if a mutation can be learned for the first time. If it can, roll the
    appropriate check to determine if it is progressed, then reset the learn
    counter on that mutation.
    """
    pass


# change character description from progression
def change_character_description_for_progression(character, mutation):
    """
    Some progression changes will affect the physical description of a
    character or NPC. In particular, mutations often are expressed as a
    change in morphology. For example, a character that gains sharp claws
    or extra limbs would look different than a character without those
    mutations.
    """
    pass
