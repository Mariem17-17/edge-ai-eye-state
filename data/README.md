# Dataset

This project uses the MRL Eye Dataset for open/closed eye-state classification.

The dataset is downloaded locally from its original source.

## Source

- Dataset: MRL Eye Dataset
- Publisher: Media Research Lab, VSB - Technical University of Ostrava
- Official page: https://mrl.cs.vsb.cz/eyedataset.html
- Archive: `mrlEyes_2018_01.zip`

## Dataset summary

The official source reports:

- 84,898 infrared eye images
- 37 subjects
- Open and closed eye-state labels
- Images acquired under different lighting conditions
- Images captured using multiple sensors
- Metadata for glasses and reflections

## Local directory structure

```text
data/
├── raw/        # Original downloaded and extracted files
├── interim/    # Audit outputs and temporary metadata
└── processed/  # Validated metadata and final dataset splits
