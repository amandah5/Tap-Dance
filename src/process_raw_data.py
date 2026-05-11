import os
import re


def process_class_plans(input_folder, output_folder, mappings):
    """Perform minimal cleaning on raw documents to prepare for the user input annotation pipeline."""

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    sorted_keys = sorted(mappings.keys(), key=len, reverse=True)
    escaped_keys = [re.escape(k) for k in sorted_keys]
    regex_pattern = re.compile(r"\b(" + r"|".join(escaped_keys) + r")\b")

    choreo_counter = 1
    class_counter = 1

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_folder, filename)
            with open(input_path, "r", encoding="utf-8") as infile:
                raw_text = infile.read()
            expanded_text = regex_pattern.sub(
                lambda match: mappings[match.group(0)], raw_text
            )
            lines = expanded_text.split("\n")
            processed_lines = []
            for line in lines:
                stripped = line.lstrip()  # remove leading whitespace
                if stripped.startswith("*"):
                    stripped = stripped[
                        1:
                    ].lstrip()  # remove '*' & any space after (from bulleted lists)
                processed_lines.append(stripped)
            expanded_text = "\n".join(processed_lines)
            if filename.startswith(
                "2026 SEASON"
            ):  # this is how all the choreography file names start
                new_filename = f"choreo_{choreo_counter}.txt"
                choreo_counter += 1
            else:
                new_filename = (
                    f"class_{class_counter}.txt"  # all other files are just class plans
                )
                class_counter += 1
            output_path = os.path.join(output_folder, new_filename)
            with open(output_path, "w", encoding="utf-8") as outfile:
                outfile.write(expanded_text)  # write to intermediate_data


if __name__ == "__main__":
    # common abbreviations I use in plans:
    tap_mappings = {"sh": "shuffle", "bc": "ball change", "fl": "flap"}
    process_class_plans("data/raw_data", "data/intermediate_data", tap_mappings)
