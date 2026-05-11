import random


def compress_count(count):
    """Compress a 3-character count string into a 2-character one using tap-specific priority rules."""

    # 1 SOUND: keep the same
    if len(count) < 2:
        return count

    # 2 SOUNDS: just take the second char
    if len(count) == 2:
        return count[1]

    # 3 SOUNDS: different rules
    c0, c1, c2 = count[0], count[1], count[2]
    if c0 in ["&", "a"]:
        return c1 + c2
    if c1 == "&" or c1 == "a":
        return c0 + c2
    if (
        c0 not in ["&", "a", "e"]
        and c1 not in ["&", "a", "e"]
        and c2 not in ["&", "a", "e"]
    ):
        return c0 + c2

    # fallback: just keep the stronger two chars, based on priority
    priority = {
        "1": 3,
        "2": 3,
        "3": 3,
        "4": 3,
        "5": 3,
        "6": 3,
        "7": 3,
        "8": 3,
        "&": 2,
        "e": 1,
        "a": 0,
    }
    chars = [c0, c1, c2]

    weakest = min(chars, key=lambda x: priority.get(x, -1))
    chars.remove(weakest)
    return "".join(chars)



def resolve_feet(parent_foot, rule, n):
    """Return a list of the corresponding feet for each step in a composite step's expansion."""
    flip = {"R": "L", "L": "R"}
    if rule == "SAME":
        return [parent_foot[0]] * n
    if rule == "SAME_OPP":
        return [parent_foot[0], flip[parent_foot[0]]]
    if rule == "SAME_OPPSAME":
        return [parent_foot[0], flip[parent_foot[0]] + parent_foot[0]]
    if rule == "FIRST_SECOND":
        return [parent_foot[0], parent_foot[1]]
    if rule == "SAME_SAME_OPPSAME":
        return [parent_foot[0], parent_foot[0], flip[parent_foot[0]] + parent_foot[0]]
    raise ValueError(f"Unknown foot rule: {rule}")


def augment_step_sequence(sequence, p_expand=0.3):
    """
    Take a sequence as a list of tokens like ['step|R|1', 'ball_heel|L|2', ...], and
    return the augmented sequence.
    """
    swaps = {  # structure: original_step: [list of possible replacements]
        "step": ["stamp"],
        "stamp": ["step"],
        "ball_heel": ["heel_toe"],
        "heel_toe": ["ball_heel"],
        "heel": ["toe"],
        "toe": ["heel"],
        "paradiddle": ["4_count_riff"],
        "4_count_riff": ["paradiddle"],
        "brush": ["scuff"],
        "scuff": ["brush"],
        "clunk": ["dig", "stomp"],
        "dig": ["stomp"],
        "stomp": ["clunk"],
        "hop": ["chug"],
        "chug": ["hop"],
        "single_wing": ["single_pullback"],
        "flap_heel": ["ball_heel"],
        "flap": ["step"],
    }
    expansions = {  # structure: original step: [ ([list of expanded atomic steps], rule_for_foot_distribution), (...]
        "paradiddle": [
            (["shuffle", "ball_heel"], "SAME"),
            (["shuffle", "heel_toe"], "SAME"),
        ],
        "pas_de_bourree": [
            (["shuffle", "step"], "SAME"),
            (["shuffle", "stamp"], "SAME"),
        ],  # pas de bourree expansions must ALL be on just the first foot
        "shuffle": [(["heel", "spank"], "SAME")],
        "3_count_riff": [
            (["shuffle", "heel_drop"], "SAME_OPP")
        ],  # shuffle will be same foot as 3 count riff, heel drop must be OPPOSITE foot
        "5_count_riff": [
            (["3_count_riff", "heel_toe"], "SAME"),
            (["3_count_riff", "ball_heel"], "SAME"),
            (["cramp_roll", "step"], "SAME"),
        ],
        "ball_change": [
            (["stamp", "stamp"], "FIRST_SECOND")
        ],  # ball change will be 2 feet, must be decomposed across the stamp stamp
        "7_count_riff": [
            (["3_count_riff", "heel_toe", "ball_change"], "SAME_SAME_OPPSAME"),
            (["5_count_riff", "ball_change"], "SAME_OPPSAME"),
            (["shuffle", "5_count_riff"], "SAME"),
        ],  # ball changes must become OPPOSITE-SAME (encoded as 2 feet)
    }
    step_length = {  # structure: {step_name: number_of_counts/sounds, ...}
        "step": 1,
        "stamp": 1,
        "flap_heel": 3,
        "drawback": 3,
        "jump": 1,
        "ball_heel": 2,
        "heel_toe": 2,
        "paradiddle": 4,
        "pas_de_bourree": 3,
        "single_switch_pullback": 2,
        "single_switch_wing": 3,
        "3_count_riff": 3,
        "4_count_riff": 4,
        "5_count_riff": 5,
        "6_count_riff": 6,
        "7_count_riff": 7,
        "shuffle": 2,
        "scuff": 1,
        "toe": 1,
        "stomp": 1,
        "spank": 1,
        "brush": 1,
        "dig": 1,
        "clunk": 1,
        "cramp_roll": 4,
        "ball_change": 2,
        "heel_drop": 1,
        "toe_drop": 1,
        "hop": 1,
        "chug": 1,
        "single_pullback": 2,
        "single_wing": 3,
        "flap": 2,
        "heel": 1,
        "pullback": 2,
        "double_pullback": 4,
        "wing": 3,
        "clap": 1,
    }
    augmented = []  # keep track of every step token (each one being step|foot|count) in the augmented sequence

    for token in sequence:  # sequence has already been split on spaces
        parts = token.split("|")  # break each individual step into step, foot, count
        if len(parts) != 3:
            augmented.append(token)
            continue  # move on if structure has been corrupted somehow

        step, foot, count = parts

        # EXPANSIONS
        if (
            step in expansions and random.random() < p_expand
        ):  # only run if it has an expansion rule, AND if the randomization triggers
            expansion, foot_rule = random.choice(
                expansions[step]
            )  # expansion becomes a chosen list of atomic steps to break into

            missing = [s for s in expansion if s not in step_length]
            if missing:
                raise ValueError(f"Missing step lengths for: {missing}")

            # get TOTAL expected length of expansion
            total_len = sum(step_length[s] for s in expansion)

            # reject if for some reason the length of the current step and sum of target step lengths don't match
            if len(count) != total_len:
                augmented.append(token)
                continue

            remaining = count  # this becomes a string like "1&2"
            expansion_counts = []

            for step_name in expansion:  # expansion is a list of the steps that this current step is being broken into
                target_len = step_length[
                    step_name
                ]  # find the length of this step in the expansion

                chunk = remaining[
                    :target_len
                ]  # assign each count (char) in "remaining" as a string to this particular chunk
                remaining = remaining[
                    target_len:
                ]  # all remaining counts move on to the next step

                expansion_counts.append(chunk)

            feet = resolve_feet(foot, foot_rule, len(expansion))

            # append the expanded steps, now with their correct counts & feet
            for new_step, new_foot, new_count in zip(
                expansion, feet, expansion_counts
            ):  # zip is 3 lists
                augmented.append(f"{new_step}|{new_foot}|{new_count}")
            continue

        # SWAPS
        if step in swaps and random.random() < 0.75:
            step = random.choice(swaps[step])
        target_len = step_length.get(step, len(count))
        while (
            len(count) > target_len
        ):  # if this step's count is currently MORE than the target we're aiming for:
            count = compress_count(count)
        augmented.append(f"{step}|{foot}|{count}")

    return augmented
