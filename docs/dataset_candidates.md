# Dataset Candidate Analysis

## Candidate 1: MRL Eye Dataset
The MRL Eye Dataset is a large-scale dataset of human eye images designed for computer vision tasks such as eye detection and blink detection. The original dataset includes 84,898 images captured under various conditions.


### Available information
- Number of images: 84,898
- Number of subjects: 37
- Original labels: open/closed eye state, subject ID, glasses, reflections, lighting conditions, and sensor ID
- Existing split: to be verified
- Planned split: subject-independent if subject metadata is available
- Sensors: Multiple acquisition sensors; exact sensor models and image modalities to be verified from the original dataset documentation.
- Lighting variation: various lighting conditions
- License or usage conditions: License and redistribution conditions: to be verified from the original dataset source before including data, sample images, or derived files in the public repository.

### Advantages
The annotations include subject ID, eye state, glasses, reflections, lighting conditions, and sensor ID. Those attributes make it possible to investigate subject leakage and performance under specific visual conditions. The images include varying lighting conditions and multiple sensors

### Risks
The dataset may contain temporally adjacent frames from the same recording. Even with subject-independent splitting, near-duplicate frames could inflate the apparent dataset size and reduce sample diversity.

### Questions to investigate
- What are the official license and redistribution conditions?
- Are the original eye-state labels open/closed or awake/sleepy?
- How is the subject ID encoded in each filename?
- How many images are available per subject?
- How many open and closed images are available per subject?
- Are left-eye and right-eye images identified?
- Are multiple frames extracted from the same recording?
- Could near-identical consecutive frames cause leakage?
- What sensors and image modalities were used?
- Are the images grayscale, infrared, RGB, or a mixture?
- How large are the original images?
- Are the existing train/validation/test splits subject-independent?
- Are glasses, reflections, lighting, and sensor labels complete?
- Can dataset images or only download instructions be included publicly?
---

## Candidate 2: Large Open/Closed Eyes Dataset
Quite large dataset of open vs closed eyes. Eyes are cropped to contain eyebrows at the top and a little bit of margin on other directions.

### Available information
- Number of images: 174,756
- Class distribution: 133,103 open and 41,653 closed
- Image dimensions: 90 × 90 pixels with three channels
- Existing splits: train (139,804), validation (27,960), and test (6,990)
- Original data sources: Reportedly aggregated from open-source eye datasets; exact provenance must be verified

### Advantages
- Substantially larger number of images
- Ready-made train, validation, and test directories
- Standardized 90 × 90 image dimensions
- Potentially useful as a secondary dataset for robustness testing
- Large sample count may support model-development experiments if leakage and provenance concerns can be resolved

### Risks
The strong class imbalance may bias the model toward predicting the open-eye class unless it is addressed during splitting, training, or evaluation.

### Questions to investigate
- What are the original source datasets?
- Are subject identifiers preserved?
- Can the same subject occur across training, validation, and test sets?
- Were near-duplicate images removed?
- Are consecutive video frames included?
- How reliable are the open/closed labels?
- Why is the class distribution strongly imbalanced?
- Are the provided splits reproducible?
- Does the Apache 2.0 license apply to every source image?
- Are RGB channels genuine color information or repeated grayscale channels?
- Are glasses, reflections, lighting, and sensor conditions available?
---

## Preliminary decision
The MRL Eye Dataset is currently the preferred candidate because its subject identifiers and condition annotations may support subject-independent evaluation and detailed failure analysis. However, the final selection depends on verifying the original license, label definitions, filename/metadata structure, and whether a leakage-safe split can be constructed. The larger open/closed-eye dataset remains a secondary candidate, but its shuffled splits and unclear subject provenance create a higher risk of identity or near-duplicate leakage.