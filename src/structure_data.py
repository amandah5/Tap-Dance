'''
import os
import json

RAW_DIR = "data/intermediate_data"
PROCESSED_DIR = "data/processed_data"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def process_file(file_path):
    exercises = []
    current_exercise = None

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    for line in lines:
        print("\n~~~~~~~~~~~~~~~~~~~~\n")
        print("RAW LINE:", line)
        print("Current song:", current_exercise["song"] if current_exercise else None)

        action = input(
            "song | start | add | skip | end | quit: "
        ).strip().lower()

        if action == "quit":
            break

        elif action == "song":
            song = input("Song: ").strip()

            if current_exercise:
                current_exercise["song"] = song
            else:
                current_exercise = {
                    "song": song,
                    "repeat": None,
                    "sequence": []
                }

        elif action == "start":
            if current_exercise is None:
                song = input("Song: ").strip()
                current_exercise = {
                    "song": song,
                    "repeat": None,
                    "sequence": []
                }

        elif action == "skip":
            continue

        elif action == "add":
            if current_exercise is None:
                print("No active exercise. Start one first.")
                continue

            print("Enter steps for this line:")
            while True:
                step_input = input("step, count, foot (blank = done): ").strip()

                if step_input == "":
                    break

                try:
                    step, count, foot = [x.strip() for x in step_input.split(",")]
                    step = step.replace(" ", "_")

                    current_exercise["sequence"].append({
                        "step": step,
                        "count": count,
                        "foot": foot
                    })

                except ValueError:
                    print("Format: step, count, foot")

        elif action == "end":
            if current_exercise is None:
                print("No exercise to end.")
                continue

            repeat = input("Repeat (none/same/reverse): ").strip().lower()
            while repeat not in ["none", "same", "reverse"]:
                repeat = input("Repeat (none/same/reverse): ").strip().lower()

            current_exercise["repeat"] = repeat
            exercises.append(current_exercise)
            current_exercise = None

        else:
            print("Invalid option.")

    base = os.path.basename(file_path).replace(".txt", ".json")
    out_path = os.path.join(PROCESSED_DIR, base)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(exercises, f, indent=2)

    print("Saved:", out_path)


def main():
    ensure_dir(PROCESSED_DIR)

    for fname in os.listdir(RAW_DIR):
        if fname.endswith(".txt"):
            process_file(os.path.join(RAW_DIR, fname))

if __name__ == "__main__":
    main()


import os
import json

RAW_DIR = "data/intermediate_data"
PROCESSED_DIR = "data/processed_data"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def normalize_step(name):
    return name.strip().replace(" ", "_")

def add_steps_for_line(line, current_exercise):
    """
    Nested step-entry mode for ONE raw line.
    You can add multiple steps or exit back to line-level control.
    """
    print("\nEntering step mode for line:")
    print(line)

    while True:
        step_input = input(
            "step, count, foot | OR ENTER to finish this line: "
        ).strip()

        if step_input == "":
            break

        try:
            step, count, foot = [x.strip() for x in step_input.split(",")]
            step = normalize_step(step)

            current_exercise["sequence"].append({
                "step": step,
                "count": count,
                "foot": foot
            })

        except ValueError:
            print("Format error. Use: step, count, foot")

def process_file(file_path):
    exercises = []
    current_exercise = None

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [l.strip() for l in f if l.strip()]

    i = 0
    while i < len(lines):
        line = lines[i]

        print("\n------------------------")
        print(f"LINE {i+1}: {line}")
        print(f"Current song: {current_exercise['song'] if current_exercise else None}")

        action = input(
            "song | add | skip | end | quit: "
        ).strip().lower()

        if action == "quit":
            break

        # ---------------- SONG (no line consumption)
        elif action == "song":
            song = input("Enter song: ").strip()

            if current_exercise is None:
                current_exercise = {
                    "song": song,
                    "repeat": None,
                    "sequence": []
                }
            else:
                current_exercise["song"] = song

            continue  # IMPORTANT: do NOT advance line

        # ---------------- SKIP (consume line)
        elif action == "skip":
            i += 1
            continue

        # ---------------- ADD (consume line + nested step entry)
        elif action == "add":
            if current_exercise is None:
                print("No active exercise. You must set a song first.")
                continue

            add_steps_for_line(line, current_exercise)

            # after finishing this line's step entry, we advance
            i += 1
            continue

        # ---------------- END (finalize but do NOT consume line)
        elif action == "end":
            if current_exercise is None:
                print("No exercise to end.")
                continue

            repeat = input("Repeat (none/same/reverse): ").strip().lower()
            while repeat not in ["none", "same", "reverse"]:
                repeat = input("Repeat (none/same/reverse): ").strip().lower()

            current_exercise["repeat"] = repeat
            exercises.append(current_exercise)

            # reset but DO NOT advance line
            current_exercise = None
            continue

        else:
            print("Invalid option.")
            continue

    # save file
    base = os.path.basename(file_path).replace(".txt", ".json")
    out_path = os.path.join(PROCESSED_DIR, base)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(exercises, f, indent=2)

    print("\nSaved:", out_path)


def main():
    ensure_dir(PROCESSED_DIR)

    for fname in os.listdir(RAW_DIR):
        if fname.endswith(".txt"):
            process_file(os.path.join(RAW_DIR, fname))

if __name__ == "__main__":
    main()


import os
import json

RAW_DIR = "data/intermediate_data"
PROCESSED_DIR = "data/processed_data"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def normalize(name):
    return name.strip().replace(" ", "_")

def add_steps(line, exercise):
    print("\nStep mode for line:")
    print(line)

    while True:
        inp = input("step, count, foot (ENTER = done): ").strip()
        if inp == "":
            break

        try:
            step, count, foot = [x.strip() for x in inp.split(",")]
            exercise["sequence"].append({
                "step": normalize(step),
                "count": count,
                "foot": foot
            })
        except ValueError:
            print("Format: step, count, foot")

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [l.strip() for l in f if l.strip()]

    exercises = []
    current_exercise = None

    i = 0
    while i < len(lines):
        line = lines[i]

        print("\n----------------------")
        print(f"LINE {i+1}/{len(lines)}: {line}")
        print("Active song:", current_exercise["song"] if current_exercise else None)

        action = input(
            "song | add | skip | end | quit: "
        ).strip().lower()

        # ---------------- SONG (no line move)
        if action == "song":
            song = input("Song: ").strip()

            if current_exercise:
                current_exercise["song"] = song
            else:
                current_exercise = {
                    "song": song,
                    "repeat": None,
                    "sequence": []
                }

            continue

        # ---------------- SKIP (moves line)
        elif action == "skip":
            i += 1
            continue

        # ---------------- ADD (consume line into current exercise)
        elif action == "add":
            if current_exercise is None:
                print("No active exercise. Set song first.")
                continue

            add_steps(line, current_exercise)
            i += 1
            continue

        # ---------------- END (finalize exercise ONLY, DO NOT MOVE LINE)
        elif action == "end":
            if current_exercise is None:
                print("No active exercise.")
                continue

            repeat = input("Repeat (none/same/reverse): ").strip().lower()
            while repeat not in ["none", "same", "reverse"]:
                repeat = input("Repeat (none/same/reverse): ").strip().lower()

            current_exercise["repeat"] = repeat
            exercises.append(current_exercise)

            # reset, but DO NOT move line
            current_exercise = None
            continue

        elif action == "quit":
            break

        else:
            print("Invalid option.")

    # save full file AFTER all exercises are done
    base = os.path.basename(file_path).replace(".txt", ".json")
    out_path = os.path.join(PROCESSED_DIR, base)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(exercises, f, indent=2)

    print("\nSaved:", out_path)


def main():
    ensure_dir(PROCESSED_DIR)

    for fname in os.listdir(RAW_DIR):
        if fname.endswith(".txt"):
            print(f"\n=== FILE: {fname} ===")
            process_file(os.path.join(RAW_DIR, fname))

if __name__ == "__main__":
    main()



import os
import json

RAW_DIR = "data/intermediate_data"
PROCESSED_DIR = "data/processed_data"


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def normalize_step(name):
    return name.strip().replace(" ", "_")


def step_mode(line, exercise):
    """
    Nested step-entry mode.
    Stays on same raw line until blank input.
    Does NOT affect file iteration.
    """
    print("\nSTEP MODE")
    print("LINE:", line)

    while True:
        inp = input("step, count, foot (ENTER = done): ").strip()

        if inp == "":
            break

        try:
            step, count, foot = [x.strip() for x in inp.split(",")]
            exercise["sequence"].append({
                "step": normalize_step(step),
                "count": count,
                "foot": foot
            })
        except ValueError:
            print("Format must be: step, count, foot")


def process_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [l.strip() for l in f if l.strip()]

    exercises = []
    active_exercise = None

    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        print("\n-----------------------------")
        print(f"LINE {i+1}/{n}: {line}")
        print("Active exercise:", bool(active_exercise))

        action = input(
            "song | add | skip | end | quit: "
        ).strip().lower()

        # ---------------- SONG (no line consumption)
        if action == "song":
            song = input("Song: ").strip()

            if active_exercise is None:
                active_exercise = {
                    "song": song,
                    "repeat": None,
                    "sequence": []
                }
            else:
                active_exercise["song"] = song

        # ---------------- ADD (attach steps, then stay in same exercise)
        elif action == "add":
            if active_exercise is None:
                print("No active exercise. Set song first.")
                continue

            step_mode(line, active_exercise)

        # ---------------- SKIP (ONLY thing that advances line)
        elif action == "skip":
            i += 1
            continue

        # ---------------- END (finalize exercise, do NOT move line)
        elif action == "end":
            if active_exercise is None:
                print("No active exercise.")
                continue

            repeat = input("Repeat (none/same/reverse): ").strip().lower()
            while repeat not in ["none", "same", "reverse"]:
                repeat = input("Repeat (none/same/reverse): ").strip().lower()

            active_exercise["repeat"] = repeat
            exercises.append(active_exercise)

            active_exercise = None

        # ---------------- QUIT (next file)
        elif action == "quit":
            break

        else:
            print("Invalid option.")

    # save file output
    base = os.path.basename(file_path).replace(".txt", ".json")
    out_path = os.path.join(PROCESSED_DIR, base)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(exercises, f, indent=2)

    print("\nSaved:", out_path)


def main():
    ensure_dir(PROCESSED_DIR)

    for fname in os.listdir(RAW_DIR):
        if fname.endswith(".txt"):
            print("\n=============================")
            print("FILE:", fname)
            process_file(os.path.join(RAW_DIR, fname))


if __name__ == "__main__":
    main()
'''

import os
import json

RAW_DIR = "data/intermediate_data"
PROCESSED_DIR = "data/processed_data"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def normalize_step(name):
    return name.strip().replace(" ", "_")

def step_mode(line, exercise):
    print("\nSTEP MODE")
    print("LINE:", line)

    while True:
        inp = input("step, count, foot (ENTER = done): ").strip()

        if inp == "":
            break

        try:
            step, count, foot = [x.strip() for x in inp.split(",")]
            exercise["sequence"].append({
                "step": normalize_step(step),
                "count": count,
                "foot": foot
            })
        except ValueError:
            print("Format: step, count, foot")

def save_exercise(exercise, file_name, counter):
    out_name = f"{file_name}_ex{counter}.json"
    out_path = os.path.join(PROCESSED_DIR, out_name)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(exercise, f, indent=2)

    print(f"\nSaved: {out_name}")

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [l.strip() for l in f if l.strip()]

    file_name = os.path.basename(file_path).replace(".txt", "")
    exercise_counter = 0
    active_exercise = None

    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        print("\n-----------------------------")
        print(f"LINE {i+1}/{n}: {line}")
        print("Active:", bool(active_exercise))

        action = input("g(song) | a(add) | s(skip) | e(end) | q(quit): ").strip().lower()

        # -------- SONG
        if action == "g":
            song = input("Song: ").strip()

            if active_exercise is None:
                active_exercise = {
                    "song": song,
                    "repeat": None,
                    "sequence": []
                }
            else:
                active_exercise["song"] = song

        # -------- ADD
        elif action == "a":
            if active_exercise is None:
                print("No active exercise. Set song first.")
                continue

            step_mode(line, active_exercise)

        # -------- SKIP (ONLY thing that moves forward)
        elif action == "s":
            i += 1

        # -------- END (SAVE IMMEDIATELY, DO NOT MOVE LINE)
        elif action == "e":
            if active_exercise is None:
                print("No active exercise.")
                continue

            repeat = input("Repeat (none/same/reverse): ").strip().lower()
            while repeat not in ["none", "same", "reverse"]:
                repeat = input("Repeat (none/same/reverse): ").strip().lower()

            active_exercise["repeat"] = repeat

            save_exercise(active_exercise, file_name, exercise_counter)
            exercise_counter += 1

            active_exercise = None

        # -------- QUIT (next file)
        elif action == "q":
            break

        else:
            print("Invalid input")

    print(f"\nFinished file: {file_name}")

def main():
    ensure_dir(PROCESSED_DIR)

    for fname in os.listdir(RAW_DIR):
        if fname.endswith(".txt"):
            print("\n=============================")
            print("FILE:", fname)
            process_file(os.path.join(RAW_DIR, fname))

if __name__ == "__main__":
    main()