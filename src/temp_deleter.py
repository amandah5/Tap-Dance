import os
import glob

processed_dir = "data/processed_data"

files = glob.glob(os.path.join(processed_dir, "*"))
for f in files:
    os.remove(f)

print("All files in this directory have been deleted")