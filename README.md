# Project Setup & Run Instructions

## Overview
This project is intended to process tap dance class plans and standardize their structure. Then, this domain-specific data can be used to fine-tune a pretrained transformer model in order to teach the model how to generate sequence completions.

This pipeline processes raw tap dance sequence data, structures it into a tokenized format, and performs data augmentation for training a sequence model. The included notebook was adapted from the Unsloth framework and performs training and evaluation on the curated data.

*Raw and intermediate data folders are excluded from the repository to avoid clutter and maintain a clean, reproducible dataset pipeline. Only processed, analysis-ready data are included. See raw_data_sample.txt for a sense of the quality of this data.*

---

## Pipeline Steps

*If reproducing, skip steps 1-3. Full raw data files are not included; instead, use the provided JSONL files with the Unsloth notebook in step 4.*

### 1. Raw Data Processing
Run:
```
python src/process_raw_data.py
```

- Input: a folder of text files, completely unprocessed
- Output: a minimally-cleaned folder of text files after expanding abbreviations, standardizing file names, etc.


---

### 2. Data Structuring
Run:
```
python src/structure_data.py
```

- This is the script that handles user input to process the text files line by line.
- Input: the output directory from `process_raw_data`
- Output: a cleaned/filtered dataset of 106 valid examples


---

### 3. Data Augmentation
Run:
```
python src/augment_data.py
```

- Input: the structured dataset
- Output: an expanded dataset with augmented sequences
- Note: this uses `step_replacements` internally (do not run this script separately)


---

### 4. SFT with LoRA 
Run:
```
unsloth.ipynb
```

- Input: both the training and validation JSONL files generated during augmentation
- Output: a trained model, loss plots, evaluation metrics, and an opportunity to experiment with unseen data
- This can be run on the original smaller datasets, or on the larger datasets (`training_aug.jsonl` and `val_aug.jsonl`)
