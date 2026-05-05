# Project Setup & Run Instructions

## Overview
This project is intended to process tap dance class plans and standardize data structure. Then, I use a pretrained transformer model and Low-Rank Adaptation on this domain-specific language to teach it how to generate sequence completions.

This pipeline processes raw tap dance sequence data, structures it into a tokenized format, and performs data augmentation for training a sequence model. The included notebook was adapted from the Unsloth framework and performs training and evaluation on the curated data.

*Raw and intermediate data folders are excluded from the repository to avoid clutter and maintain a clean, reproducible dataset pipeline. Only processed, analysis-ready data are included. See raw_data_sample.txt for a sense of the quality of this data.*

---

## Pipeline Steps (Run Order)

### 1. Raw Data Processing
Run:
```
process_raw_data
```

- Input: a folder of text files, completely unprocessed
- Output: a minimally-cleaned folder of text files, after expanding some abbreviations and reducing some unnecessary text

---

### 2. Data Structuring
Run:
```
structure_data
```

- Input: the output directory from `process_raw_data`
- Output: a cleaned/filtered dataset of 106 valid examples
    - Note: this script handles user input flow experimentation logic

---

### 3. Data Augmentation
Run:
```
augment_data
```

- Input: the structured dataset
- Output: an expanded dataset with augmented sequences
- Note: this uses `step_replacements` internally (do not run this script separately)

---

### 4. SFT with LoRA 
Run:
```
unsloth
```

- Input: both the training and validation JSONL files generated during augmentation
- Note: this can be run on the original smaller datasets, or on the larger datasets (training_aug.jsonl and val_aug.jsonl)
- Output: a trained model, loss plots, evaluation metrics, and an opportunity to experiment with unseen data

---

## How to Run Full Pipeline

Run in order:

```
process_raw_data
structure_data
augment_data
unsloth
```