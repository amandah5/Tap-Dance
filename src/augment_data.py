import json
import random

from step_replacements import augment_step_sequence

random.seed(42)



def mirror_sequence(sequence: str) -> str:
    """Switch right and left feet in an exercise."""
    steps = sequence.split(" ")
    out = []
    for step in steps:
        parts = step.split("|")
        if len(parts) != 3:
            out.append(step)
            continue
        foot = parts[1]
        flipped = []
        for c in foot:
            if c == "R":
                flipped.append("L")
            elif c == "L":
                flipped.append("R")
            else:  # N (none) or B (both)
                flipped.append(c)
        parts[1] = "".join(flipped)
        out.append("|".join(parts))
    return " ".join(out)


def shift_count(count_str, shift=4):
    """Shift counts by 4 within an 8-count phrase."""
    final = []
    for character in count_str:
        if character in ["e", "&", "a"]:
            final.append(character)
        else:
            num = int(character)
            new_num = ((num - 1 + shift) % 8) + 1
            final.append(str(new_num))
    return "".join(final)


def shift_sequence(sequence: str) -> str:
    """Apply 4-count shifts to every step in a sequence."""
    steps = sequence.split(" ")
    out = []
    for step in steps:
        parts = step.split("|")
        if len(parts) != 3:
            out.append(step)
            continue
        parts[2] = shift_count(parts[2], shift=4)
        out.append("|".join(parts))
    return " ".join(out)


def load_jsonl(path):
    """Generate a list of lines from a JSON file."""
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def write_jsonl(path, data):
    """Write every element in data to a file."""
    with open(path, "w", encoding="utf-8") as f:
        for obj in data:
            f.write(json.dumps(obj) + "\n")


def augment_dataset(raw_file):
    """Apply mirrored, count-shifted, and expanded/swapped sequences for augmentation."""
    data = load_jsonl(raw_file)
    augmented = []
    seen = set()
    for item in data:
        seq = item["sequence"]  # string
        current = seq.split(" ")  # list of tokens

        # keep the original sequence
        augmented.append(item)

        # add the original sequence, but mirrored (other fields like song stay the same)
        m = item.copy()
        m["sequence"] = mirror_sequence(seq)
        if m["sequence"] not in seen:
            augmented.append(m)
            seen.add(m["sequence"])

        # add the original sequence, but shift counts ahead by 4
        s = item.copy()
        s["sequence"] = shift_sequence(seq)
        if s["sequence"] not in seen:
            augmented.append(s)
            seen.add(s["sequence"])

        # for anywhere from 0 to 6 times, add a mutated version of the original sequence with
        # random steps swapped or expanded into multiple atomic steps, based on a pre-determined
        # dictionary of valid swaps
        k_expansions = random.randint(0, 6)
        for _ in range(k_expansions):
            current = augment_step_sequence(current, p_expand=0.3)
            candidate = " ".join(current)
            if candidate not in seen:
                seen.add(candidate)
                e = item.copy()
                e["sequence"] = candidate
                augmented.append(e)

    return augmented


def split_train_val(data, val_ratio=0.1, seed=42):
    """Randomize the order of the datapoints and split between train and validation sets."""
    random.seed(seed)
    random.shuffle(data)
    val_size = int(len(data) * val_ratio)
    val_data = data[:val_size]
    train_data = data[val_size:]
    return train_data, val_data


def main():
    raw_file = "data/full_raw.jsonl"
    full_aug_file = "data/full_aug.jsonl"
    train_file = "data/training_aug.jsonl"
    val_file = "data/val_aug.jsonl"

    # STEP 1: augment all the original curated examples
    augmented = augment_dataset(raw_file)
    write_jsonl(full_aug_file, augmented)

    # STEP 2: split into training & val files
    train, val = split_train_val(augmented, val_ratio=0.1)

    write_jsonl(train_file, train)
    write_jsonl(val_file, val)

    print(f"Total augmented: {len(augmented)}")
    print(f"Train: {len(train)}")
    print(f"Val: {len(val)}")


if __name__ == "__main__":
    main()
