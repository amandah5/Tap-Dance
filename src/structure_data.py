import os
import json
import random



# global
RAW_DIR = "data/intermediate_data"
OUTPUT_FILE = "data/training_data.jsonl"



def ensure_dir(path):
    """Make the folder if it doesn't exist."""
    os.makedirs(path, exist_ok=True)



def normalize_step(name):
    """Replace spaces with underscores in step names."""
    return name.strip().replace(" ", "_")



def format_sequence(sequence):
    """Convert sequence list to a formatted string for training."""
    return " ".join([f"{s['step']}|{s['foot']}|{s['count']}" for s in sequence])



def generate_training_pairs(exercise):
    """Generate a single training entry from an exercise sequence."""
    sequence = exercise["sequence"]
    if len(sequence) < 1:  # need at least 1 step
        return []
    
    sequence_str = format_sequence(sequence)
    entry = {
        "song": exercise["song"],
        "sequence": sequence_str,
        "repeat": exercise["repeat"],
        "travel": exercise["travel"]
    }
    return [entry]  # Return as list for consistency



def step_mode(line, exercise):
    """Walk through this line and build on the current exercise."""
    print("\nSTEP MODE")
    print("LINE:", line) # take the current line from the file
    while True:
        inp = input("step, count, foot (ENTER = done) | u(undo): ").strip() # expected format of user input: 3 items
        if inp == "": # empty input (just pressing enter) ends this line
            break
        elif inp.lower() == "u": # undo the last step added
            if exercise["sequence"]:
                removed = exercise["sequence"].pop()
                print(f"Undone: {removed['step']}|{removed['foot']}|{removed['count']}")
            else:
                print("Nothing to undo!")
            continue
        try:
            step, count, foot = [x.strip() for x in inp.split(",")] # split into these 3 fields
            exercise["sequence"].append({ # turn this input into a dict
                "step": normalize_step(step),
                "count": count,
                "foot": foot
            })
        except ValueError:
            print("Format: step, count, foot") # tell user if input format is incorrect (not 3 comma-separated items)



def save_exercise(exercise, file_name, counter):
    """Write this exercise's training entry to the JSONL file."""
    pairs = generate_training_pairs(exercise)
    
    if not pairs:
        return
    
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair) + "\n")
    print(f"\nSaved 1 training entry from {file_name}")



def process_file(file_path):
    """Process one file at a time, which may contain more than one exercise. Each exercise becomes
    its own training entry in the JSONL file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [l.strip() for l in f if l.strip()]
    file_name = os.path.basename(file_path).replace(".txt", "") # take the base name (no extension)
    exercise_counter = 0
    active_exercise = None # will become an actual exercise
    i = 0 # manual loop counter
    n = len(lines) # max (exclusive) loop iteration
    while i < n:
        line = lines[i]
        print("\n-------------------------------------")
        print(f"LINE {i+1}/{n}: {line}") # display the file line in the console
        print("Active:", bool(active_exercise)) # True if we're within an actual exercise 

        # DEFINE OPTIONS FOR THE USER
        action = input("g(song) | a(add) | s(skip) | e(end) | u(undo) | q(quit): ").strip().lower()

        # SONG
        if action == "g":
            song = input("Song: ").strip()
            if active_exercise is None: # initialize a NEW exercise with this song
                active_exercise = {"song": song, "repeat": None, "travel": None, "sequence": []}
            else: # change the current exercise song
                active_exercise["song"] = song

        # ADD
        elif action == "a":
            if active_exercise is None:
                print("Uh oh! No active exercise. Set the song first.") # exercise cannot happen in silence.
                continue
            step_mode(line, active_exercise)

        # SKIP (this is the only thing that actually moves forward in the file processing)
        elif action == "s":
            i += 1

        # END (save this exercise's training pairs but don't jump lines, in case of weird formatting)
        elif action == "e":
            if active_exercise is None:
                print("What's there to end? There is no active exercise!") # you can't end something you never started
                continue
            # 2 remaining fields to fill in at the end of the exercise: repeat status, travel status
            repeat = input("Repeat (none/same/reverse): ").strip().lower()
            while repeat not in ["none", "same", "reverse"]:
                repeat = input("Repeat (none/same/reverse): ").strip().lower()
            travel = input("Travel (T/F): ").strip().lower()
            while travel not in ["t", "f", "true", "false"]:
                travel = input("Travel (T/F): ").strip().lower()
            active_exercise["repeat"] = repeat
            active_exercise["travel"] = travel in ["t", "true"]
            save_exercise(active_exercise, file_name, exercise_counter)
            exercise_counter += 1
            active_exercise = None

        # UNDO (remove the last step added to the current exercise)
        elif action == "u":
            if active_exercise and active_exercise["sequence"]:
                removed = active_exercise["sequence"].pop()
                print(f"Undone: {removed['step']}|{removed['foot']}|{removed['count']}")
            else:
                print("Nothing to undo!")

        # QUIT (ready to move on to the next file)
        elif action == "q":
            break

        else:
            print("Sir that is not a valid input")

    print(f"\nFinished file: {file_name}")



def main():
    """Process all raw data files, adding exercises to training_data.jsonl."""
    ensure_dir("data")
    
    files = [f for f in os.listdir(RAW_DIR) if f.endswith(".txt")]
    random.shuffle(files)
    
    print(f"Found {len(files)} file(s) to process")
    
    for fname in files:
        print("\n======================================")
        print("FILE:", fname)
        process_file(os.path.join(RAW_DIR, fname))



if __name__ == "__main__":
    main()