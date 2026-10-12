# Dataset Candidate Analysis

## Candidate 1: MRL Eye Dataset
The MRL Eye Dataset is a large-scale dataset of human eye images designed for computer vision tasks such as eye detection and blink detection. The original dataset includes 84,898 images captured under various conditions.


### Available information
- Number of images:  84,898 images
Dataset Structure:
Train: Awake (25,770), Sleepy (25,167)
Validation: Awake (8,591), Sleepy (8,389)
Test: Awake (8,591), Sleepy (8,390)

- Number of subjects:37 subjects
- Classes: Awake, Sleepy 
- Image type: .png
- Additional annotations:  ID, eye state, glasses, reflections, lighting conditions, and sensor ID.
- Sensors: Infrared camera
- Lighting variation: various lighting conditions
- License or usage conditions: MIT

### Advantages
The annotations include subject ID, eye state, glasses, reflections, lighting conditions, and sensor ID. Those attributes make it possible to investigate subject leakage and performance under specific visual conditions. The images include varying lighting conditions and multiple sensors
### Risks
the reported subject distribution is not balanced. 
### Questions to investigate

---

## Candidate 2: Large Open/Closed Eyes Dataset
Quite large dataset of open vs closed eyes. Eyes are cropped to contain eyebrows at the top and a little bit of margin on other directions.

### Available information
- Number of images: 174,756 images
- Class distribution: 133103 open, 41653 closed eyes
- Image dimensions:90x90 with 3 channels.
- Existing splits: train (139804 images), val (27960 images) , test (6990 images)
- License: Apache 2.0
- Original data sources:from open source eye datasets

### Advantages
A larger dataset
### Risks
its published train, validation, and test folders were created after shuffling and stratification, and the search description does not indicate a subject-independent split.
### Questions to investigate

---

## Preliminary decision

The annotations in thz MRL dataset include subject ID, eye state, glasses, reflections, lighting conditions, and sensor ID. Those attributes make it possible to investigate subject leakage and performance under specific visual conditions and which could later support meaningful failure analysis..
For this project, a trustworthy subject-aware evaluation is more valuable than achieving a spectacular accuracy number on a potentially leaky random split.